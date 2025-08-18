import { Request, Response } from 'express';
import { 
  BiddingRoom, 
  Bid, 
  WholesaleProduct, 
  User 
} from '../models/index.js';
import { AuthenticatedRequest } from '../types/index.js';
import { 
  successResponse, 
  errorResponse, 
  getPaginationOptions, 
  createPaginatedResponse, 
  getSkipValue 
} from '../utils/index.js';
import config from '../config/index.js';

export const getActiveBiddings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    // Build query for active wholesale products
    const query: any = { 
      type: 'wholesale',
      isActive: true,
      biddingStatus: 'active',
      biddingEndTime: { $gt: new Date() }
    };
    
    if (req.query.category) {
      query.category = req.query.category;
    }
    
    if (req.query.location) {
      query['location.address'] = { $regex: req.query.location, $options: 'i' };
    }
    
    if (req.query.minPrice || req.query.maxPrice) {
      query.startingPrice = {};
      if (req.query.minPrice) query.startingPrice.$gte = Number(req.query.minPrice);
      if (req.query.maxPrice) query.startingPrice.$lte = Number(req.query.maxPrice);
    }

    // Apply ending time filter
    if (req.query.endingIn) {
      const now = new Date();
      let endTime: Date | null = new Date();
      
      switch (req.query.endingIn) {
        case '1h':
          endTime.setHours(now.getHours() + 1);
          break;
        case '6h':
          endTime.setHours(now.getHours() + 6);
          break;
        case '24h':
          endTime.setHours(now.getHours() + 24);
          break;
        default:
          endTime = null;
      }
      
      if (endTime) {
        query.biddingEndTime.$lte = endTime;
      }
    }

    // Sort by custom criteria
    let sortCriteria = sort;
    if (req.query.sortBy) {
      switch (req.query.sortBy) {
        case 'ending-soon':
          sortCriteria = 'biddingEndTime';
          break;
        case 'latest':
          sortCriteria = '-createdAt';
          break;
        default:
          sortCriteria = sort;
      }
    }

    const products = await WholesaleProduct.find(query)
      .populate('farmerId', 'name phone address')
      .sort(sortCriteria)
      .skip(skip)
      .limit(limit);

    // Get current highest bids for each product
    const productsWithBids = await Promise.all(
      products.map(async (product) => {
        const biddingRoom = await BiddingRoom.findOne({ productId: product._id })
          .populate({
            path: 'currentHighestBid',
            populate: {
              path: 'traderId',
              select: 'name'
            }
          });

        return {
          ...product.toObject(),
          biddingRoom: biddingRoom ? {
            _id: biddingRoom._id,
            currentHighestBid: biddingRoom.currentHighestBid,
            participantCount: biddingRoom.participants.length
          } : null
        };
      })
    );

    const total = await WholesaleProduct.countDocuments(query);

    const response = createPaginatedResponse(productsWithBids, total, page, limit);
    res.json(successResponse(response, 'Active biddings retrieved successfully'));

  } catch (error) {
    console.error('Get active biddings error:', error);
    res.status(500).json(errorResponse('Failed to retrieve active biddings'));
  }
};

export const getBiddingRoom = async (req: Request, res: Response): Promise<void> => {
  try {
    const biddingRoom = await BiddingRoom.findById(req.params.roomId)
      .populate({
        path: 'productId',
        populate: {
          path: 'farmerId',
          select: 'name phone address'
        }
      })
      .populate({
        path: 'bids',
        populate: {
          path: 'traderId',
          select: 'name'
        },
        options: { sort: { timestamp: -1 } }
      })
      .populate('participants', 'name')
      .populate({
        path: 'currentHighestBid',
        populate: {
          path: 'traderId',
          select: 'name'
        }
      });

    if (!biddingRoom) {
      res.status(404).json(errorResponse('Bidding room not found'));
      return;
    }

    res.json(successResponse(biddingRoom, 'Bidding room retrieved successfully'));

  } catch (error) {
    console.error('Get bidding room error:', error);
    res.status(500).json(errorResponse('Failed to retrieve bidding room'));
  }
};

export const placeBid = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    const { amount } = req.body;
    const traderId = req.user!.userId;

    // Check if user is a trader
    if (req.user!.role !== 'trader') {
      res.status(403).json(errorResponse('Only traders can place bids'));
      return;
    }

    // Find the product and bidding room
    const product = await WholesaleProduct.findById(productId) as any;
    if (!product || !product.isActive || product.biddingStatus !== 'active') {
      res.status(404).json(errorResponse('Product not found or bidding inactive'));
      return;
    }

    // Check if bidding has ended
    if (new Date() > product.biddingEndTime) {
      res.status(400).json(errorResponse('Bidding has ended'));
      return;
    }

    const biddingRoom = await BiddingRoom.findOne({ productId })
      .populate('currentHighestBid');

    if (!biddingRoom || !biddingRoom.isActive) {
      res.status(404).json(errorResponse('Bidding room not found or inactive'));
      return;
    }

    // Validate bid amount
    const currentHighest = biddingRoom.currentHighestBid as any;
    // Always increment by 1
    const minimumBid = currentHighest && currentHighest.amount
      ? currentHighest.amount + 1
      : product.startingPrice;

    if (amount < minimumBid) {
      res.status(400).json(errorResponse(`Minimum bid is ₹${minimumBid}`));
      return;
    }

    // Update previous winning bid BEFORE creating new bid to avoid duplicate key error
    if (currentHighest) {
      await Bid.updateOne({ _id: currentHighest._id }, { $set: { isWinning: false } });
    }

    // Create new bid
    const newBid = new Bid({
      productId,
      traderId,
      amount,
      timestamp: new Date(),
      isWinning: true
    });

    await newBid.save();

    // Update bidding room
    biddingRoom.currentHighestBid = newBid._id as any;
    biddingRoom.bids.push(newBid._id as any);
    
    // Add trader to participants if not already present
    if (!biddingRoom.participants.includes(traderId as any)) {
      biddingRoom.participants.push(traderId as any);
    }

    await biddingRoom.save();

    // Populate the new bid with trader info
    await newBid.populate('traderId', 'name');

    res.status(201).json(successResponse(newBid, 'Bid placed successfully'));

  } catch (error) {
    console.error('Place bid error:', error);
    res.status(500).json(errorResponse('Failed to place bid'));
  }
};

export const getMyBids = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    if (req.user!.role !== 'trader') {
      res.status(403).json(errorResponse('Only traders can view bids'));
      return;
    }

    const bids = await Bid.find({ traderId: req.user!.userId })
      .populate({
        path: 'productId',
        populate: {
          path: 'farmerId',
          select: 'name phone'
        }
      })
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await Bid.countDocuments({ traderId: req.user!.userId });

    const response = createPaginatedResponse(bids, total, page, limit);
    res.json(successResponse(response, 'My bids retrieved successfully'));

  } catch (error) {
    console.error('Get my bids error:', error);
    res.status(500).json(errorResponse('Failed to retrieve bids'));
  }
};

export const getBiddingHistory = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    const { page, limit } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    const bids = await Bid.find({ productId })
      .populate('traderId', 'name _id')
      .sort({ timestamp: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Bid.countDocuments({ productId });

    const response = createPaginatedResponse(bids, total, page, limit);
    res.json(successResponse(response, 'Bidding history retrieved successfully'));

  } catch (error) {
    console.error('Get bidding history error:', error);
    res.status(500).json(errorResponse('Failed to retrieve bidding history'));
  }
};

export const getMyWinningBids = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    if (req.user!.role !== 'trader') {
      res.status(403).json(errorResponse('Only traders can view winning bids'));
      return;
    }

    const winningBids = await Bid.find({ 
      traderId: req.user!.userId,
      isWinning: true
    })
      .populate({
        path: 'productId',
        populate: {
          path: 'farmerId',
          select: 'name phone address'
        }
      })
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await Bid.countDocuments({ 
      traderId: req.user!.userId,
      isWinning: true
    });

    const response = createPaginatedResponse(winningBids, total, page, limit);
    res.json(successResponse(response, 'Winning bids retrieved successfully'));

  } catch (error) {
    console.error('Get winning bids error:', error);
    res.status(500).json(errorResponse('Failed to retrieve winning bids'));
  }
};
