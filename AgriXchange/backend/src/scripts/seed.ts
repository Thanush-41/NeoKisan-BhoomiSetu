import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import config from '../config/index.js';
import { connectDB } from '../config/database.js';
import {
  User,
  Farmer,
  Trader,
  RegularUser,
  RetailProduct,
  WholesaleProduct,
  NewsArticle,
  Scheme,
  DeliveryPartner,
  BiddingRoom
} from '../models/index.js';

const sampleFarmers = [
  {
    name: 'Rajesh Kumar',
    phone: '9876543210',
    password: 'password123',
    role: 'farmer',
    address: 'Village Kharar, Punjab',
    farmSize: 5,
    cropTypes: ['wheat', 'rice', 'vegetables'],
    verificationStatus: 'verified'
  },
  {
    name: 'Sunita Devi',
    phone: '9876543211',
    password: 'password123',
    role: 'farmer',
    address: 'Village Sonipat, Haryana',
    farmSize: 3,
    cropTypes: ['tomatoes', 'onions', 'potatoes'],
    verificationStatus: 'verified'
  },
  {
    name: 'Mohan Singh',
    phone: '9876543212',
    password: 'password123',
    role: 'farmer',
    address: 'Village Nashik, Maharashtra',
    farmSize: 8,
    cropTypes: ['grapes', 'onions', 'sugarcane'],
    verificationStatus: 'verified'
  }
];

const sampleTraders = [
  {
    name: 'Anil Traders',
    phone: '9876543220',
    password: 'password123',
    role: 'trader',
    address: 'Mandi Road, Delhi',
    gstin: '07AABCA1234M1ZV',
    licenseNumber: 'LIC123456',
    companyName: 'Anil Agro Trading',
    verificationStatus: 'verified'
  },
  {
    name: 'Wholesale Fruits Co.',
    phone: '9876543221',
    password: 'password123',
    role: 'trader',
    address: 'APMC Market, Mumbai',
    gstin: '27BBCDA5678N2ZU',
    licenseNumber: 'LIC789012',
    companyName: 'Mumbai Wholesale Fruits',
    verificationStatus: 'verified'
  }
];

const sampleUsers = [
  {
    name: 'Priya Sharma',
    phone: '9876543230',
    password: 'password123',
    role: 'user',
    address: 'Sector 15, Gurgaon',
    deliveryAddresses: [
      {
        street: 'House No. 123, Sector 15',
        city: 'Gurgaon',
        state: 'Haryana',
        pincode: '122001',
        isDefault: true
      }
    ]
  },
  {
    name: 'Amit Patel',
    phone: '9876543231',
    password: 'password123',
    role: 'user',
    address: 'Andheri West, Mumbai',
    deliveryAddresses: [
      {
        street: 'Flat 401, Building A, Andheri West',
        city: 'Mumbai',
        state: 'Maharashtra',
        pincode: '400058',
        isDefault: true
      }
    ]
  }
];

const sampleRetailProducts = [
  {
    name: 'Fresh Tomatoes',
    category: 'vegetables',
    description: 'Farm fresh red tomatoes, organically grown',
    images: ['https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e'],
    location: {
      latitude: 30.7333,
      longitude: 76.7794,
      address: 'Kharar, Punjab'
    },
    type: 'retail',
    price: 40,
    unit: 'kg',
    quantity: 100,
    minOrderQuantity: 2
  },
  {
    name: 'Organic Onions',
    category: 'vegetables',
    description: 'Fresh organic onions, no pesticides used',
    images: ['https://images.unsplash.com/photo-1518977676601-b53f82aba655'],
    location: {
      latitude: 28.9845,
      longitude: 77.0674,
      address: 'Sonipat, Haryana'
    },
    type: 'retail',
    price: 30,
    unit: 'kg',
    quantity: 150,
    minOrderQuantity: 3
  },
  {
    name: 'Premium Basmati Rice',
    category: 'grains',
    description: 'High quality basmati rice, aged for 2 years',
    images: ['https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6'],
    location: {
      latitude: 30.7333,
      longitude: 76.7794,
      address: 'Kharar, Punjab'
    },
    type: 'retail',
    price: 120,
    unit: 'kg',
    quantity: 200,
    minOrderQuantity: 5
  }
];

const sampleWholesaleProducts = [
  {
    name: 'Bulk Potatoes',
    category: 'vegetables',
    description: 'High quality potatoes for wholesale, perfect for retail chains',
    images: ['https://images.unsplash.com/photo-1518977676601-b53f82aba655'],
    location: {
      latitude: 28.9845,
      longitude: 77.0674,
      address: 'Sonipat, Haryana'
    },
    type: 'wholesale',
    startingPrice: 15,
    quantity: 5000,
    unit: 'kg',
    qualityCertificate: 'https://example.com/cert1.pdf',
    biddingEndTime: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
    biddingStatus: 'active'
  },
  {
    name: 'Fresh Grapes Wholesale',
    category: 'fruits',
    description: 'Premium quality grapes for export and wholesale',
    images: ['https://images.unsplash.com/photo-1537640538966-79f369143ef8'],
    location: {
      latitude: 19.9975,
      longitude: 73.7898,
      address: 'Nashik, Maharashtra'
    },
    type: 'wholesale',
    startingPrice: 50,
    quantity: 2000,
    unit: 'kg',
    qualityCertificate: 'https://example.com/cert2.pdf',
    biddingEndTime: new Date(Date.now() + 48 * 60 * 60 * 1000), // 48 hours from now
    biddingStatus: 'active'
  }
];

const sampleNews = [
  {
    title: 'New Government Scheme for Organic Farming Launched',
    content: 'The government has announced a new scheme to promote organic farming with subsidies up to 50% for certified organic farmers...',
    summary: 'Government launches new organic farming scheme with 50% subsidies for certified farmers.',
    imageUrl: 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854',
    source: 'AgriNews India',
    category: 'government',
    publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    tags: ['government', 'organic farming', 'subsidies']
  },
  {
    title: 'Weather Alert: Heavy Rainfall Expected in Northern States',
    content: 'The meteorological department has issued a weather alert for heavy rainfall in Punjab, Haryana, and Uttar Pradesh...',
    summary: 'Weather alert issued for heavy rainfall in northern states this week.',
    imageUrl: 'https://images.unsplash.com/photo-1504608524841-42fe6f032b4b',
    source: 'Weather Bureau',
    category: 'weather',
    publishedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    tags: ['weather', 'rainfall', 'alert']
  },
  {
    title: 'Technology Innovation in Agriculture: Drone Farming',
    content: 'Latest advances in drone technology are revolutionizing farming practices with precision agriculture...',
    summary: 'Drone technology revolutionizing farming with precision agriculture techniques.',
    imageUrl: 'https://images.unsplash.com/photo-1473968512647-3e447244af8f',
    source: 'Tech Agriculture',
    category: 'technology',
    publishedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    tags: ['technology', 'drones', 'precision agriculture']
  }
];

const sampleSchemes = [
  {
    name: 'PM-KISAN Samman Nidhi',
    description: 'Direct income support to farmers providing ₹6000 per year in three equal installments.',
    eligibility: [
      'Small and marginal farmers',
      'Landholding farmers families',
      'Valid Aadhaar card required'
    ],
    benefits: [
      '₹6000 per year direct cash transfer',
      'Three equal installments of ₹2000',
      'Direct bank transfer'
    ],
    applicationProcess: 'Apply online through PM-KISAN portal or visit nearest Common Service Center',
    documentsRequired: [
      'Aadhaar Card',
      'Bank Account Details',
      'Land Records',
      'Identity Proof'
    ],
    contactInfo: {
      phone: '155261',
      email: 'pmkisan-ict@gov.in',
      website: 'https://pmkisan.gov.in'
    }
  },
  {
    name: 'Soil Health Card Scheme',
    description: 'Provides soil health cards to farmers containing crop-wise recommendations of nutrients and fertilizers.',
    eligibility: [
      'All farmers',
      'Land ownership or cultivation rights required'
    ],
    benefits: [
      'Free soil testing',
      'Nutrient recommendations',
      'Fertilizer recommendations',
      'Improved crop yield'
    ],
    applicationProcess: 'Contact nearest Krishi Vigyan Kendra or Agriculture Office',
    documentsRequired: [
      'Identity Proof',
      'Land Records',
      'Contact Details'
    ],
    contactInfo: {
      phone: '1800-180-1551',
      website: 'https://soilhealth.dac.gov.in'
    }
  }
];

const sampleDeliveryPartners = [
  {
    name: 'Ramesh Kumar',
    phone: '9876543250',
    vehicleNumber: 'DL01AB1234',
    rating: 4.5,
    totalDeliveries: 150,
    isAvailable: true,
    currentLocation: {
      latitude: 28.6139,
      longitude: 77.2090
    }
  },
  {
    name: 'Suresh Singh',
    phone: '9876543251',
    vehicleNumber: 'MH02CD5678',
    rating: 4.2,
    totalDeliveries: 120,
    isAvailable: true,
    currentLocation: {
      latitude: 19.0760,
      longitude: 72.8777
    }
  }
];

async function seedDatabase() {
  try {
    console.log('Connecting to database...');
    await connectDB();

    console.log('Clearing existing data...');
    await Promise.all([
      User.deleteMany({}),
      RetailProduct.deleteMany({}),
      WholesaleProduct.deleteMany({}),
      NewsArticle.deleteMany({}),
      Scheme.deleteMany({}),
      DeliveryPartner.deleteMany({}),
      BiddingRoom.deleteMany({})
    ]);

    console.log('Creating users...');
    
    // Create farmers
    const farmers = [];
    for (const farmerData of sampleFarmers) {
      const farmer = new Farmer(farmerData);
      await farmer.save();
      farmers.push(farmer);
    }

    // Create traders
    const traders = [];
    for (const traderData of sampleTraders) {
      const trader = new Trader(traderData);
      await trader.save();
      traders.push(trader);
    }

    // Create regular users
    const users = [];
    for (const userData of sampleUsers) {
      const user = new RegularUser(userData);
      await user.save();
      users.push(user);
    }

    console.log('Creating products...');
    
    // Create retail products
    for (let i = 0; i < sampleRetailProducts.length; i++) {
      const productData = {
        ...sampleRetailProducts[i],
        farmerId: farmers[i % farmers.length]._id
      };
      const product = new RetailProduct(productData);
      await product.save();
    }

    // Create wholesale products and bidding rooms
    for (let i = 0; i < sampleWholesaleProducts.length; i++) {
      const productData = {
        ...sampleWholesaleProducts[i],
        farmerId: farmers[i % farmers.length]._id
      };
      const product = new WholesaleProduct(productData);
      await product.save();

      // Create bidding room
      const biddingRoom = new BiddingRoom({
        productId: product._id,
        endTime: (product as any).biddingEndTime,
        isActive: true
      });
      await biddingRoom.save();
    }

    console.log('Creating news articles...');
    for (const newsData of sampleNews) {
      const article = new NewsArticle(newsData);
      await article.save();
    }

    console.log('Creating schemes...');
    for (const schemeData of sampleSchemes) {
      const scheme = new Scheme(schemeData);
      await scheme.save();
    }

    console.log('Creating delivery partners...');
    for (const partnerData of sampleDeliveryPartners) {
      const partner = new DeliveryPartner(partnerData);
      await partner.save();
    }

    console.log('✅ Database seeded successfully!');
    console.log('\n📊 Sample Data Created:');
    console.log(`👨‍🌾 Farmers: ${farmers.length}`);
    console.log(`🏢 Traders: ${traders.length}`);
    console.log(`👥 Users: ${users.length}`);
    console.log(`🛒 Retail Products: ${sampleRetailProducts.length}`);
    console.log(`📦 Wholesale Products: ${sampleWholesaleProducts.length}`);
    console.log(`📰 News Articles: ${sampleNews.length}`);
    console.log(`📋 Schemes: ${sampleSchemes.length}`);
    console.log(`🚚 Delivery Partners: ${sampleDeliveryPartners.length}`);
    
    console.log('\n🔐 Sample Login Credentials:');
    console.log('Farmer: Phone: 9876543210, Password: password123');
    console.log('Trader: Phone: 9876543220, Password: password123');
    console.log('User: Phone: 9876543230, Password: password123');

    process.exit(0);
  } catch (error) {
    console.error('❌ Error seeding database:', error);
    process.exit(1);
  }
}

seedDatabase();
