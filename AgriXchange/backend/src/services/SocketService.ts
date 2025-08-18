import { Server } from 'socket.io';
import { Server as HttpServer } from 'http';
import jwt from 'jsonwebtoken';
import { JWTPayload, SocketUser, BidData } from '../types/index.js';
import { BiddingRoom, Bid, WholesaleProduct, User } from '../models/index.js';
import config from '../config/index.js';

class SocketService {
  private io: Server | null = null;
  private connectedUsers: Map<string, SocketUser> = new Map();
  private roomParticipants: Map<string, Set<string>> = new Map();

  initialize(server: HttpServer) {
    this.io = new Server(server, {
      cors: {
        origin: config.corsOrigin,
        methods: ['GET', 'POST']
      }
    });

    this.io.on('connection', (socket) => {
      console.log('User connected:', socket.id);

      // Authentication
      socket.on('authenticate', async (token: string) => {
        try {
          const decoded = jwt.verify(token, config.jwtSecret) as JWTPayload;
          const user = await User.findById(decoded.userId).select('name role');
          
          if (user) {
            const socketUser: SocketUser = {
              userId: user._id!.toString(),
              role: user.role,
              name: user.name
            };
            
            this.connectedUsers.set(socket.id, socketUser);
            socket.emit('authenticated', socketUser);
          } else {
            socket.emit('authentication_error', 'User not found');
          }
        } catch (error) {
          socket.emit('authentication_error', 'Invalid token');
        }
      });

      // Join bidding room
      socket.on('join-bidding-room', async (roomId: string) => {
        const user = this.connectedUsers.get(socket.id);
        if (!user || user.role !== 'trader') {
          socket.emit('error', 'Only traders can join bidding rooms');
          return;
        }

        try {
          const biddingRoom = await BiddingRoom.findById(roomId)
            .populate('productId')
            .populate('currentHighestBid');

          if (!biddingRoom || !biddingRoom.isActive) {
            socket.emit('error', 'Bidding room not found or inactive');
            return;
          }

          // Add user to room
          socket.join(roomId);
          
          // Add to participants if not already added
          if (!biddingRoom.participants.includes(user.userId as any)) {
            biddingRoom.participants.push(user.userId as any);
            await biddingRoom.save();
          }

          // Track room participants
          if (!this.roomParticipants.has(roomId)) {
            this.roomParticipants.set(roomId, new Set());
          }
          this.roomParticipants.get(roomId)!.add(socket.id);

          // Notify others about new participant
          socket.to(roomId).emit('user-joined', user);

          // Send room data to joined user
          socket.emit('room-joined', {
            room: biddingRoom,
            participants: await this.getRoomParticipants(roomId)
          });

        } catch (error) {
          socket.emit('error', 'Failed to join bidding room');
        }
      });

      // Leave bidding room
      socket.on('leave-bidding-room', (roomId: string) => {
        const user = this.connectedUsers.get(socket.id);
        if (!user) return;

        socket.leave(roomId);
        
        // Remove from room participants
        if (this.roomParticipants.has(roomId)) {
          this.roomParticipants.get(roomId)!.delete(socket.id);
        }

        // Notify others
        socket.to(roomId).emit('user-left', user.userId);
      });

      // Place bid
      socket.on('place-bid', async (data: BidData) => {
        const user = this.connectedUsers.get(socket.id);
        if (!user || user.role !== 'trader') {
          socket.emit('error', 'Only traders can place bids');
          return;
        }

        try {
          const { roomId, amount } = data;
          
          const biddingRoom = await BiddingRoom.findById(roomId)
            .populate('productId')
            .populate('currentHighestBid');

          if (!biddingRoom || !biddingRoom.isActive) {
            socket.emit('error', 'Bidding room not found or inactive');
            return;
          }

          const product = biddingRoom.productId as any;
          
          // Check if bidding has ended
          if (new Date() > biddingRoom.endTime) {
            socket.emit('error', 'Bidding has ended');
            await this.endBidding(roomId);
            return;
          }

          // Validate bid amount
          const currentHighest = biddingRoom.currentHighestBid as any;
          const minimumBid = currentHighest 
            ? currentHighest.amount + config.bidding.minBidIncrement
            : product.startingPrice;

          if (amount < minimumBid) {
            socket.emit('error', `Minimum bid is ₹${minimumBid}`);
            return;
          }

          // Create new bid
          const newBid = new Bid({
            productId: product._id,
            traderId: user.userId,
            amount,
            timestamp: new Date(),
            isWinning: true
          });

          await newBid.save();

          // Update previous winning bid
          if (currentHighest) {
            await Bid.findByIdAndUpdate(currentHighest._id, { isWinning: false });
          }

          // Update bidding room
          biddingRoom.currentHighestBid = newBid._id as any;
          biddingRoom.bids.push(newBid._id as any);
          await biddingRoom.save();

          // Get trader info for broadcast
          const trader = await User.findById(user.userId).select('name');
          
          const bidWithTrader = {
            ...newBid.toObject(),
            trader: {
              _id: user.userId,
              name: trader?.name || 'Unknown'
            }
          };

          // Broadcast to all participants in the room
          this.io!.to(roomId).emit('bid-placed', bidWithTrader);

        } catch (error) {
          console.error('Bid placement error:', error);
          socket.emit('error', 'Failed to place bid');
        }
      });

      // Handle disconnection
      socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        
        const user = this.connectedUsers.get(socket.id);
        if (user) {
          // Remove from all rooms
          this.roomParticipants.forEach((participants, roomId) => {
            if (participants.has(socket.id)) {
              participants.delete(socket.id);
              socket.to(roomId).emit('user-left', user.userId);
            }
          });
        }

        this.connectedUsers.delete(socket.id);
      });
    });
  }

  async endBidding(roomId: string) {
    try {
      const biddingRoom = await BiddingRoom.findById(roomId)
        .populate('currentHighestBid')
        .populate('productId');

      if (!biddingRoom) return;

      // Mark room as inactive
      biddingRoom.isActive = false;
      
      // Set winning bid
      if (biddingRoom.currentHighestBid) {
        biddingRoom.winningBid = biddingRoom.currentHighestBid;
      }

      await biddingRoom.save();

      // Update product status
      await WholesaleProduct.findByIdAndUpdate(
        (biddingRoom.productId as any)._id,
        { biddingStatus: 'ended' }
      );

      // Notify all participants
      this.io?.to(roomId).emit('bidding-ended', {
        roomId,
        winningBid: biddingRoom.winningBid
      });

    } catch (error) {
      console.error('Error ending bidding:', error);
    }
  }

  private async getRoomParticipants(roomId: string): Promise<SocketUser[]> {
    const participants: SocketUser[] = [];
    const socketIds = this.roomParticipants.get(roomId) || new Set();
    
    for (const socketId of socketIds) {
      const user = this.connectedUsers.get(socketId);
      if (user) {
        participants.push(user);
      }
    }
    
    return participants;
  }

  getIO(): Server | null {
    return this.io;
  }

  // Method to manually trigger bidding end (for cron jobs)
  async checkAndEndExpiredBidding() {
    try {
      const expiredRooms = await BiddingRoom.find({
        isActive: true,
        endTime: { $lte: new Date() }
      });

      for (const room of expiredRooms) {
        await this.endBidding(room._id!.toString());
      }
    } catch (error) {
      console.error('Error checking expired bidding:', error);
    }
  }
}

export default new SocketService();
