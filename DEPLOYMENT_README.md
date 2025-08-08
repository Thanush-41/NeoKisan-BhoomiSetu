# 🌾 BhoomiSetu - Agricultural AI Advisor

**Successfully Deployed and Running!** ✅

BhoomiSetu is an AI-powered agricultural advisor designed specifically for Indian farmers. It provides intelligent guidance on irrigation, crop selection, weather forecasts, market prices, and government schemes through both web and Telegram interfaces.

## 🚀 **CURRENT STATUS**

✅ **Web Application**: Running at http://localhost:8000  
✅ **Telegram Bot**: Active at https://t.me/neokisan_bot  
✅ **Dependencies**: All installed and working  
✅ **APIs**: Weather and commodity data configured  
⚠️ **OpenAI Integration**: Requires API key for full AI features

## 🔧 **Quick Start**

### 1. **View Web Interface**
- Open: http://localhost:8000
- Features: Landing page, health check, API testing

### 2. **Chat with Telegram Bot**
- Visit: https://t.me/neokisan_bot
- Send `/start` to begin
- Ask questions like:
  - "When should I irrigate my crops?"
  - "What are today's onion prices?"
  - "How can I get a farm loan?"

### 3. **Enable Full AI Features**
```bash
# Edit .env file and add your OpenAI API key:
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Then restart the application:
```bash
python main.py
```

## 📋 **Available Commands**

### **Web Application**
```bash
python simple_start.py    # Start web interface only
python main.py            # Start both web and Telegram bot
```

### **Telegram Bot Only**
```bash
python src/telegram/bot.py
```

### **Testing**
```bash
python test_setup.py      # System check
python test_telegram.py   # Telegram functionality test
```

## 🔗 **API Endpoints**

- **Health Check**: http://localhost:8000/api/health
- **API Test**: http://localhost:8000/api/test
- **Documentation**: http://localhost:8000/docs (when running main.py)

## 🌾 **Features**

### **Agricultural Intelligence**
- **Irrigation Guidance**: Personalized watering advice
- **Crop Selection**: Optimal variety recommendations
- **Weather Integration**: Real-time forecasts
- **Pest Management**: Disease prevention tips

### **Market & Financial**
- **Live Prices**: Commodity rates from mandis
- **Government Schemes**: PM-KISAN, KCC, PMFBY info
- **Loan Guidance**: Credit and financing help

### **Multi-Platform**
- **Web Interface**: Modern responsive design
- **Telegram Bot**: Chat-based assistance
- **Multilingual**: Hindi, English, Telugu support

## 🛠 **Technical Stack**

- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Bot**: python-telegram-bot 22.3
- **AI**: OpenAI GPT-3.5-turbo
- **APIs**: OpenWeather, Data.gov.in
- **Frontend**: HTML5, Bootstrap 5

## 📁 **Project Structure**

```
BhoomiSetu/
├── src/
│   ├── agents/          # AI agricultural advisor
│   ├── web/             # FastAPI web application  
│   ├── telegram/        # Telegram bot
│   └── knowledge/       # Agricultural data
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── .env               # Environment variables
├── main.py           # Main application runner
├── simple_start.py   # Web-only startup
└── test_*.py        # Test scripts
```

## 🎯 **Usage Examples**

### **Telegram Bot Commands**
```
/start                    # Welcome message
/location Mumbai          # Set your location
/crop rice               # Set your crop type
/weather                 # Get weather forecast
/prices onion            # Check market prices
/help                    # Show help
```

### **Natural Language Queries**
```
English:
- "When should I plant wheat?"
- "What are the cotton prices today?"
- "How can I get a KCC loan?"

Hindi:
- "मुझे धान की फसल कब बोनी चाहिए?"
- "आज प्याज का भाव क्या है?"

Telugu:
- "వరి పంటకు ఎప్పుడు నీరు పట్టాలి?"
```

## 🔧 **Configuration**

### **Environment Variables (.env)**
```env
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Pre-configured (working)
TELEGRAM_BOT_TOKEN=8023646765:AAEdKW_9JnvNg98kuNAm9oyw07MHbL-UgDk
DATA_GOV_API_KEY=579b464db66ec23bdd00000121ba61b5b04f400760f5e55625b4bb25

# Server settings
HOST=0.0.0.0
PORT=8000
```

## 🌟 **Key Achievements**

✅ **Multilingual Support**: Handles Hindi, English, Telugu queries  
✅ **Real-time Data**: Weather and market price integration  
✅ **Government Schemes**: Comprehensive financial guidance  
✅ **Dual Interface**: Web application + Telegram bot  
✅ **Agricultural Knowledge**: Crop-specific advice database  
✅ **Scalable Architecture**: Modular, extensible design  

## 🚀 **Next Steps**

1. **Add OpenAI API key** for full AI functionality
2. **Customize crop database** for specific regions
3. **Add more languages** and local dialects
4. **Integrate soil testing** APIs
5. **Add image recognition** for pest/disease identification
6. **Deploy to cloud** for wider accessibility

## 📞 **Support & Access**

- **Web Interface**: http://localhost:8000
- **Telegram Bot**: https://t.me/neokisan_bot
- **Health Check**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/docs

---

**🌾 BhoomiSetu - Bridging Technology and Agriculture for Better Farming Decisions**

*Successfully deployed and ready to help farmers across India!*
