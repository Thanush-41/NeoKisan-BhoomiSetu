import mongoose, { Schema, Document } from 'mongoose';
import { IOrder, IOrderItem, OrderStatus, IAddress } from '../types/index.js';

// Order Item Schema
const orderItemSchema = new Schema({
  productId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Product', 
    required: true 
  },
  quantity: { 
    type: Number, 
    required: true, 
    min: 1 
  },
  price: { 
    type: Number, 
    required: true, 
    min: 0 
  },
  totalPrice: { 
    type: Number, 
    required: true, 
    min: 0 
  },
});

// Address Schema (embedded)
const addressSchema = new Schema<IAddress>({
  street: { type: String, required: true },
  city: { type: String, required: true },
  state: { type: String, required: true },
  pincode: { type: String, required: true },
  landmark: String,
  isDefault: { type: Boolean, default: false },
});

// Order Schema
const orderSchema = new Schema({
  userId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    required: true 
  },
  items: [orderItemSchema],
  totalAmount: { 
    type: Number, 
    required: true, 
    min: 0 
  },
  status: { 
    type: String, 
    enum: ['pending', 'confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered', 'cancelled', 'returned'],
    default: 'pending' 
  },
  deliveryAddress: { 
    type: addressSchema, 
    required: true 
  },
  deliveryPartnerId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'DeliveryPartner' 
  },
  paymentMethod: { 
    type: String, 
    enum: ['cash', 'upi', 'card'], 
    required: true 
  },
  paymentStatus: { 
    type: String, 
    enum: ['pending', 'completed', 'failed'], 
    default: 'pending' 
  },
  deliveredAt: Date,
}, {
  timestamps: true,
});

// Indexes for efficient queries
orderSchema.index({ userId: 1, createdAt: -1 });
orderSchema.index({ status: 1 });
orderSchema.index({ deliveryPartnerId: 1 });
orderSchema.index({ paymentStatus: 1 });
orderSchema.index({ createdAt: -1 });

// Validate order items total
orderSchema.pre('save', function (next) {
  const calculatedTotal = this.items.reduce((sum, item) => sum + item.totalPrice, 0);
  if (Math.abs(calculatedTotal - this.totalAmount) > 0.01) {
    return next(new Error('Total amount does not match sum of item prices'));
  }
  
  // Set delivered date when status changes to delivered
  if (this.status === 'delivered' && !this.deliveredAt) {
    this.deliveredAt = new Date();
  }
  
  next();
});

export const Order = mongoose.model('Order', orderSchema);

export default Order;
