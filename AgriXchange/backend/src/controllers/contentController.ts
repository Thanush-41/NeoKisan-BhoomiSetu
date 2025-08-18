import { Request, Response } from 'express';
import { NewsArticle, Scheme } from '../models/index.js';
import { 
  successResponse, 
  errorResponse, 
  getPaginationOptions, 
  createPaginatedResponse, 
  getSkipValue 
} from '../utils/index.js';

export const getNews = async (req: Request, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    const query: any = { isActive: true };
    
    if (req.query.category) {
      query.category = req.query.category;
    }
    
    if (req.query.search) {
      query.$text = { $search: req.query.search };
    }

    const news = await NewsArticle.find(query)
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await NewsArticle.countDocuments(query);

    const response = createPaginatedResponse(news, total, page, limit);
    res.json(successResponse(response, 'News articles retrieved successfully'));

  } catch (error) {
    console.error('Get news error:', error);
    res.status(500).json(errorResponse('Failed to retrieve news articles'));
  }
};

export const getNewsArticle = async (req: Request, res: Response): Promise<void> => {
  try {
    const article = await NewsArticle.findById(req.params.id);
    
    if (!article || !article.isActive) {
      res.status(404).json(errorResponse('Article not found'));
      return;
    }

    res.json(successResponse(article, 'News article retrieved successfully'));

  } catch (error) {
    console.error('Get news article error:', error);
    res.status(500).json(errorResponse('Failed to retrieve news article'));
  }
};

export const getSchemes = async (req: Request, res: Response): Promise<void> => {
  try {
    const { page, limit, sort } = getPaginationOptions(req.query);
    const skip = getSkipValue(page, limit);

    const query: any = { isActive: true };
    
    if (req.query.search) {
      query.$text = { $search: req.query.search };
    }

    const schemes = await Scheme.find(query)
      .sort(sort)
      .skip(skip)
      .limit(limit);

    const total = await Scheme.countDocuments(query);

    const response = createPaginatedResponse(schemes, total, page, limit);
    res.json(successResponse(response, 'Schemes retrieved successfully'));

  } catch (error) {
    console.error('Get schemes error:', error);
    res.status(500).json(errorResponse('Failed to retrieve schemes'));
  }
};

export const getScheme = async (req: Request, res: Response): Promise<void> => {
  try {
    const scheme = await Scheme.findById(req.params.id);
    
    if (!scheme || !scheme.isActive) {
      res.status(404).json(errorResponse('Scheme not found'));
      return;
    }

    res.json(successResponse(scheme, 'Scheme retrieved successfully'));

  } catch (error) {
    console.error('Get scheme error:', error);
    res.status(500).json(errorResponse('Failed to retrieve scheme'));
  }
};
