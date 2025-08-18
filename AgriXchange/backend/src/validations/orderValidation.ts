import Joi from 'joi';

const addressSchema = Joi.object({
  street: Joi.string().required(),
  city: Joi.string().required(),
  state: Joi.string().required(),
  pincode: Joi.string().pattern(/^[0-9]{6}$/).required(),
  landmark: Joi.string().optional(),
  isDefault: Joi.boolean().optional()
});

const orderItemSchema = Joi.object({
  productId: Joi.string().pattern(/^[0-9a-fA-F]{24}$/).required(),
  quantity: Joi.number().min(1).required()
});

export const createOrderSchema = {
  body: Joi.object({
    items: Joi.array().items(orderItemSchema).min(1).required(),
    deliveryAddress: addressSchema.required(),
    paymentMethod: Joi.string().valid('cash', 'upi', 'card').required()
  })
};

export const updateOrderStatusSchema = {
  body: Joi.object({
    status: Joi.string().valid(
      'pending', 'confirmed', 'processing', 'shipped', 
      'out_for_delivery', 'delivered', 'cancelled', 'returned'
    ).required(),
    deliveryPartnerId: Joi.string().pattern(/^[0-9a-fA-F]{24}$/).optional()
  }),
  params: Joi.object({
    orderId: Joi.string().pattern(/^[0-9a-fA-F]{24}$/).required()
  })
};

export const orderQuerySchema = {
  query: Joi.object({
    status: Joi.string().valid(
      'pending', 'confirmed', 'processing', 'shipped', 
      'out_for_delivery', 'delivered', 'cancelled', 'returned'
    ).optional(),
    fromDate: Joi.date().optional(),
    toDate: Joi.date().optional(),
    page: Joi.number().min(1).optional(),
    limit: Joi.number().min(1).max(100).optional()
  })
};

export const orderParamsSchema = {
  params: Joi.object({
    orderId: Joi.string().pattern(/^[0-9a-fA-F]{24}$/).required()
  })
};
