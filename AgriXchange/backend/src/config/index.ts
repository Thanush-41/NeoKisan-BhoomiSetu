import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const config = {
  port: process.env.PORT || 5000,
  nodeEnv: process.env.NODE_ENV || 'development',
  mongoUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/agrixchange',
  jwtSecret: process.env.JWT_SECRET || 'your-super-secret-jwt-key',
  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  
  // External APIs
  weatherApiKey: process.env.WEATHER_API_KEY || '',
  newsApiKey: process.env.NEWS_API_KEY || '',
  
  // Cloudinary
  cloudinary: {
    cloudName: process.env.CLOUDINARY_CLOUD_NAME || '',
    apiKey: process.env.CLOUDINARY_API_KEY || '',
    apiSecret: process.env.CLOUDINARY_API_SECRET || '',
  },
  
  // JWT
  jwt: {
    expiresIn: '7d',
    refreshExpiresIn: '30d',
  },
  
  // Pagination
  pagination: {
    defaultLimit: 10,
    maxLimit: 100,
  },
  
  // File uploads
  upload: {
    maxFileSize: 5 * 1024 * 1024, // 5MB
    allowedImageTypes: ['image/jpeg', 'image/png', 'image/webp'],
    allowedDocumentTypes: ['application/pdf', 'image/jpeg', 'image/png'],
  },
  
  // Rate limiting
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
  },
  
  // Bidding
  bidding: {
    minBidIncrement: 1, // minimum bid increment in currency
    maxBiddingDuration: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
  },
};

export default config;
