<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# BhoomiSetu - Agricultural AI Advisor

This is an AI-powered agricultural advisor system for Indian farmers that works on both web and Telegram platforms.

## Project Structure

- `src/agents/` - Core AI agent with agricultural intelligence
- `src/web/` - FastAPI web application and REST APIs
- `src/telegram/` - Telegram bot implementation
- `src/knowledge/` - Agricultural knowledge base and data
- `templates/` - HTML templates for web interface
- `static/` - Static files (CSS, JS, images)

## Key Technologies

- **Python/FastAPI** for web backend
- **python-telegram-bot** for Telegram integration
- **LangChain + OpenAI** for AI/ML capabilities
- **APIs**: OpenWeather, Data.gov.in for real-time data
- **Multi-language support** using Google Translate

## Development Guidelines

### When working on this project:

1. **Agricultural Focus**: Always consider Indian farming context, crops, and practices
2. **Multilingual Support**: Code should handle Hindi, Telugu, English, and other Indian languages
3. **API Integration**: Use provided API keys for weather and commodity data
4. **User Experience**: Design for farmers with varying digital literacy
5. **Data Accuracy**: Ensure agricultural advice is factual and location-specific

### Code Style:

- Follow PEP 8 for Python code
- Use async/await for I/O operations
- Include proper error handling and logging
- Add docstrings for all functions and classes
- Use type hints where appropriate

### API Keys Configuration:

The project uses these APIs:
- OpenWeather API (weather data)
- Data.gov.in API (commodity prices)
- Telegram Bot API
- OpenAI API (you need to add your own key)

### Agricultural Knowledge:

When adding crop information or advice:
- Use scientifically accurate data
- Consider Indian climate zones and seasons
- Include local variety names and regional practices
- Provide practical, actionable advice
- Consider cost-effectiveness for small farmers

### Testing:

- Test both web and Telegram interfaces
- Verify multilingual functionality
- Check API integrations
- Test edge cases and error scenarios
