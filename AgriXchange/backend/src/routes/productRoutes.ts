import { Router } from 'express';
import {
  createProduct,
  getProducts,
  getProduct,
  updateProduct,
  deleteProduct,
  getMyProducts,
  getFarmerProducts,
  rateProduct
} from '../controllers/index.js';
import { authenticateToken, authorizeRoles, optionalAuth, uploadProductImages } from '../middleware/index.js';
import { validateRequest } from '../middleware/index.js';
import {
  createProductSchema,
  updateProductSchema,
  productQuerySchema,
  productParamsSchema
} from '../validations/index.js';

const router = Router();

// Public routes
router.get('/', optionalAuth, validateRequest(productQuerySchema), getProducts);
router.get('/:id', validateRequest(productParamsSchema), getProduct);
router.get('/farmer/:farmerId', getFarmerProducts);

// Protected routes
router.use(authenticateToken);

// Farmer only routes
router.post('/', 
  authorizeRoles('farmer'),
  uploadProductImages,
  // Remove validation for now since we need to parse location first
  createProduct
);

router.put('/:id', 
  authorizeRoles('farmer'), 
  validateRequest({
    body: updateProductSchema.body,
    params: productParamsSchema.params
  }), 
  updateProduct
);

router.delete('/:id', 
  authorizeRoles('farmer'), 
  validateRequest(productParamsSchema), 
  deleteProduct
);

router.get('/my/products', 
  authorizeRoles('farmer'), 
  validateRequest(productQuerySchema), 
  getMyProducts
);

// Add product rating (authenticated users)
router.post('/:id/rate', authenticateToken, rateProduct);

export default router;
