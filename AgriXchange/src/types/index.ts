export type UserRole = 'farmer' | 'trader' | 'user';

export interface User {
  id: string;
  name: string;
  email?: string;
  phone: string;
  role: UserRole;
  profilePhoto?: string;
  address: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Farmer extends User {
  role: 'farmer';
  farmSize?: number;
  cropTypes?: string[];
  verificationStatus: 'pending' | 'verified' | 'rejected';
}

export interface Trader extends User {
  role: 'trader';
  gstin: string;
  licenseNumber: string;
  companyName?: string;
  verificationStatus: 'pending' | 'verified' | 'rejected';
}

export interface RegularUser extends User {
  role: 'user';
  deliveryAddresses: Address[];
}

export interface Address {
  id: string;
  street: string;
  city: string;
  state: string;
  pincode: string;
  landmark?: string;
  isDefault: boolean;
}

export interface ProductRating {
  userId: string;
  value: number;
  comment?: string;
  createdAt: string | Date;
}

export interface Product {
  id: string;
  name: string;
  category: ProductCategory;
  description?: string;
  images: string[];
  farmerId: string;
  farmer: Farmer;
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  ratings?: ProductRating[];
  averageRating?: number;
}

export interface RetailProduct extends Product {
  type: 'retail';
  price: number;
  unit: string; // kg, piece, dozen, etc.
  quantity: number;
  minOrderQuantity: number;
  ratings?: ProductRating[];
  averageRating?: number;
}

export interface WholesaleProduct extends Product {
  type: 'wholesale';
  startingPrice: number;
  quantity: number;
  unit: string;
  qualityCertificate: string; // AGMARK certificate URL
  biddingEndTime: Date;
  biddingStatus: 'active' | 'ended' | 'cancelled';
  ratings?: ProductRating[];
  averageRating?: number;
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

export interface Bid {
  id: string;
  productId: string;
  traderId: string;
  trader: Trader;
  amount: number;
  timestamp: Date;
  isWinning: boolean;
}

export interface BiddingRoom {
  id: string;
  product: WholesaleProduct;
  bids: Bid[];
  currentHighestBid?: Bid;
  participants: Trader[];
  isActive: boolean;
  endTime: Date;
}

export interface Order {
  id: string;
  userId: string;
  user: RegularUser;
  items: OrderItem[];
  totalAmount: number;
  status: OrderStatus;
  deliveryAddress: Address;
  deliveryPartner?: DeliveryPartner;
  paymentMethod: 'cash' | 'upi' | 'card';
  createdAt: Date;
  updatedAt: Date;
  deliveredAt?: Date;
}

export interface OrderItem {
  id: string;
  productId: string;
  product: RetailProduct;
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

export interface DeliveryPartner {
  id: string;
  name: string;
  phone: string;
  vehicleNumber: string;
  rating: number;
  isAvailable: boolean;
}

export interface CartItem {
  productId: string;
  product: RetailProduct;
  quantity: number;
}

export interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  description: string;
  windSpeed: number;
  pressure: number;
  forecast: WeatherForecast[];
}

export interface WeatherForecast {
  date: string;
  temperature: {
    min: number;
    max: number;
  };
  description: string;
  humidity: number;
  rainfall?: number;
}

export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  summary: string;
  imageUrl?: string;
  source: string;
  category: 'farming' | 'weather' | 'market' | 'government' | 'technology';
  publishedAt: Date;
  tags: string[];
}

export interface Scheme {
  id: string;
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

// Form types
export interface LoginForm {
  phone: string;
  password: string;
  role: UserRole;
}

export interface SignupForm {
  name: string;
  phone: string;
  email?: string;
  password: string;
  confirmPassword: string;
  role: UserRole;
  address: string;
  // Farmer specific
  farmSize?: number;
  cropTypes?: string[];
  // Trader specific
  gstin?: string;
  licenseNumber?: string;
  companyName?: string;
}

export interface ProductForm {
  name: string;
  category: ProductCategory;
  description?: string;
  images: File[];
  location: string;
  type: 'retail' | 'wholesale';
  // Retail specific
  price?: number;
  unit?: string;
  quantity?: number;
  minOrderQuantity?: number;
  // Wholesale specific
  startingPrice?: number;
  qualityCertificate?: File;
  biddingDuration?: number; // in hours
}

// Socket event types
export interface SocketEvents {
  'join-bidding-room': (roomId: string) => void;
  'leave-bidding-room': (roomId: string) => void;
  'place-bid': (data: { roomId: string; amount: number }) => void;
  'bid-placed': (bid: Bid) => void;
  'bidding-ended': (data: { roomId: string; winningBid?: Bid }) => void;
  'user-joined': (user: Trader) => void;
  'user-left': (userId: string) => void;
}

// Filter and search types
export interface ProductFilters {
  category?: ProductCategory;
  location?: string;
  priceRange?: {
    min: number;
    max: number;
  };
  quantityRange?: {
    min: number;
    max: number;
  };
  sortBy?: 'price-asc' | 'price-desc' | 'latest' | 'popular';
  searchQuery?: string;
}

export interface BiddingFilters {
  category?: ProductCategory;
  location?: string;
  priceRange?: {
    min: number;
    max: number;
  };
  endingIn?: '1h' | '6h' | '24h' | 'all';
  sortBy?: 'ending-soon' | 'highest-bid' | 'lowest-bid' | 'latest';
}
