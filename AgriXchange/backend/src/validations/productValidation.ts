import Joi from 'joi';

export const createProductSchema = {
  body: Joi.object({
    name: Joi.string().min(2).max(100).required(),
    category: Joi.string().valid(
      'vegetables', 'fruits', 'grains', 'pulses', 'spices', 'herbs', 'dairy', 'other'
    ).required(),
    description: Joi.string().max(500).optional(),
    location: Joi.object({
      latitude: Joi.number().min(-90).max(90).required(),
      longitude: Joi.number().min(-180).max(180).required(),
      address: Joi.string().required()
    }).required(),
    type: Joi.string().valid('retail', 'wholesale').required(),
    // Retail specific
    price: Joi.when('type', {
      is: 'retail',
      then: Joi.number().min(0).required(),
      otherwise: Joi.forbidden()
    }),
    unit: Joi.when('type', {
      is: 'retail',
      then: Joi.string().required(),
      otherwise: Joi.forbidden()
    }),
    quantity: Joi.number().min(0).required(),
    minOrderQuantity: Joi.when('type', {
      is: 'retail',
      then: Joi.number().min(1).required(),
      otherwise: Joi.forbidden()
    }),
    // Wholesale specific
    startingPrice: Joi.when('type', {
      is: 'wholesale',
      then: Joi.number().min(0).required(),
      otherwise: Joi.forbidden()
    }),
    biddingDuration: Joi.when('type', {
      is: 'wholesale',
      then: Joi.number().min(1).max(168).required(), // 1 hour to 7 days
      otherwise: Joi.forbidden()
    })
  })
};

export const updateProductSchema = {
  body: Joi.object({
    name: Joi.string().min(2).max(100).optional(),
    description: Joi.string().max(500).optional(),
    price: Joi.number().min(0).optional(),
    quantity: Joi.number().min(0).optional(),
    minOrderQuantity: Joi.number().min(1).optional(),
    isActive: Joi.boolean().optional()
  })
};

export const productQuerySchema = {
  query: Joi.object({
    category: Joi.string().valid(
      'vegetables', 'fruits', 'grains', 'pulses', 'spices', 'herbs', 'dairy', 'other'
    ).optional(),
    type: Joi.string().valid('retail', 'wholesale').optional(),
    location: Joi.string().optional(),
    minPrice: Joi.number().min(0).optional(),
    maxPrice: Joi.number().min(0).optional(),
    sortBy: Joi.string().valid('price-asc', 'price-desc', 'latest', 'popular').optional(),
    search: Joi.string().optional(),
    page: Joi.number().min(1).optional(),
    limit: Joi.number().min(1).max(100).optional()
  })
};

export const productParamsSchema = {
  params: Joi.object({
    id: Joi.string().pattern(/^[0-9a-fA-F]{24}$/).required()
  })
};
