import { Router } from 'express';
import {
  register,
  login,
  getProfile,
  updateProfile,
  changePassword,
  deleteAccount
} from '../controllers/index.js';
import { authenticateToken } from '../middleware/index.js';
import { validateRequest } from '../middleware/index.js';
import {
  registerSchema,
  loginSchema,
  updateProfileSchema,
  changePasswordSchema
} from '../validations/index.js';

const router = Router();

// Public routes
router.post('/register', validateRequest(registerSchema), register);
router.post('/login', validateRequest(loginSchema), login);

// Protected routes
router.use(authenticateToken);
router.get('/profile', getProfile);
router.put('/profile', validateRequest(updateProfileSchema), updateProfile);
router.put('/change-password', validateRequest(changePasswordSchema), changePassword);
router.delete('/account', deleteAccount);

export default router;
