import { Request, Response } from 'express';
import { Order, RetailProduct, DeliveryPartner } from '../models/index.js';
import { AuthenticatedRequest } from '../types/index.js';
import { 
  successResponse, 
  errorResponse, 
  getPaginationOptions, 
  createPaginatedResponse, 
  getSkipValue,
  generateOrderId
} from '../utils/index.js';

export const createOrder = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { items, deliveryAddress, paymentMethod } = req.body;
    
    if (req.user!.role !== 'user') {
      res.status(403).json(errorResponse('Only users can create orders'));
      return;
    }

    // Validate and calculate order details
    let totalAmount = 0;
    const orderItems = [];

    for (const item of items) {
      const product = await RetailProduct.findById(item.productId) as any;
      if (!product || !product.isActive) {
        res.status(400).json(errorResponse(`Product ${item.productId} not found or inactive`));
        return;
      }

      if (item.quantity > product.quantity) {
        res.status(400).json(errorResponse(`Not enough stock for ${product.name}`));
        return;
      }

      const itemTotal = product.price * item.quantity;
      totalAmount += itemTotal;

      orderItems.push({
        productId: item.productId,
        quantity: item.quantity,
        price: product.price,
        totalPrice: itemTotal
      });
    }

    // Create order
    const order = new Order({
      userId: req.user!.userId,
      items: orderItems,
      totalAmount,
      deliveryAddress,
      paymentMethod,
      status: 'pending'
    });

    await order.save();

    // Update product quantities
    for (const item of items) {
      await RetailProduct.findByIdAndUpdate(
        item.productId,
        { $inc: { quantity: -item.quantity } }
      );
    }

    await order.populate([
      { path: 'userId', select: 'name phone' },
      { path: 'items.productId', select: 'name images' }
    ]);

    res.status(201).json(successResponse(order, 'Order created successfully'));

  } catch (error) {
    console.error('Create order error:', error);
    res.status(500).json(errorResponse('Failed to create order'));
  }
};

export const getOrders = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    let query: any = {};
    
    // Users can only see their own orders
    if (req.user!.role === 'user') {
      query.userId = req.user!.userId;
    }

    // Apply filters
    if (req.query.status) {
      query.status = req.query.status;
    }

    if (req.query.fromDate || req.query.toDate) {
      query.createdAt = {};
      if (req.query.fromDate) query.createdAt.$gte = new Date(req.query.fromDate as string);
      if (req.query.toDate) query.createdAt.$lte = new Date(req.query.toDate as string);
    }

    const orders = await Order.find(query)
      .populate('userId', 'name phone')
      .populate('items.productId', 'name images')
      .populate('deliveryPartnerId', 'name phone vehicleNumber')
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await Order.countDocuments(query);

    const response = createPaginatedResponse(orders, total, page, limit);
    res.json(successResponse(response, 'Orders retrieved successfully'));

  } catch (error) {
    console.error('Get orders error:', error);
    res.status(500).json(errorResponse('Failed to retrieve orders'));
  }
};

export const getOrder = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const order = await Order.findById(req.params.orderId)
      .populate('userId', 'name phone')
      .populate('items.productId', 'name images')
      .populate('deliveryPartnerId', 'name phone vehicleNumber');

    if (!order) {
      res.status(404).json(errorResponse('Order not found'));
      return;
    }

    // Users can only see their own orders
    if (req.user!.role === 'user' && order.userId.toString() !== req.user!.userId) {
      res.status(403).json(errorResponse('Access denied'));
      return;
    }

    res.json(successResponse(order, 'Order retrieved successfully'));

  } catch (error) {
    console.error('Get order error:', error);
    res.status(500).json(errorResponse('Failed to retrieve order'));
  }
};

export const updateOrderStatus = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { status, deliveryPartnerId } = req.body;
    const { orderId } = req.params;

    const order = await Order.findById(orderId);
    if (!order) {
      res.status(404).json(errorResponse('Order not found'));
      return;
    }

    // Only admins or delivery partners can update order status
    if (req.user!.role === 'user') {
      // Users can only cancel their own orders
      if (status !== 'cancelled' || order.userId.toString() !== req.user!.userId) {
        res.status(403).json(errorResponse('Access denied'));
        return;
      }
      
      // Can only cancel pending orders
      if (order.status !== 'pending') {
        res.status(400).json(errorResponse('Can only cancel pending orders'));
        return;
      }
    }

    // Update order status
    order.status = status;
    
    if (deliveryPartnerId) {
      order.deliveryPartnerId = deliveryPartnerId;
    }

    await order.save();

    await order.populate([
      { path: 'userId', select: 'name phone' },
      { path: 'items.productId', select: 'name images' },
      { path: 'deliveryPartnerId', select: 'name phone vehicleNumber' }
    ]);

    res.json(successResponse(order, 'Order status updated successfully'));

  } catch (error) {
    console.error('Update order status error:', error);
    res.status(500).json(errorResponse('Failed to update order status'));
  }
};

export const cancelOrder = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { orderId } = req.params;
    
    const order = await Order.findById(orderId);
    if (!order) {
      res.status(404).json(errorResponse('Order not found'));
      return;
    }

    // Users can only cancel their own orders
    if (req.user!.role === 'user' && order.userId.toString() !== req.user!.userId) {
      res.status(403).json(errorResponse('Access denied'));
      return;
    }

    // Can only cancel pending or confirmed orders
    if (!['pending', 'confirmed'].includes(order.status)) {
      res.status(400).json(errorResponse('Cannot cancel order at this stage'));
      return;
    }

    // Update order status
    order.status = 'cancelled';
    await order.save();

    // Restore product quantities
    for (const item of order.items) {
      await RetailProduct.findByIdAndUpdate(
        item.productId,
        { $inc: { quantity: item.quantity } }
      );
    }

    res.json(successResponse(order, 'Order cancelled successfully'));

  } catch (error) {
    console.error('Cancel order error:', error);
    res.status(500).json(errorResponse('Failed to cancel order'));
  }
};

export const getOrderStatistics = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    let matchQuery: any = {};
    
    // Users can only see their own statistics
    if (req.user!.role === 'user') {
      matchQuery.userId = req.user!.userId;
    }

    const stats = await Order.aggregate([
      { $match: matchQuery },
      {
        $group: {
          _id: '$status',
          count: { $sum: 1 },
          totalAmount: { $sum: '$totalAmount' }
        }
      }
    ]);

    const totalOrders = await Order.countDocuments(matchQuery);
    const totalRevenue = await Order.aggregate([
      { $match: { ...matchQuery, status: 'delivered' } },
      { $group: { _id: null, total: { $sum: '$totalAmount' } } }
    ]);

    const response = {
      totalOrders,
      totalRevenue: totalRevenue[0]?.total || 0,
      statusBreakdown: stats
    };

    res.json(successResponse(response, 'Order statistics retrieved successfully'));

  } catch (error) {
    console.error('Get order statistics error:', error);
    res.status(500).json(errorResponse('Failed to retrieve order statistics'));
  }
};
