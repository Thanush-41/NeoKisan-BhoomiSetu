import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { Layout } from './components/layout';
import { LandingPage } from './pages/LandingPage';
import { SignInPage } from './pages/SignInPage';
import { SignUpPage } from './pages/SignUpPage';
import { ProductsPage } from './pages/ProductsPage';
import { LiveBiddingPage } from './pages/LiveBiddingPage';
import { UserDashboard } from './pages/UserDashboard';
import { FarmerDashboard } from './pages/FarmerDashboard';
import { TraderDashboard } from './pages/TraderDashboard';
import { CartPage } from './pages/CartPage';
import { OrdersPage } from './pages/OrdersPage';
import { AddProductPage } from './pages/AddProductPage';
import { ProfilePage } from './pages/ProfilePage';
import BiddingRoomPage from './pages/BiddingRoomPage';
import { TraderBiddingHistoryPage } from './pages/TraderBiddingHistoryPage';

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/signin" element={<SignInPage />} />
              <Route path="/signup" element={<SignUpPage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/orders" element={<OrdersPage />} />
              <Route path="/bidding" element={<LiveBiddingPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/user/dashboard" element={<UserDashboard />} />
              <Route path="/farmer/dashboard" element={<FarmerDashboard />} />
              <Route path="/farmer/add-product" element={<AddProductPage />} />
              <Route path="/trader/dashboard" element={<TraderDashboard />} />
              <Route path="/bidding/:roomId" element={<BiddingRoomPage />} />
              <Route path="/bidding-history" element={<TraderBiddingHistoryPage />} />
              {/* More routes will be added here */}
            </Routes>
          </Layout>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
