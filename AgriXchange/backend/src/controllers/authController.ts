import { Request, Response } from 'express';
import { User, Farmer, Trader, RegularUser } from '../models/index.js';
import { AuthenticatedRequest } from '../types/index.js';
import { generateToken, successResponse, errorResponse, sanitizeUser } from '../utils/index.js';

export const register = async (req: Request, res: Response): Promise<void> => {
  try {
    const { role, ...userData } = req.body;
    
    console.log('=== REGISTRATION DEBUG ===');
    console.log('Full request body:', req.body);
    console.log('Extracted role:', role);
    console.log('User data:', userData);
    console.log('========================');

    // Check if user already exists
    const existingUser = await User.findOne({ phone: userData.phone });
    if (existingUser) {
      console.log('Registration failed: User already exists with phone:', userData.phone);
      res.status(400).json(errorResponse('User already exists with this phone number'));
      return;
    }

    // Check email if provided
    if (userData.email) {
      const existingEmail = await User.findOne({ email: userData.email });
      if (existingEmail) {
        console.log('Registration failed: User already exists with email:', userData.email);
        res.status(400).json(errorResponse('User already exists with this email'));
        return;
      }
    }

    let user;
    switch (role) {
      case 'farmer':
        user = new Farmer(userData);
        break;
      case 'trader':
        // Check if GSTIN already exists
        const existingGstin = await Trader.findOne({ gstin: userData.gstin });
        if (existingGstin) {
          console.log('Registration failed: Trader already exists with GSTIN:', userData.gstin);
          res.status(400).json(errorResponse('Trader already exists with this GSTIN'));
          return;
        }
        user = new Trader(userData);
        break;
      case 'user':
        user = new RegularUser(userData);
        break;
      default:
        console.log('Registration failed: Invalid role:', role);
        res.status(400).json(errorResponse('Invalid role'));
        return;
    }

    await user.save();
    console.log('Registration successful for user:', (user as any).name);

    const token = generateToken(user._id!.toString(), (user as any).role);

    res.status(201).json(successResponse({
      token,
      user: sanitizeUser(user)
    }, 'User registered successfully'));

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json(errorResponse('Registration failed'));
  }
};

export const login = async (req: Request, res: Response): Promise<void> => {
  try {
    const { phone, password } = req.body;

    // Only allow login with phone (role is not required for login)
    const user = await User.findOne({ phone });
    if (!user) {
      res.status(401).json(errorResponse('Invalid credentials'));
      return;
    }

    // Check password
    const isPasswordValid = await (user as any).comparePassword(password);
    if (!isPasswordValid) {
      res.status(401).json(errorResponse('Invalid credentials'));
      return;
    }

    // Check if user is active
    if (!user.isActive) {
      res.status(401).json(errorResponse('Account is deactivated'));
      return;
    }

    const token = generateToken(user._id!.toString(), user.role);

    res.json(successResponse({
      token,
      user: sanitizeUser(user)
    }, 'Login successful'));

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json(errorResponse('Login failed'));
  }
};

export const getProfile = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const user = await User.findById(req.user!.userId);
    if (!user) {
      res.status(404).json(errorResponse('User not found'));
      return;
    }

    res.json(successResponse(sanitizeUser(user), 'Profile retrieved successfully'));

  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json(errorResponse('Failed to retrieve profile'));
  }
};

export const updateProfile = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const user = await User.findById(req.user!.userId);
    if (!user) {
      res.status(404).json(errorResponse('User not found'));
      return;
    }

    // Update allowed fields
    const allowedFields = ['name', 'email', 'address', 'farmSize', 'cropTypes', 'companyName'];
    const updates = Object.keys(req.body)
      .filter(key => allowedFields.includes(key))
      .reduce((obj, key) => {
        obj[key] = req.body[key];
        return obj;
      }, {} as any);

    Object.assign(user, updates);
    await user.save();

    res.json(successResponse(sanitizeUser(user), 'Profile updated successfully'));

  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json(errorResponse('Failed to update profile'));
  }
};

export const changePassword = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { currentPassword, newPassword } = req.body;
    const user = await User.findById(req.user!.userId);
    if (!user) {
      res.status(404).json(errorResponse('User not found'));
      return;
    }
    // Verify current password
    const isCurrentPasswordValid = await (user as any).comparePassword(currentPassword);
    if (!isCurrentPasswordValid) {
      res.status(400).json(errorResponse('Current password is incorrect'));
      return;
    }
    // Update password
    user.password = newPassword;
    await user.save();
    res.json(successResponse(null, 'Password changed successfully'));
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json(errorResponse('Failed to change password'));
  }
};

export const deleteAccount = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const user = await User.findById(req.user!.userId);
    if (!user) {
      res.status(404).json(errorResponse('User not found'));
      return;
    }

    // Soft delete - deactivate account
    user.isActive = false;
    await user.save();

    res.json(successResponse(null, 'Account deactivated successfully'));

  } catch (error) {
    console.error('Delete account error:', error);
    res.status(500).json(errorResponse('Failed to delete account'));
  }
};
