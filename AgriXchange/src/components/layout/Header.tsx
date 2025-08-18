import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, User, Menu, X, Sprout, ArrowLeft } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import { Button } from '../ui';

export const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { totalItems } = useCart();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMenuOpen(false);
  };

  const getDashboardLink = () => {
    if (!user) return '/';
    
    switch (user.role) {
      case 'farmer':
        return '/farmer/dashboard';
      case 'trader':
        return '/trader/dashboard';
      case 'user':
        return '/user/dashboard';
      default:
        return '/';
    }
  };

  const renderNavLinks = () => {
    if (!isAuthenticated) {
      return (
        <div className="flex items-center space-x-4">
          <Link to="/products" className="text-gray-600 hover:text-primary-600 transition-colors">
            Products
          </Link>
          <Link to="/bidding" className="text-gray-600 hover:text-primary-600 transition-colors">
            Live Bidding
          </Link>
          <Link to="/signin" className="text-gray-600 hover:text-primary-600 transition-colors">
            Sign In
          </Link>
          <Link to="/signup">
            <Button size="sm">Get Started</Button>
          </Link>
        </div>
      );
    }

    // Common links for authenticated users
    const commonLinks = (
      <>
        {/* <Link to="/products" className="text-gray-600 hover:text-primary-600 transition-colors">
          Products
        </Link>
        <Link to="/bidding" className="text-gray-600 hover:text-primary-600 transition-colors">
          Live Bidding
        </Link> */}
      </>
    );

    // Role-specific links
    if (user?.role === 'user') {
      return (
        <div className="flex items-center space-x-4">
          {commonLinks}
         <Link to="/products" className="text-gray-600 hover:text-primary-600 transition-colors">
          Products
        </Link>

          <Link to="/cart" className="relative text-gray-600 hover:text-primary-600 transition-colors">
            <ShoppingCart className="w-6 h-6" />
            {totalItems > 0 && (
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {totalItems}
              </span>
            )}
          </Link>
          <div className="relative">
            <button
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
              onClick={() => setIsProfileMenuOpen((open) => !open)}
              aria-haspopup="true"
              aria-expanded={isProfileMenuOpen}
              tabIndex={0}
              type="button"
            >
              <User className="w-6 h-6" />
              <span className="hidden md:block">{user.name}</span>
            </button>
            {isProfileMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
                <Link to={getDashboardLink()} className="block px-4 py-2 text-gray-700 hover:bg-gray-100" onClick={() => setIsProfileMenuOpen(false)}>
                  Dashboard
                </Link>
                <Link to="/profile" className="block px-4 py-2 text-gray-700 hover:bg-gray-100" onClick={() => setIsProfileMenuOpen(false)}>
                  Profile
                </Link>
                <button onClick={() => { handleLogout(); setIsProfileMenuOpen(false); }} className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      );
    }

    if (user?.role === 'farmer') {
      return (
        <div className="flex items-center space-x-4">
          {commonLinks}
   <Link to="/products" className="text-gray-600 hover:text-primary-600 transition-colors">
          Products
        </Link>
        <Link to="/bidding" className="text-gray-600 hover:text-primary-600 transition-colors">
          Live Bidding
        </Link>
          <Link to="/farmer/add-product" className="text-gray-600 hover:text-primary-600 transition-colors">
            Add Product
          </Link>
          <Link to="/weather" className="text-gray-600 hover:text-primary-600 transition-colors">
            Weather
          </Link>
          <Link to="/news" className="text-gray-600 hover:text-primary-600 transition-colors">
            News
          </Link>
          <div className="relative">
            <button
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
              onClick={() => setIsProfileMenuOpen((open) => !open)}
              aria-haspopup="true"
              aria-expanded={isProfileMenuOpen}
              tabIndex={0}
              type="button"
            >
              <User className="w-6 h-6" />
              <span className="hidden md:block">{user.name}</span>
            </button>
            {isProfileMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
                <Link to={getDashboardLink()} className="block px-4 py-2 text-gray-700 hover:bg-gray-100" onClick={() => setIsProfileMenuOpen(false)}>
                  Dashboard
                </Link>
                <Link to="/profile" className="block px-4 py-2 text-gray-700 hover:bg-gray-100" onClick={() => setIsProfileMenuOpen(false)}>
                  Profile
                </Link>
                <button onClick={() => { handleLogout(); setIsProfileMenuOpen(false); }} className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      );
    }

    if (user?.role === 'trader') {
      return (
        <div className="flex items-center space-x-4">
          {commonLinks}
                  <Link to="/bidding" className="text-gray-600 hover:text-primary-600 transition-colors">
          Live Bidding
        </Link>
          <Link to="/bidding-history" className="text-gray-600 hover:text-primary-600 transition-colors">
            Bidding History
          </Link>
          <div className="relative">
            <button
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
              onClick={() => setIsProfileMenuOpen((open) => !open)}
              aria-haspopup="true"
              aria-expanded={isProfileMenuOpen}
              tabIndex={0}
              type="button"
            >
              <User className="w-6 h-6" />
              <span className="hidden md:block">{user.name}</span>
            </button>
            {isProfileMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
                <Link to={getDashboardLink()} className="block px-4 py-2 text-gray-700 hover:bg-gray-100" onClick={() => setIsProfileMenuOpen(false)}>
                  Dashboard
                </Link>
                <Link to="/profile" className="block px-4 py-2 text-gray-700 hover:bg-gray-100" onClick={() => setIsProfileMenuOpen(false)}>
                  Profile
                </Link>
                <button onClick={() => { handleLogout(); setIsProfileMenuOpen(false); }} className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-6">
            {/* Back to NeoKisan Button */}
            <a 
              href="https://neokisan-bhoomisetu.onrender.com/" 
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors bg-gray-50 hover:bg-gray-100 px-3 py-2 rounded-lg"
              target="_self"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm font-medium">Back to NeoKisan-BhoomiSetu</span>
            </a>
            
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <Sprout className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">AgriXchange</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {renderNavLinks()}
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-gray-600 hover:text-primary-600"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden bg-white border-t">
          <div className="container mx-auto px-4 py-4 space-y-4">
            {/* Back to NeoKisan Button - Mobile */}
            <a 
              href="https://neokisan-bhoomisetu.onrender.com/" 
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors bg-gray-50 hover:bg-gray-100 px-3 py-2 rounded-lg"
              target="_self"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="font-medium">Back to BhoomiSetu</span>
            </a>
            
            <Link to="/products" className="block text-gray-600 hover:text-primary-600 transition-colors">
              Products
            </Link>
            <Link to="/bidding" className="block text-gray-600 hover:text-primary-600 transition-colors">
              Live Bidding
            </Link>
            
            {isAuthenticated ? (
              <>
                {user?.role === 'user' && (
                  <Link to="/cart" className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors">
                    <ShoppingCart className="w-5 h-5" />
                    <span>Cart ({totalItems})</span>
                  </Link>
                )}
                
                {user?.role === 'farmer' && (
                  <>
                    <Link to="/farmer/add-product" className="block text-gray-600 hover:text-primary-600 transition-colors">
                      Add Product
                    </Link>
                    <Link to="/weather" className="block text-gray-600 hover:text-primary-600 transition-colors">
                      Weather
                    </Link>
                    <Link to="/news" className="block text-gray-600 hover:text-primary-600 transition-colors">
                      News
                    </Link>
                  </>
                )}
                
                {user?.role === 'trader' && (
                  <Link to="/bidding-history" className="block text-gray-600 hover:text-primary-600 transition-colors">
                    Bidding History
                  </Link>
                )}
                
                <Link to={getDashboardLink()} className="block text-gray-600 hover:text-primary-600 transition-colors">
                  Dashboard
                </Link>
                <Link to="/profile" className="block text-gray-600 hover:text-primary-600 transition-colors">
                  Profile
                </Link>
                <button onClick={handleLogout} className="block w-full text-left text-gray-600 hover:text-primary-600 transition-colors">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/signin" className="block text-gray-600 hover:text-primary-600 transition-colors">
                  Sign In
                </Link>
                <Link to="/signup" className="block">
                  <Button size="sm" fullWidth>Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
