import jwt from 'jsonwebtoken';
import { JWTPayload, UserRole } from '../types/index.js';
import config from '../config/index.js';

export const generateToken = (userId: string, role: string): string => {
  const payload: JWTPayload = {
    userId,
    role: role as UserRole
  };

  return jwt.sign(payload, config.jwtSecret, {
    expiresIn: '24h'
  });
};

export const generateRefreshToken = (userId: string, role: string): string => {
  const payload: JWTPayload = {
    userId,
    role: role as UserRole
  };

  return jwt.sign(payload, config.jwtSecret, {
    expiresIn: '7d'
  });
};

export const verifyToken = (token: string): JWTPayload => {
  return jwt.verify(token, config.jwtSecret) as JWTPayload;
};
