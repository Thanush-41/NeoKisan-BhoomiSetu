# AgriXchange 🌾 Extention to BhoomiSetu (https://neokisan-bhoomisetu.onrender.com/)

A comprehensive web application that connects farmers directly with consumers and retailers, eliminating middlemen and ensuring fair prices for agricultural produce.

---

## 🚀 Features

### For Farmers
- **Product Listing**: List produce for both retail and wholesale markets  
- **Live Bidding**: Participate in real-time auctions for wholesale orders  
- **Weather Integration**: Access current weather and forecasts  
- **Agricultural News**: Stay updated with latest farming news and trends  
- **Quality Certification**: Upload AGMARK quality certificates  

### For Traders
- **Wholesale Bidding**: Participate in live auctions for bulk purchases  
- **Bidding History**: Track all previous bids and transactions  
- **Verified Trading**: GSTIN and license verification for trusted trading  

### For Consumers
- **Fresh Produce**: Browse and purchase directly from local farmers  
- **Smart Filtering**: Filter by location, price, category, and quality  
- **Shopping Cart**: Easy cart management and checkout  
- **Delivery Partners**: Choose from available delivery options  

---

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript  
- **Build Tool**: Vite  
- **Styling**: Tailwind CSS  
- **Routing**: React Router v6  
- **State Management**: React Context API  
- **Forms**: React Hook Form + Zod validation  
- **Icons**: Lucide React  
- **Real-time**: Socket.IO (for live bidding)  

---

## 🏗️ Project Structure

src/
├── components/
│ ├── ui/ # Reusable UI components
│ ├── layout/ # Layout components (Header, Footer, Layout)
│ └── forms/ # Form components
├── pages/ # Page components
├── context/ # React Context providers
├── hooks/ # Custom React hooks
├── services/ # API services and utilities
├── types/ # TypeScript type definitions
└── utils/ # Utility functions

yaml
Copy
Edit

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)  
- npm or yarn  

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Thanush-41/AgriXchange.git
cd AgriXchange
Install dependencies


npm install
Start the development server

# Environment Configuration
NODE_ENV=development
PORT=5000

# Database
MONGODB_URI=...
# JWT Secret
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Cloudinary (for image uploads)
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
CLOUDINARY_URL=...

# Weather API (OpenWeatherMap)
WEATHER_API_KEY=...
# News API
NEWS_API_KEY=your-news-api-key

# Cors Origins
CORS_ORIGIN=http://localhost:5173



npm run dev
Open your browser and navigate to:
👉 http://localhost:5173
  ```
📱 User Roles & Authentication
The application supports three user roles:

Farmer → List products, participate in bidding, access weather & news

Trader → Participate in wholesale bidding with verified credentials

Consumer → Browse and purchase retail products

Demo Credentials
Phone: Any 10-digit number

Password: Any 6+ character password

(Authentication is simulated for demo purposes)

🎯 Key Pages
Landing Page – Features overview

Authentication – Sign in/Sign up with role selection

Dashboards – Role-specific dashboards

Product Listing – Advanced filtering and browsing

Live Bidding – Real-time auction interface

Cart & Checkout – Shopping cart + delivery partner selection

Weather – Weather details for farmers

News – Agricultural updates

Profile Management – User profile and settings

🔧 Development Scripts

npm run dev       # Start development server
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
🎨 Design System
Primary Colors: Green (agriculture feel)

Secondary Colors: Yellow/Amber highlights

Typography: Inter font family

Components: Consistent buttons, inputs, and cards

Responsive: Mobile-first responsive design

🌟 Key Features Implementation
Live Bidding System
Real-time updates using Socket.IO

Bidding room management

Automatic bid validation

Winner determination

Role-Based Access
Protected routes by user role

Role-specific navigation and UI

Conditional rendering

Product Management
Image upload simulation

Category-based organization

Location-based filtering

Quality certification handling

🚧 Future Enhancements
Payment gateway integration

Real backend API integration

Mobile app development

Advanced analytics dashboard

Government scheme integration

Multi-language support

📄 License
This project is licensed under the MIT License – see the LICENSE file for details.

🤝 Contributing
Contributions are welcome!
Please feel free to submit a Pull Request.

📞 Support
For questions/support: thanushgarimella@gmail.com


✅ This version removes the stray ESLint config snippet you had at the end and keeps it **clean, copy-paste ready** for your repo.

Do you also want me to create a **badges section** (build, license, PRs welcome, etc.) at the top of the README for a more professional look?



