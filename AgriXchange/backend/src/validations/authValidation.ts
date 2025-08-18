import Joi from 'joi';

export const registerSchema = {
  body: Joi.object({
    name: Joi.string().min(2).max(50).required(),
    email: Joi.string().email().optional(),
    phone: Joi.string().pattern(/^[0-9]{10}$/).required(),
    password: Joi.string().min(6).required(),
    role: Joi.string().valid('farmer', 'trader', 'user').required(),
    address: Joi.string().min(5).max(200).required(),
    // Farmer specific
    farmSize: Joi.when('role', {
      is: 'farmer',
      then: Joi.string().optional(),
      otherwise: Joi.forbidden()
    }),
    cropTypes: Joi.when('role', {
      is: 'farmer',
      then: Joi.string().optional(),
      otherwise: Joi.forbidden()
    }),
    // Trader specific
    gstin: Joi.when('role', {
      is: 'trader',
      then: Joi.string().pattern(/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/).required(),
      otherwise: Joi.forbidden()
    }),
    licenseNumber: Joi.when('role', {
      is: 'trader',
      then: Joi.string().required(),
      otherwise: Joi.forbidden()
    }),
    companyName: Joi.when('role', {
      is: 'trader',
      then: Joi.string().max(100).optional(),
      otherwise: Joi.forbidden()
    })
  })
};

export const loginSchema = {
  body: Joi.object({
    phone: Joi.string().pattern(/^[0-9]{10}$/).required(),
    password: Joi.string().min(6).required(),
    role: Joi.string().valid('farmer', 'trader', 'user').required()
  })
};

export const updateProfileSchema = {
  body: Joi.object({
    name: Joi.string().min(2).max(50).optional(),
    email: Joi.string().email().optional(),
    address: Joi.string().min(5).max(200).optional(),
    farmSize: Joi.number().min(0).optional(),
    cropTypes: Joi.array().items(Joi.string()).optional(),
    companyName: Joi.string().max(100).optional()
  })
};

export const changePasswordSchema = {
  body: Joi.object({
    currentPassword: Joi.string().required(),
    newPassword: Joi.string().min(6).required(),
    confirmPassword: Joi.string().valid(Joi.ref('newPassword')).required()
  })
};
