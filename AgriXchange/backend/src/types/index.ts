import { Request } from 'express';

export type UserRole = 'farmer' | 'trader' | 'user';

export interface IUser {
  _id?: string;
  name: string;
  email?: string;
  phone: string;
  password: string;
  role: UserRole;
  profilePhoto?: string;
  address: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface IFarmer extends IUser {
  role: 'farmer';
  farmSize?: number;
  cropTypes?: string[];
  verificationStatus: 'pending' | 'verified' | 'rejected';
  verificationDocuments?: string[];
}

export interface ITrader extends IUser {
  role: 'trader';
  gstin: string;
  licenseNumber: string;
  companyName?: string;
  verificationStatus: 'pending' | 'verified' | 'rejected';
  verificationDocuments?: string[];
}

export interface IRegularUser extends IUser {
  role: 'user';
  deliveryAddresses: IAddress[];
}

export interface IAddress {
  _id?: string;
  street: string;
  city: string;
  state: string;
  pincode: string;
  landmark?: string;
  isDefault: boolean;
}

export type ProductCategory = 
  | 'vegetables'
  | 'fruits' 
  | 'grains'
  | 'pulses'
  | 'spices'
  | 'herbs'
  | 'dairy'
  | 'other';

export interface IProduct {
  _id?: string;
  name: string;
  category: ProductCategory;
  description?: string;
  images: string[];
  farmerId: string;
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  isActive: boolean;
  type: 'retail' | 'wholesale';
  createdAt: Date;
  updatedAt: Date;
}

export interface IRetailProduct extends IProduct {
  type: 'retail';
  price: number;
  unit: string;
  quantity: number;
  minOrderQuantity: number;
}

export interface IWholesaleProduct extends IProduct {
  type: 'wholesale';
  startingPrice: number;
  quantity: number;
  unit: string;
  qualityCertificate?: string;
  biddingEndTime: Date;
  biddingStatus: 'active' | 'ended' | 'cancelled';
}

export interface IBid {
  _id?: string;
  productId: string;
  traderId: string;
  amount: number;
  timestamp: Date;
  isWinning: boolean;
}

export interface IBiddingRoom {
  _id?: string;
  productId: string;
  bids: IBid[];
  participants: string[]; // trader IDs
  isActive: boolean;
  startTime: Date;
  endTime: Date;
  currentHighestBid?: IBid;
  winningBid?: IBid;
}

export interface IOrder {
  _id?: string;
  userId: string;
  items: IOrderItem[];
  totalAmount: number;
  status: OrderStatus;
  deliveryAddress: IAddress;
  deliveryPartnerId?: string;
  paymentMethod: 'cash' | 'upi' | 'card';
  paymentStatus: 'pending' | 'completed' | 'failed';
  createdAt: Date;
  updatedAt: Date;
  deliveredAt?: Date;
}

export interface IOrderItem {
  productId: string;
  quantity: number;
  price: number;
  totalPrice: number;
}

export type OrderStatus = 
  | 'pending'
  | 'confirmed'
  | 'processing'
  | 'shipped'
  | 'out_for_delivery'
  | 'delivered'
  | 'cancelled'
  | 'returned';

export interface IDeliveryPartner {
  _id?: string;
  name: string;
  phone: string;
  vehicleNumber: string;
  rating: number;
  totalDeliveries: number;
  isAvailable: boolean;
  currentLocation?: {
    latitude: number;
    longitude: number;
  };
}

export interface IWeatherData {
  location: string;
  temperature: number;
  humidity: number;
  description: string;
  windSpeed: number;
  pressure: number;
  forecast: IWeatherForecast[];
  updatedAt: Date;
}

export interface IWeatherForecast {
  date: string;
  temperature: {
    min: number;
    max: number;
  };
  description: string;
  humidity: number;
  rainfall?: number;
}

export interface INewsArticle {
  _id?: string;
  title: string;
  content: string;
  summary: string;
  imageUrl?: string;
  source: string;
  category: 'farming' | 'weather' | 'market' | 'government' | 'technology';
  publishedAt: Date;
  tags: string[];
  isActive: boolean;
}

export interface IScheme {
  _id?: string;
  name: string;
  description: string;
  eligibility: string[];
  benefits: string[];
  applicationProcess: string;
  documentsRequired: string[];
  lastDate?: Date;
  contactInfo: {
    phone?: string;
    email?: string;
    website?: string;
  };
  isActive: boolean;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Socket event types
export interface SocketUser {
  userId: string;
  role: UserRole;
  name: string;
}

export interface BidData {
  roomId: string;
  amount: number;
}

export interface SocketEvents {
  'join-bidding-room': (roomId: string) => void;
  'leave-bidding-room': (roomId: string) => void;
  'place-bid': (data: BidData) => void;
  'bid-placed': (bid: IBid & { trader: { name: string; _id: string } }) => void;
  'bidding-ended': (data: { roomId: string; winningBid?: IBid }) => void;
  'user-joined': (user: SocketUser) => void;
  'user-left': (userId: string) => void;
  'error': (message: string) => void;
}

// JWT Payload
export interface JWTPayload {
  userId: string;
  role: UserRole;
  iat?: number;
  exp?: number;
}

// Request with user
export interface AuthenticatedRequest extends Request {
  user?: {
    userId: string;
    role: UserRole;
  };
}

// Request with user and files (for multer)
export interface AuthenticatedRequestWithFiles extends AuthenticatedRequest {
  files?: Express.Multer.File[] | { [fieldname: string]: Express.Multer.File[]; };
}

export interface IProductRating {
  userId: string;
  value: number;
  comment?: string;
  createdAt: Date;
}

// Extend IProduct to include ratings and averageRating
export interface IProductWithRatings extends IProduct {
  ratings: IProductRating[];
  averageRating: number;
}
