import Joi from 'joi';

export const placeBidSchema = {
  body: Joi.object({
    amount: Joi.number().min(0).required()
  }),
  params: Joi.object({
    productId: Joi.string().pattern(/^[0-9a-fA-F]{24}$/).required()
  })
};

export const biddingQuerySchema = {
  query: Joi.object({
    category: Joi.string().valid(
      'vegetables', 'fruits', 'grains', 'pulses', 'spices', 'herbs', 'dairy', 'other'
    ).optional(),
    location: Joi.string().optional(),
    minPrice: Joi.number().min(0).optional(),
    maxPrice: Joi.number().min(0).optional(),
    endingIn: Joi.string().valid('1h', '6h', '24h', 'all').optional(),
    sortBy: Joi.string().valid('ending-soon', 'highest-bid', 'lowest-bid', 'latest').optional(),
    page: Joi.number().min(1).optional(),
    limit: Joi.number().min(1).max(100).optional()
  })
};

export const biddingRoomParamsSchema = {
  params: Joi.object({
    roomId: Joi.string().pattern(/^[0-9a-fA-F]{24}$/).required()
  })
};
