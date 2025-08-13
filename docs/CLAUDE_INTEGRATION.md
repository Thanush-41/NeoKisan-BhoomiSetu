# BhoomiSetu MCP Integration with Claude Desktop

This guide explains how to integrate BhoomiSetu's agricultural AI with Claude Desktop using the Model Context Protocol (MCP).

## 🚀 Quick Setup

### 1. Configure Claude Desktop

Copy the configuration to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bhoomisetu": {
      "command": "python",
      "args": [
        "t:\\BhoomiSetu\\src\\mcp\\mcp_server_claude.py"
      ],
      "env": {
        "PYTHONPATH": "t:\\BhoomiSetu"
      }
    }
  }
}
```

**Note:** Update the path `t:\\BhoomiSetu` to match your actual project location.

### 2. Start Claude Desktop

Restart Claude Desktop after adding the configuration. The BhoomiSetu tools will be automatically loaded.

## 🌾 Available Tools in Claude Desktop

Once integrated, you can use these tools directly in Claude Desktop:

### 1. **Agricultural Chat**
Ask any farming question in natural language:
```
Can you help me with agricultural advice for growing rice in Tamil Nadu?
```

### 2. **Crop Recommendations**
Get AI-powered crop suggestions:
```
What crops should I plant on 5 acres of clay soil in Punjab during winter?
```

### 3. **Disease Detection**
Identify crop diseases and get treatment advice:
```
My tomato plants have yellow leaves and brown spots. What could be wrong?
```

### 4. **Weather Analysis**
Get weather-based farming advice:
```
How will next week's weather affect my wheat harvest in Haryana?
```

### 5. **Market Prices**
Check current commodity prices:
```
What are the current onion prices in Maharashtra?
```

### 6. **Government Schemes**
Get information about agricultural schemes:
```
What government schemes are available for small farmers in Karnataka?
```

## 💬 How to Use in Claude Desktop

### Example Conversations:

**You:** "I need help planning my kharif crops for this season"

**Claude:** I'll help you plan your kharif crops! Let me gather some agricultural advice for you.

*[Claude will automatically use the crop_recommendation tool]*

**You:** "My cotton plants are showing signs of disease - leaves are turning yellow and there are small brown spots"

**Claude:** Let me analyze those symptoms for you.

*[Claude will use the disease_detection tool to identify the issue]*

### Natural Language Integration

The beauty of MCP integration is that you can ask questions naturally, and Claude will:
1. Understand your agricultural query
2. Automatically select the appropriate BhoomiSetu tool
3. Call the tool with the right parameters
4. Present the results in a clear, conversational way

## 🔧 Features

### Multilingual Support
- Ask questions in English, Hindi, or other Indian languages
- Get responses in your preferred language

### Location-Aware Advice
- Provide your location for region-specific recommendations
- Get weather and market data for your area

### Context-Aware Responses
- Claude remembers your previous questions in the conversation
- Builds on previous advice for better recommendations

### Real-Time Data
- Current weather conditions
- Live market prices
- Latest government scheme information

## 🛠️ Troubleshooting

### Tool Not Appearing
1. Check Claude Desktop config file path
2. Verify Python path in configuration
3. Restart Claude Desktop completely
4. Check console for error messages

### Tool Execution Errors
1. Ensure all dependencies are installed:
   ```bash
   cd t:\BhoomiSetu
   pip install -r requirements.txt
   ```
2. Verify environment variables in `.env` file
3. Check if BhoomiSetu services are properly initialized

### Configuration Issues
1. Use absolute paths in the configuration
2. Ensure Python is in your system PATH
3. Check PYTHONPATH points to BhoomiSetu directory

## 📊 Tool Parameters

### Agricultural Chat
- `message` (required): Your agricultural question
- `language` (optional): Response language (en, hi, te, etc.)
- `location` (optional): Your location
- `crop_type` (optional): Specific crop you're asking about

### Crop Recommendation
- `location` (required): Farm location
- `soil_type`: Type of soil (clay, sandy, loamy)
- `season`: Current season (kharif, rabi, summer)
- `farm_size`: Farm size in acres
- `budget`: Available budget in INR
- `irrigation_type`: Irrigation method

### Disease Detection
- `crop_type` (required): Type of crop
- `symptoms` (required): List of observed symptoms
- `location`: Location where crop is grown
- `weather_conditions`: Current weather

## 🌟 Tips for Best Results

1. **Be Specific**: Include your location, crop type, and current season
2. **Describe Symptoms Clearly**: For disease detection, list all visible symptoms
3. **Mention Your Context**: Farm size, soil type, irrigation availability
4. **Ask Follow-up Questions**: Build on previous responses for detailed advice

## 🔗 Integration Benefits

- **Seamless Experience**: No need to switch between applications
- **Natural Conversation**: Ask questions as you would to an agricultural expert
- **Comprehensive Advice**: Access to weather, market, and scheme data in one place
- **Multilingual Support**: Get advice in your preferred language
- **Real-time Data**: Always up-to-date information

## 📝 Example Usage Scenarios

### Season Planning
"I have 10 acres in Punjab. Help me plan what to grow this rabi season considering soil type and market prices."

### Problem Solving
"My rice crop is facing some issues - the leaves are yellowing and growth seems stunted. The weather has been very humid lately."

### Market Intelligence
"I'm planning to sell my wheat harvest next month. What are the current market trends and prices?"

### Government Support
"I'm a small farmer in Andhra Pradesh. What government schemes can help me with irrigation setup?"

The MCP integration makes BhoomiSetu's agricultural intelligence available directly within Claude Desktop, providing you with expert farming advice through natural conversation! 🌾
