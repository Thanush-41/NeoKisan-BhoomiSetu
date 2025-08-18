import mongoose, { Schema, Document } from 'mongoose';
import { INewsArticle } from '../types/index.js';

const newsArticleSchema = new Schema({
  title: { 
    type: String, 
    required: true, 
    trim: true 
  },
  content: { 
    type: String, 
    required: true 
  },
  summary: { 
    type: String, 
    required: true, 
    maxlength: 500 
  },
  imageUrl: String,
  source: { 
    type: String, 
    required: true 
  },
  category: { 
    type: String, 
    enum: ['farming', 'weather', 'market', 'government', 'technology'],
    required: true 
  },
  publishedAt: { 
    type: Date, 
    required: true 
  },
  tags: [{ 
    type: String, 
    trim: true 
  }],
  isActive: { 
    type: Boolean, 
    default: true 
  },
}, {
  timestamps: true,
});

// Indexes for efficient queries
newsArticleSchema.index({ category: 1, publishedAt: -1 });
newsArticleSchema.index({ publishedAt: -1 });
newsArticleSchema.index({ isActive: 1 });
newsArticleSchema.index({ tags: 1 });
newsArticleSchema.index({ title: 'text', content: 'text', summary: 'text' });

export const NewsArticle = mongoose.model('NewsArticle', newsArticleSchema);

export default NewsArticle;
