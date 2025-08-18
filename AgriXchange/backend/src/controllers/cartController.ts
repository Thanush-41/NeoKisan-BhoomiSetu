import { Request, Response } from 'express';
import { Cart } from '../models/Cart.js';
import { Product } from '../models/Product.js';

// Get cart for use
export const getCart = async (req: any, res: Response) => {
  try {
    const userId = req.user.userId;
    const cart = await Cart.findOne({ userId }).populate('items.productId');
    res.json({ success: true, data: cart });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to get cart' });
  }
};

// Add item to cart
export const addToCart = async (req: any, res: Response) => {
  try {
    const userId = req.user.userId;
    const { productId, quantity } = req.body;
    let cart = await Cart.findOne({ userId });
    if (!cart) {
      cart = new Cart({ userId, items: [] });
    }
    // Check product stock
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({ success: false, message: 'Product not found' });
    }

    // Decrement stock

    await product.save();
    // Add to cart
    const itemIndex = cart.items.findIndex((item: any) => item.productId.toString() === productId);
    if (itemIndex > -1) {
      cart.items[itemIndex].quantity += quantity;
    } else {
      cart.items.push({ productId, quantity });
    }
    cart.updatedAt = new Date();
    await cart.save();
    res.json({ success: true, data: cart });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to add to cart' });
  }
};

// Update item quantity
export const updateCartItem = async (req: any, res: Response) => {
  try {
    const userId = req.user.userId;
    const { productId, quantity } = req.body;
    const cart = await Cart.findOne({ userId });
    if (!cart) return res.status(404).json({ success: false, message: 'Cart not found' });
    const item = cart.items.find((item: any) => item.productId.toString() === productId);
    if (!item) return res.status(404).json({ success: false, message: 'Item not found' });
    // Check product stock
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({ success: false, message: 'Product not found' });
    }
    // Increment stock if quantity is reduced
    if (quantity < item.quantity) {
      const diff = item.quantity - quantity;

      await product.save();
    }
    item.quantity = quantity;
    cart.updatedAt = new Date();
    await cart.save();
    res.json({ success: true, data: cart });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to update cart item' });
  }
};

// Remove item from cart
export const removeFromCart = async (req: any, res: Response) => {
  try {
    const userId = req.user.userId;
    const { productId } = req.body;
    const cart = await Cart.findOne({ userId });
    if (!cart) return res.status(404).json({ success: false, message: 'Cart not found' });
    const item = cart.items.find((item: any) => item.productId.toString() === productId);
    if (!item) return res.status(404).json({ success: false, message: 'Item not found' });
    // Check product stock
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({ success: false, message: 'Product not found' });
    }
    // Increment stock

    await product.save();
    cart.items = cart.items.filter((item: any) => item.productId.toString() !== productId);
    cart.updatedAt = new Date();
    await cart.save();
    res.json({ success: true, data: cart });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to remove from cart' });
  }
};

// Clear cart
export const clearCart = async (req: any, res: Response) => {
  try {
    const userId = req.user.userId;
    const cart = await Cart.findOne({ userId });
    if (!cart) return res.status(404).json({ success: false, message: 'Cart not found' });
    // Restore product quantities
    for (const item of cart.items) {
      const product = await Product.findById(item.productId);
      if (product) {

        await product.save();
      }
    }
    cart.items = [];
    cart.updatedAt = new Date();
    await cart.save();
    res.json({ success: true, data: cart });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to clear cart' });
  }
};
