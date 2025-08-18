import { Router } from 'express';
import authRoutes from './authRoutes.js';
import productRoutes from './productRoutes.js';
import biddingRoutes from './biddingRoutes.js';
import orderRoutes from './orderRoutes.js';
import weatherRoutes from './weatherRoutes.js';
import contentRoutes from './contentRoutes.js';
import cartRoutes from './cartRoutes.js';

const router = Router();

// API routes
router.use('/auth', authRoutes);
router.use('/products', productRoutes);
router.use('/bidding', biddingRoutes);
router.use('/orders', orderRoutes);
router.use('/weather', weatherRoutes);
router.use('/content', contentRoutes);
router.use('/cart', cartRoutes);

// Health check
router.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'AgriXchange API is running',
    timestamp: new Date().toISOString()
  });
});

export default router;
