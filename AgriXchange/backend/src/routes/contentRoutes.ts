import { Router } from 'express';
import {
  getNews,
  getNewsArticle,
  getSchemes,
  getScheme
} from '../controllers/index.js';

const router = Router();

// Public routes
router.get('/news', getNews);
router.get('/news/:id', getNewsArticle);
router.get('/schemes', getSchemes);
router.get('/schemes/:id', getScheme);

export default router;
