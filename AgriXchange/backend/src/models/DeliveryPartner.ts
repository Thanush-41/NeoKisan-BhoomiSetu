import mongoose, { Schema, Document } from 'mongoose';
import { IDeliveryPartner } from '../types/index.js';

const deliveryPartnerSchema = new Schema({
  name: { 
    type: String, 
    required: true, 
    trim: true 
  },
  phone: { 
    type: String, 
    required: true, 
    unique: true 
  },
  vehicleNumber: { 
    type: String, 
    required: true, 
    unique: true,
    uppercase: true 
  },
  rating: { 
    type: Number, 
    default: 0, 
    min: 0, 
    max: 5 
  },
  totalDeliveries: { 
    type: Number, 
    default: 0, 
    min: 0 
  },
  isAvailable: { 
    type: Boolean, 
    default: true 
  },
  currentLocation: {
    latitude: { type: Number },
    longitude: { type: Number },
  },
}, {
  timestamps: true,
});

// Indexes for efficient queries (phone and vehicleNumber already have unique indexes)
deliveryPartnerSchema.index({ isAvailable: 1 });
deliveryPartnerSchema.index({ rating: -1 });

export const DeliveryPartner = mongoose.model('DeliveryPartner', deliveryPartnerSchema);

export default DeliveryPartner;
