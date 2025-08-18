import { PaginatedResponse } from '../types/index.js';

export interface PaginationOptions {
  page?: number;
  limit?: number;
  sort?: string;
}

export const getPaginationOptions = (query: any): Required<PaginationOptions> => {
  const page = Math.max(1, parseInt(query.page) || 1);
  const limit = Math.min(100, Math.max(1, parseInt(query.limit) || 10));
  const sort = query.sort || '-createdAt';

  return { page, limit, sort };
};

export const createPaginatedResponse = <T>(
  data: T[],
  total: number,
  page: number,
  limit: number
): PaginatedResponse<T> => {
  const totalPages = Math.ceil(total / limit);
  
  return {
    data,
    pagination: {
      page,
      limit,
      total,
      totalPages
    }
  };
};

export const getSkipValue = (page: number, limit: number): number => {
  return (page - 1) * limit;
};
