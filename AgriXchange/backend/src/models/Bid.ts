import mongoose, { Schema, Document } from 'mongoose';
import { IBid } from '../types/index.js';

const bidSchema = new Schema({
  productId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Product', 
    required: true 
  },
  traderId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    required: true 
  },
  amount: { 
    type: Number, 
    required: true, 
    min: 0 
  },
  timestamp: { 
    type: Date, 
    default: Date.now 
  },
  isWinning: { 
    type: Boolean, 
    default: false 
  },
}, {
  timestamps: true,
});

// Indexes for efficient queries
bidSchema.index({ productId: 1, amount: -1 });
bidSchema.index({ traderId: 1, timestamp: -1 });
bidSchema.index({ productId: 1, timestamp: -1 });
bidSchema.index({ isWinning: 1 });

export const Bid = mongoose.model('Bid', bidSchema);

export default Bid;
