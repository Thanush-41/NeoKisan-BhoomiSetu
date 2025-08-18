import { Router } from 'express';
import {
  getWeatherByLocation,
  getWeatherByCity
} from '../controllers/index.js';

const router = Router();

// Public routes
router.get('/location', getWeatherByLocation);
router.get('/city/:city', getWeatherByCity);

export default router;
