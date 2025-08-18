import { Router } from 'express';
import {
  getActiveBiddings,
  getBiddingRoom,
  placeBid,
  getMyBids,
  getBiddingHistory,
  getMyWinningBids
} from '../controllers/index.js';
import { authenticateToken, authorizeRoles } from '../middleware/index.js';
import { validateRequest } from '../middleware/index.js';
import {
  placeBidSchema,
  biddingQuerySchema,
  biddingRoomParamsSchema
} from '../validations/index.js';

const router = Router();

// Public routes
router.get('/active', validateRequest(biddingQuerySchema), getActiveBiddings);
router.get('/room/:roomId', validateRequest(biddingRoomParamsSchema), getBiddingRoom);
router.get('/history/:productId', getBiddingHistory);

// Protected routes
router.use(authenticateToken);

// Trader only routes
router.post('/bid/:productId', 
  authorizeRoles('trader'), 
  validateRequest(placeBidSchema), 
  placeBid
);

router.get('/my/bids', 
  authorizeRoles('trader'), 
  getMyBids
);

router.get('/my/winning', 
  authorizeRoles('trader'), 
  getMyWinningBids
);

export default router;
