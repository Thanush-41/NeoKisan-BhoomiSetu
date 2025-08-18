import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { CartItem, RetailProduct } from '../types';

interface CartContextType {
  items: CartItem[];
  totalItems: number;
  totalAmount: number;
  addToCart: (product: RetailProduct, quantity: number) => Promise<void>;
  removeFromCart: (productId: string) => Promise<void>;
  updateQuantity: (productId: string, quantity: number) => Promise<void>;
  clearCart: () => Promise<void>;
  isInCart: (productId: string) => boolean;
  getItemQuantity: (productId: string) => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>([]);
  const token = localStorage.getItem('agrixchange_token');

  // Fetch cart from backend
  const fetchCart = async () => {
    if (!token) return;
    try {
      const res = await fetch('https://agrixchange.onrender.com/api/cart', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok && data.success && data.data && Array.isArray(data.data.items)) {
        // Map backend cart items to frontend CartItem
        setItems(
          data.data.items.map((item: any) => {
            if (!item.productId) return null; // skip nulls
            return {
              productId: item.productId._id || item.productId,
              product: item.productId, // populated product
              quantity: item.quantity,
            };
          }).filter(Boolean)
        );
      } else {
        setItems([]); // Ensure cart is empty if no data
        if (!data.success) {
          console.error('Cart fetch error:', data.message || data.error);
        }
      }
    } catch (e) {
      setItems([]);
      console.error('Cart fetch exception:', e);
    }
  };

  useEffect(() => {
    fetchCart();
    // eslint-disable-next-line
  }, [token]);

  const addToCart = async (product: RetailProduct, quantity: number): Promise<void> => {
    if (!token) return;
    const res = await fetch('https://agrixchange.onrender.com/api/cart/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ productId: product.id, quantity }),
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      console.error('Add to cart error:', data.message || data.error);
    } else {
      console.log('Add to cart response:', data);
    }
    await fetchCart();
  };

  const removeFromCart = async (productId: string): Promise<void> => {
    if (!token) return;
    await fetch('https://agrixchange.onrender.coms/api/cart/remove', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ productId }),
    });
    await fetchCart();
  };

  const updateQuantity = async (productId: string, quantity: number): Promise<void> => {
    if (!token) return;
    await fetch('https://agrixchange.onrender.com/api/cart/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ productId, quantity }),
    });
    await fetchCart();
  };

  const clearCart = async (): Promise<void> => {
    if (!token) return;
    await fetch('https://agrixchange.onrender.com/api/cart/clear', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    await fetchCart();
  };

  const isInCart = (productId: string) => {
    return items.some(item => item.productId === productId);
  };

  const getItemQuantity = (productId: string) => {
    const item = items.find(item => item.productId === productId);
    return item ? item.quantity : 0;
  };

  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const totalAmount = items.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);

  const value = {
    items,
    totalItems,
    totalAmount,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    isInCart,
    getItemQuantity,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
