import mongoose, { Schema, Document } from 'mongoose';

export interface CartItem {
  productId: mongoose.Types.ObjectId;
  quantity: number;
}

export interface CartDocument extends Document {
  userId: mongoose.Types.ObjectId;
  items: CartItem[];
  updatedAt: Date;
}

const CartItemSchema = new Schema<CartItem>({
  productId: { type: Schema.Types.ObjectId, ref: 'Product', required: true },
  quantity: { type: Number, required: true, min: 1 },
});

const CartSchema = new Schema<CartDocument>({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true, unique: true },
  items: { type: [CartItemSchema], default: [] },
  updatedAt: { type: Date, default: Date.now },
});

export const Cart = mongoose.model<CartDocument>('Cart', CartSchema);
