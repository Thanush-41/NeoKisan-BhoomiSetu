import axios from 'axios';
import config from '../config/index.js';
import { IWeatherData, IWeatherForecast } from '../types/index.js';

class WeatherService {
  private apiKey: string;
  private baseUrl: string;

  constructor() {
    this.apiKey = config.weatherApiKey;
    this.baseUrl = 'https://api.openweathermap.org/data/2.5';
  }

  async getCurrentWeather(lat: number, lon: number): Promise<IWeatherData | null> {
    try {
      if (!this.apiKey) {
        // Return mock data if no API key
        return this.getMockWeatherData();
      }

      const response = await axios.get(`${this.baseUrl}/weather`, {
        params: {
          lat,
          lon,
          appid: this.apiKey,
          units: 'metric'
        }
      });

      const forecastResponse = await axios.get(`${this.baseUrl}/forecast`, {
        params: {
          lat,
          lon,
          appid: this.apiKey,
          units: 'metric'
        }
      });

      const weatherData = response.data;
      const forecastData = forecastResponse.data;

      const forecast: IWeatherForecast[] = forecastData.list
        .filter((_: any, index: number) => index % 8 === 0) // Get one forecast per day
        .slice(0, 5)
        .map((item: any) => ({
          date: new Date(item.dt * 1000).toISOString().split('T')[0],
          temperature: {
            min: item.main.temp_min,
            max: item.main.temp_max
          },
          description: item.weather[0].description,
          humidity: item.main.humidity,
          rainfall: item.rain ? item.rain['3h'] : 0
        }));

      return {
        location: weatherData.name,
        temperature: weatherData.main.temp,
        humidity: weatherData.main.humidity,
        description: weatherData.weather[0].description,
        windSpeed: weatherData.wind.speed,
        pressure: weatherData.main.pressure,
        forecast,
        updatedAt: new Date()
      };
    } catch (error) {
      console.error('Weather API error:', error);
      return this.getMockWeatherData();
    }
  }

  async getWeatherByCity(city: string): Promise<IWeatherData | null> {
    try {
      if (!this.apiKey) {
        return this.getMockWeatherData();
      }

      const response = await axios.get(`${this.baseUrl}/weather`, {
        params: {
          q: city,
          appid: this.apiKey,
          units: 'metric'
        }
      });

      const weatherData = response.data;
      return this.getCurrentWeather(weatherData.coord.lat, weatherData.coord.lon);
    } catch (error) {
      console.error('Weather API error:', error);
      return this.getMockWeatherData();
    }
  }

  private getMockWeatherData(): IWeatherData {
    return {
      location: 'Sample City',
      temperature: 25,
      humidity: 65,
      description: 'Clear sky',
      windSpeed: 5.2,
      pressure: 1013,
      forecast: [
        {
          date: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          temperature: { min: 20, max: 28 },
          description: 'Partly cloudy',
          humidity: 60,
          rainfall: 0
        },
        {
          date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          temperature: { min: 22, max: 30 },
          description: 'Sunny',
          humidity: 55,
          rainfall: 0
        },
        {
          date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          temperature: { min: 18, max: 25 },
          description: 'Light rain',
          humidity: 80,
          rainfall: 2.5
        },
        {
          date: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          temperature: { min: 21, max: 27 },
          description: 'Cloudy',
          humidity: 70,
          rainfall: 0
        },
        {
          date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          temperature: { min: 23, max: 29 },
          description: 'Clear sky',
          humidity: 58,
          rainfall: 0
        }
      ],
      updatedAt: new Date()
    };
  }
}

export default new WeatherService();
