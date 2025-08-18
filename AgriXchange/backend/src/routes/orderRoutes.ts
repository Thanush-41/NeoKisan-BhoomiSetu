import { Router } from 'express';
import {
  createOrder,
  getOrders,
  getOrder,
  updateOrderStatus,
  cancelOrder,
  getOrderStatistics
} from '../controllers/index.js';
import { authenticateToken, authorizeRoles } from '../middleware/index.js';
import { validateRequest } from '../middleware/index.js';
import {
  createOrderSchema,
  updateOrderStatusSchema,
  orderQuerySchema,
  orderParamsSchema
} from '../validations/index.js';

const router = Router();

// Protected routes
router.use(authenticateToken);

// User routes
router.post('/', 
  authorizeRoles('user'), 
  validateRequest(createOrderSchema), 
  createOrder
);

router.get('/', 
  validateRequest(orderQuerySchema), 
  getOrders
);

router.get('/statistics', getOrderStatistics);

router.get('/:orderId', 
  validateRequest(orderParamsSchema), 
  getOrder
);

router.put('/:orderId/status', 
  validateRequest(updateOrderStatusSchema), 
  updateOrderStatus
);

router.put('/:orderId/cancel', 
  validateRequest(orderParamsSchema), 
  cancelOrder
);

export default router;
