import { Request, Response } from 'express';
import { WeatherService } from '../services/index.js';
import { successResponse, errorResponse } from '../utils/index.js';

export const getWeatherByLocation = async (req: Request, res: Response): Promise<void> => {
  try {
    const { latitude, longitude } = req.query;
    
    if (!latitude || !longitude) {
      res.status(400).json(errorResponse('Latitude and longitude are required'));
      return;
    }

    const weatherData = await WeatherService.getCurrentWeather(
      parseFloat(latitude as string),
      parseFloat(longitude as string)
    );

    if (!weatherData) {
      res.status(500).json(errorResponse('Failed to fetch weather data'));
      return;
    }

    res.json(successResponse(weatherData, 'Weather data retrieved successfully'));

  } catch (error) {
    console.error('Get weather by location error:', error);
    res.status(500).json(errorResponse('Failed to retrieve weather data'));
  }
};

export const getWeatherByCity = async (req: Request, res: Response): Promise<void> => {
  try {
    const { city } = req.params;
    
    if (!city) {
      res.status(400).json(errorResponse('City is required'));
      return;
    }

    const weatherData = await WeatherService.getWeatherByCity(city);

    if (!weatherData) {
      res.status(500).json(errorResponse('Failed to fetch weather data'));
      return;
    }

    res.json(successResponse(weatherData, 'Weather data retrieved successfully'));

  } catch (error) {
    console.error('Get weather by city error:', error);
    res.status(500).json(errorResponse('Failed to retrieve weather data'));
  }
};
