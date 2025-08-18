import { Router } from 'express';
import type { RequestHandler } from 'express';
import { authenticateToken } from '../middleware/index.js';
import { getCart, addToCart, updateCartItem, removeFromCart, clearCart } from '../controllers/cartController.js';

const router = Router();

router.use(authenticateToken);

router.get('/', getCart as RequestHandler);
router.post('/add', addToCart as RequestHandler);
router.put('/update', updateCartItem as RequestHandler);
router.post('/remove', removeFromCart as RequestHandler); // changed from delete to post
router.post('/clear', clearCart as RequestHandler); // changed from delete to post

export default router;
