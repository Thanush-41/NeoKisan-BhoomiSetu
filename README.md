# BhoomiSetu - AI-Powered Agricultural Advisor

**🌾 Empowering Indian Farmers with AI Technology**

BhoomiSetu is an intelligent agricultural advisor that helps farmers make informed decisions about irrigation, crop selection, weather planning, market prices, and government schemes. The platform works both as a web application and a Telegram bot, supporting multiple Indian languages.

## 🚀 Features

### 🌱 **Agricultural Intelligence**
- **Irrigation Guidance**: Get personalized advice on when and how to irrigate crops
- **Crop Selection**: Choose optimal seed varieties based on climate, soil, and market conditions  
- **Weather Integration**: Real-time weather data and forecasts for farming decisions
- **Pest & Disease Management**: Expert advice on crop protection

### 💰 **Market & Financial Support**
- **Live Market Prices**: Current commodity prices from various mandis across India
- **Government Schemes**: Information about PM-KISAN, KCC, PMFBY and state schemes
- **Loan Guidance**: Help with agricultural credit and financing options

### 🌐 **Multi-Platform Access**
- **Web Interface**: Modern, responsive web application
- **Telegram Bot**: Chat with the AI advisor on Telegram (@neokisan_bot)
- **Multilingual Support**: Hindi, English, Telugu, and other Indian languages

### 🎯 **Smart Features**
- **Natural Language Processing**: Ask questions in your preferred language
- **Context-Aware Responses**: Personalized advice based on location and crop type
- **Real-time Data**: Live weather and market price integration
- **Reliable Sources**: Uses government APIs and verified agricultural data

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, LangChain
- **AI/ML**: OpenAI GPT, Google Translate API
- **APIs**: OpenWeather API, Data.gov.in commodity prices
- **Bot**: python-telegram-bot
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Database**: SQLite (configurable)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API Keys:
  - OpenAI API key
  - OpenWeather API key (provided)
  - Telegram Bot Token (provided)
  - Data.gov.in API key (provided)

### Installation

1. **Clone and Setup**
   ```bash
   cd BhoomiSetu
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Update `.env` file with your OpenAI API key
   - Other API keys are pre-configured

3. **Run the Application**
   ```bash
   python main.py
   ```

4. **Access the Platform**
   - Web Interface: http://localhost:8000
   - Telegram Bot: https://t.me/neokisan_bot

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required - Add your own
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Pre-configured
TELEGRAM_BOT_TOKEN=8023646765:AAEdKW_9JnvNg98kuNAm9oyw07MHbL-UgDk
DATA_GOV_API_KEY=579b464db66ec23bdd00000121ba61b5b04f400760f5e55625b4bb25

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 📱 Usage Examples

### Web Interface
1. Visit http://localhost:8000
2. Use the chat interface or quick action buttons
3. Ask questions like:
   - "When should I irrigate my tomatoes?"
   - "What are today's onion prices?"
   - "Which wheat variety is best for Punjab?"

### Telegram Bot
1. Start chat with @neokisan_bot
2. Use commands or natural language:
   ```
   /start - Welcome and menu
   /location Delhi - Set your location
   /weather - Get weather forecast
   /prices onion - Check onion prices
   ```

### API Endpoints
```bash
# Query the AI agent
POST /api/query
{
  "query": "When should I plant rice?",
  "location": "Hyderabad",
  "crop_type": "rice"
}

# Get weather data
POST /api/weather
{
  "location": "Mumbai"
}

# Get market prices  
POST /api/prices
{
  "commodity": "onion"
}
```

## 🌾 Supported Agricultural Queries

### Irrigation Management
- "When should I water my crops?"
- "How much water does rice need?"
- "Should I irrigate before rain?"

### Crop Selection
- "Which seeds are best for this weather?"
- "What variety should I plant in black soil?"
- "Is it too late to sow wheat?"

### Weather Planning
- "Will next week's heat affect my yield?"
- "Should I harvest before the rain?"
- "What's the temperature forecast?"

### Market Intelligence
- "What are tomato prices today?"
- "Should I sell now or wait?"
- "Which market has better rates?"

### Financial Guidance
- "How can I get a KCC loan?"
- "What subsidies are available?"
- "Am I eligible for PM-KISAN?"

## 🔗 Data Sources

- **Weather**: OpenWeather API
- **Market Prices**: Government of India Open Data Platform
- **Agricultural Knowledge**: Integrated crop databases and expert systems
- **Schemes**: Central and state government portals

## 🤝 Contributing

This project was developed for an agricultural AI challenge focusing on helping Indian farmers with data-driven decisions. The solution addresses:

- Multilingual, colloquial query handling
- Real-world constraints like limited internet access
- Noisy, incomplete public datasets
- Trust and explainability requirements
- Edge cases where wrong advice has real costs

## 📞 Support

- **Web**: Use the chat interface for instant help
- **Telegram**: @neokisan_bot
- **Issues**: Report bugs or request features

## 📄 License

This project uses publicly available datasets and APIs in compliance with their terms of service.

---

**🌾 BhoomiSetu - Bridging Technology and Agriculture for a Better Tomorrow**
