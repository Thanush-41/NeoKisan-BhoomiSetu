import mongoose, { Schema, Document } from 'mongoose';
import { IBiddingRoom, IBid } from '../types/index.js';

const biddingRoomSchema = new Schema({
  productId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Product', 
    required: true,
    unique: true 
  },
  bids: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Bid'
  }],
  participants: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  isActive: { 
    type: Boolean, 
    default: true 
  },
  startTime: { 
    type: Date, 
    default: Date.now 
  },
  endTime: { 
    type: Date, 
    required: true 
  },
  currentHighestBid: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Bid'
  },
  winningBid: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Bid'
  },
}, {
  timestamps: true,
});

// Indexes for efficient queries (productId already has unique index)
biddingRoomSchema.index({ isActive: 1 });
biddingRoomSchema.index({ endTime: 1 });
biddingRoomSchema.index({ participants: 1 });

// Validate end time
biddingRoomSchema.pre('save', function (next) {
  if (this.endTime <= this.startTime) {
    return next(new Error('End time must be after start time'));
  }
  next();
});

export const BiddingRoom = mongoose.model('BiddingRoom', biddingRoomSchema);

export default BiddingRoom;
