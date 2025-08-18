import { Request, Response } from 'express';
import { Product, RetailProduct, WholesaleProduct, BiddingRoom } from '../models/index.js';
import { AuthenticatedRequest, AuthenticatedRequestWithFiles } from '../types/index.js';
import { 
  successResponse, 
  errorResponse, 
  getPaginationOptions, 
  createPaginatedResponse, 
  getSkipValue 
} from '../utils/index.js';
import mongoose from 'mongoose';
import type { IProductWithRatings } from '../types/index.js';
import { uploadToCloudinary } from '../utils/cloudinary';

export const createProduct = async (req: AuthenticatedRequestWithFiles, res: Response): Promise<void> => {
  try {
    console.log('=== PRODUCT CREATION DEBUG ===');
    console.log('Request body:', req.body);
    console.log('Request files:', req.files);
    console.log('User ID:', req.user?.userId);
    console.log('===============================');
    
    const { type, biddingDuration, location, ...productData } = req.body;
    
    // Parse location if it's a JSON string
    let parsedLocation = location;
    if (typeof location === 'string') {
      try {
        parsedLocation = JSON.parse(location);
      } catch (error) {
        console.log('Location parsing error:', error);
        res.status(400).json(errorResponse('Invalid location format'));
        return;
      }
    }
    
    // Manual validation after parsing
    if (!parsedLocation || typeof parsedLocation !== 'object') {
      res.status(400).json(errorResponse('Location is required'));
      return;
    }
    
    if (!parsedLocation.latitude || !parsedLocation.longitude || !parsedLocation.address) {
      res.status(400).json(errorResponse('Location must include latitude, longitude, and address'));
      return;
    }
    
    // Validate required fields based on type
    if (type === 'retail') {
      if (!productData.price || !productData.unit) {
        res.status(400).json(errorResponse('Price, unit are required for retail products'));
        return;
      }
    } else if (type === 'wholesale') {
      if (!productData.startingPrice || !biddingDuration) {
        res.status(400).json(errorResponse('Starting price and bidding duration are required for wholesale products'));
        return;
      }
    }
    
    // Handle uploaded images
    const uploadedFiles = req.files as Express.Multer.File[];
    const imageUrls: string[] = [];
    if (uploadedFiles && uploadedFiles.length > 0) {
      for (const file of uploadedFiles) {
        try {
          // Upload to Cloudinary
          const result: any = await uploadToCloudinary(file.buffer, 'products');
          imageUrls.push(result.secure_url);
        } catch (err) {
          console.error('Cloudinary upload error:', err);
          res.status(500).json(errorResponse('Image upload failed'));
          return;
        }
      }
    }
    
    // Add farmer ID, location, and images
    productData.farmerId = req.user!.userId;
    productData.location = parsedLocation;
    productData.images = imageUrls;

    console.log('Final product data:', productData);
    console.log('Product type:', type);
    console.log('Bidding duration:', biddingDuration);
    
    let product;
    if (type === 'retail') {
      product = new RetailProduct(productData);
    } else {
      // Calculate bidding end time
      const biddingEndTime = new Date();
      biddingEndTime.setHours(biddingEndTime.getHours() + parseInt(biddingDuration));
      
      product = new WholesaleProduct({
        ...productData,
        biddingEndTime
      });
    }

    await product.save();

    // Create or update bidding room for wholesale products
    if (type === 'wholesale') {
      // Check if a bidding room already exists for this product
      let biddingRoom = await BiddingRoom.findOne({ productId: product._id });
      if (!biddingRoom) {
        biddingRoom = new BiddingRoom({
          productId: product._id,
          endTime: (product as any).biddingEndTime,
          isActive: true
        });
        await biddingRoom.save();
      } else if (!biddingRoom.isActive) {
        // Reactivate and update endTime if needed
        biddingRoom.isActive = true;
        biddingRoom.endTime = (product as any).biddingEndTime;
        await biddingRoom.save();
      }
    }

    await product.populate('farmerId', 'name phone location');

    res.status(201).json(successResponse(product, 'Product created successfully'));

  } catch (error) {
    console.error('Create product error:', error);
    res.status(500).json(errorResponse('Failed to create product'));
  }
};

export const getProducts = async (req: Request, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    // Cast req to AuthenticatedRequest to access user
    const authReq = req as any as AuthenticatedRequest;
    const query: any = { isActive: true };

    // Role-based filtering
    if (authReq.user && authReq.user.role) {
      if (authReq.user.role === 'user') {
        query.type = 'retail';
      } else if (authReq.user.role === 'trader') {
        query.type = 'wholesale';
      }
    } else if (req.query.type) {
      query.type = req.query.type;
    }

    if (req.query.category) {
      query.category = req.query.category;
    }

    if (req.query.search) {
      query.$text = { $search: req.query.search };
    }

    if (req.query.minPrice || req.query.maxPrice) {
      query.price = {};
      if (req.query.minPrice) query.price.$gte = Number(req.query.minPrice);
      if (req.query.maxPrice) query.price.$lte = Number(req.query.maxPrice);
    }

    // Execute query
    const products = await Product.find(query)
      .populate('farmerId', 'name phone address')
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await Product.countDocuments(query);

    const response = createPaginatedResponse(products, total, page, limit);
    res.json(successResponse(response, 'Products retrieved successfully'));

  } catch (error) {
    console.error('Get products error:', error);
    res.status(500).json(errorResponse('Failed to retrieve products'));
  }
};

export const getProduct = async (req: Request, res: Response): Promise<void> => {
  try {
    const product = await Product.findById(req.params.id)
      .populate('farmerId', 'name phone address');

    if (!product) {
      res.status(404).json(errorResponse('Product not found'));
      return;
    }

    res.json(successResponse(product, 'Product retrieved successfully'));

  } catch (error) {
    console.error('Get product error:', error);
    res.status(500).json(errorResponse('Failed to retrieve product'));
  }
};

export const updateProduct = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const product = await Product.findById(req.params.id);
    
    if (!product) {
      res.status(404).json(errorResponse('Product not found'));
      return;
    }

    // Check if user owns the product
    if (product.farmerId.toString() !== req.user!.userId) {
      res.status(403).json(errorResponse('Not authorized to update this product'));
      return;
    }

    // Update product
    Object.assign(product, req.body);
    await product.save();

    await product.populate('farmerId', 'name phone address');

    res.json(successResponse(product, 'Product updated successfully'));

  } catch (error) {
    console.error('Update product error:', error);
    res.status(500).json(errorResponse('Failed to update product'));
  }
};

export const deleteProduct = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const product = await Product.findById(req.params.id);
    
    if (!product) {
      res.status(404).json(errorResponse('Product not found'));
      return;
    }

    // Check if user owns the product
    if (product.farmerId.toString() !== req.user!.userId) {
      res.status(403).json(errorResponse('Not authorized to delete this product'));
      return;
    }

    // Soft delete - deactivate product
    product.isActive = false;
    await product.save();

    res.json(successResponse(null, 'Product deleted successfully'));

  } catch (error) {
    console.error('Delete product error:', error);
    res.status(500).json(errorResponse('Failed to delete product'));
  }
};

export const getMyProducts = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    const query = { 
      farmerId: req.user!.userId,
      isActive: true 
    };

    const products = await Product.find(query)
      .populate('farmerId', 'name phone address')
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await Product.countDocuments(query);

    const response = createPaginatedResponse(products, total, page, limit);
    res.json(successResponse(response, 'My products retrieved successfully'));

  } catch (error) {
    console.error('Get my products error:', error);
    res.status(500).json(errorResponse('Failed to retrieve products'));
  }
};

export const getFarmerProducts = async (req: Request, res: Response): Promise<void> => {
  try {
    const { farmerId } = req.params;
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    const query = { 
      farmerId, 
      isActive: true 
    };

    const products = await Product.find(query)
      .populate('farmerId', 'name phone address')
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await Product.countDocuments(query);

    const response = createPaginatedResponse(products, total, page, limit);
    res.json(successResponse(response, 'Farmer products retrieved successfully'));

  } catch (error) {
    console.error('Get farmer products error:', error);
    res.status(500).json(errorResponse('Failed to retrieve farmer products'));
  }
};

// Add product rating
export const rateProduct = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const productId = req.params.id;
    const userId = req.user!.userId;
    const { value, comment } = req.body;

    if (!value || value < 1 || value > 5) {
      res.status(400).json(errorResponse('Rating value must be between 1 and 5'));
      return;
    }

    const product = await Product.findById(productId);
    if (!product) {
      res.status(404).json(errorResponse('Product not found'));
      return;
    }

    // Remove previous rating by this user if exists
    const productWithRatings = product as unknown as IProductWithRatings;
    productWithRatings.ratings = productWithRatings.ratings.filter((r: any) => r.userId.toString() !== userId);
    // Add new rating
    productWithRatings.ratings.push({ userId, value, comment, createdAt: new Date() });
    // Recalculate average rating
    const avg = productWithRatings.ratings.reduce((sum: number, r: any) => sum + r.value, 0) / productWithRatings.ratings.length;
    productWithRatings.averageRating = Math.round(avg * 10) / 10;
    await product.save();
    res.json(successResponse({ averageRating: productWithRatings.averageRating, ratings: productWithRatings.ratings }, 'Product rated successfully'));
  } catch (error) {
    console.error('Rate product error:', error);
    res.status(500).json(errorResponse('Failed to rate product'));
  }
};
