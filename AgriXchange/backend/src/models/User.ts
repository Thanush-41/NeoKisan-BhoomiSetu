import mongoose, { Schema, Document } from 'mongoose';
import bcrypt from 'bcryptjs';
import { IUser, IFarmer, ITrader, IRegularUser, IAddress, UserRole } from '../types/index.js';

// Address Schema
const addressSchema = new Schema<IAddress>({
  street: { type: String, required: true },
  city: { type: String, required: true },
  state: { type: String, required: true },
  pincode: { type: String, required: true },
  landmark: String,
  isDefault: { type: Boolean, default: false },
});

// Base User Schema
const userSchema = new Schema({
  name: { type: String, required: true, trim: true },
  email: { type: String, unique: true, sparse: true, lowercase: true },
  phone: { type: String, required: true, unique: true },
  password: { type: String, required: true, minlength: 6 },
  role: { type: String, enum: ['farmer', 'trader', 'user'], required: true },
  profilePhoto: String,
  address: { type: String, required: true },
  isActive: { type: Boolean, default: true },
}, {
  timestamps: true,
  discriminatorKey: 'role',
});

// Index for efficient queries (only for non-unique fields)
userSchema.index({ role: 1 });

// Hash password before saving
userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error as Error);
  }
});

// Compare password method
userSchema.methods.comparePassword = async function (candidatePassword: string): Promise<boolean> {
  return bcrypt.compare(candidatePassword, this.password);
};

// Remove password from JSON output
userSchema.methods.toJSON = function () {
  const userObject = this.toObject();
  delete userObject.password;
  return userObject;
};

// Base User Model
export const User = mongoose.model('User', userSchema);

// Farmer Schema
const farmerSchema = new Schema({
  farmSize: { type: Number, min: 0 },
  cropTypes: [{ type: String }],
  verificationStatus: { 
    type: String, 
    enum: ['pending', 'verified', 'rejected'], 
    default: 'pending' 
  },
  verificationDocuments: [String],
});

// Trader Schema
const traderSchema = new Schema({
  gstin: { type: String, required: true, unique: true },
  licenseNumber: { type: String, required: true, unique: true },
  companyName: String,
  verificationStatus: { 
    type: String, 
    enum: ['pending', 'verified', 'rejected'], 
    default: 'pending' 
  },
  verificationDocuments: [String],
});

// Regular User Schema
const regularUserSchema = new Schema({
  deliveryAddresses: [addressSchema],
});

// Create discriminator models
export const Farmer = User.discriminator('farmer', farmerSchema);
export const Trader = User.discriminator('trader', traderSchema);
export const RegularUser = User.discriminator('user', regularUserSchema);

export default { User, Farmer, Trader, RegularUser };
