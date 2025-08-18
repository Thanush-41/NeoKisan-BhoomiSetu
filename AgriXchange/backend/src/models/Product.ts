import mongoose, { Schema, Document } from 'mongoose';
import { IProduct, IRetailProduct, IWholesaleProduct, ProductCategory } from '../types/index.js';

// Location Schema
const locationSchema = new Schema({
  latitude: { type: Number, required: true },
  longitude: { type: Number, required: true },
  address: { type: String, required: true },
});

// Base Product Schema
const productSchema = new Schema({
  name: { type: String, required: true, trim: true },
  category: { 
    type: String, 
    enum: ['vegetables', 'fruits', 'grains', 'pulses', 'spices', 'herbs', 'dairy', 'other'],
    required: true 
  },
  description: { type: String, trim: true },
  images: [{ type: String, required: true }],
  farmerId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  location: { type: locationSchema, required: true },
  isActive: { type: Boolean, default: true },
  type: { type: String, enum: ['retail', 'wholesale'], required: true },
}, {
  timestamps: true,
  discriminatorKey: 'type',
});

// Indexes for efficient queries
productSchema.index({ category: 1 });
productSchema.index({ farmerId: 1 });
productSchema.index({ type: 1 });
productSchema.index({ isActive: 1 });
productSchema.index({ 'location.address': 'text', name: 'text', description: 'text' });
productSchema.index({ createdAt: -1 });

// Rating Schema
const ratingSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  value: { type: Number, required: true, min: 1, max: 5 },
  comment: { type: String },
  createdAt: { type: Date, default: Date.now },
});

productSchema.add({
  ratings: { type: [ratingSchema], default: [] },
  averageRating: { type: Number, default: 0 },
});

// Base Product Model
export const Product = mongoose.model('Product', productSchema);

// Retail Product Schema
const retailProductSchema = new Schema({
  price: { type: Number, required: true, min: 0 },
  unit: { type: String, required: true }, // kg, piece, dozen, etc.
  quantity: { type: Number, required: true, min: 0 },
});

// Wholesale Product Schema
const wholesaleProductSchema = new Schema({
  startingPrice: { type: Number, required: true, min: 0 },
  quantity: { type: Number, required: true, min: 0 },
  unit: { type: String, required: true },
  qualityCertificate: String, // URL to certificate
  biddingEndTime: { type: Date, required: true },
  biddingStatus: { 
    type: String, 
    enum: ['active', 'ended', 'cancelled'], 
    default: 'active' 
  },
});

// Validate bidding end time is in the future
wholesaleProductSchema.pre('save', function (next) {
  if (this.biddingEndTime && this.biddingEndTime <= new Date()) {
    return next(new Error('Bidding end time must be in the future'));
  }
  next();
});

// Index for bidding queries
wholesaleProductSchema.index({ biddingEndTime: 1 });
wholesaleProductSchema.index({ biddingStatus: 1 });

// Create discriminator models
export const RetailProduct = Product.discriminator('retail', retailProductSchema);
export const WholesaleProduct = Product.discriminator('wholesale', wholesaleProductSchema);

export default { Product, RetailProduct, WholesaleProduct };
