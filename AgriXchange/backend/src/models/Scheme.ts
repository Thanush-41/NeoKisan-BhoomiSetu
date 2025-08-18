import mongoose, { Schema, Document } from 'mongoose';
import { IScheme } from '../types/index.js';

const schemeSchema = new Schema({
  name: { 
    type: String, 
    required: true, 
    trim: true 
  },
  description: { 
    type: String, 
    required: true 
  },
  eligibility: [{ 
    type: String, 
    required: true 
  }],
  benefits: [{ 
    type: String, 
    required: true 
  }],
  applicationProcess: { 
    type: String, 
    required: true 
  },
  documentsRequired: [{ 
    type: String, 
    required: true 
  }],
  lastDate: Date,
  contactInfo: {
    phone: String,
    email: String,
    website: String,
  },
  isActive: { 
    type: Boolean, 
    default: true 
  },
}, {
  timestamps: true,
});

// Indexes for efficient queries
schemeSchema.index({ isActive: 1 });
schemeSchema.index({ lastDate: 1 });
schemeSchema.index({ name: 'text', description: 'text' });

export const Scheme = mongoose.model('Scheme', schemeSchema);

export default Scheme;
