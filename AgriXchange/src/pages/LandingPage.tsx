import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Truck, 
  TrendingUp, 
  Shield, 
  Users, 
  Leaf, 
  BarChart3, 
  ArrowRight,
  CheckCircle
} from 'lucide-react';
import { Button, Card } from '../components/ui';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 to-secondary-50 py-20">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Connect Farmers
                <span className="block text-primary-600">Directly with</span>
                <span className="block text-secondary-600">Markets</span>
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed">
                Eliminate middlemen, get fair prices, and build direct relationships 
                between farmers, traders, and consumers. Join the agricultural revolution.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/signup">
                  <Button size="lg" className="w-full sm:w-auto">
                    Get Started Today
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link to="/products">
                  <Button variant="outline" size="lg" className="w-full sm:w-auto">
                    Browse Products
                  </Button>
                </Link>
              </div>
              <div className="flex items-center space-x-8 pt-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary-600">1000+</div>
                  <div className="text-sm text-gray-600">Active Farmers</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary-600">500+</div>
                  <div className="text-sm text-gray-600">Products Listed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary-600">₹2M+</div>
                  <div className="text-sm text-gray-600">Transactions</div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <img 
                  src="https://images.unsplash.com/photo-1500937386664-56d1dfef3854?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
                  alt="Farmer with fresh produce" 
                  className="w-full h-96 object-cover rounded-xl"
                />
              </div>
              <div className="absolute -bottom-6 -right-6 bg-primary-600 text-white p-4 rounded-xl shadow-lg">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-6 h-6" />
                  <div>
                    <div className="font-semibold">30% Higher</div>
                    <div className="text-sm opacity-90">Farmer Income</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose AgriXchange?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform provides comprehensive solutions for farmers, traders, and consumers 
              to connect, trade, and grow together.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card hover className="text-center">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Truck className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Direct Delivery</h3>
              <p className="text-gray-600">
                Connect with delivery partners and get your produce directly to consumers 
                without multiple intermediaries.
              </p>
            </Card>

            <Card hover className="text-center">
              <div className="bg-secondary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-secondary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Live Bidding</h3>
              <p className="text-gray-600">
                Participate in real-time auctions for wholesale produce and get the best 
                prices for your crops.
              </p>
            </Card>

            <Card hover className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Quality Assured</h3>
              <p className="text-gray-600">
                AGMARK certified quality grading ensures trust and transparency in 
                every transaction.
              </p>
            </Card>

            <Card hover className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Community Driven</h3>
              <p className="text-gray-600">
                Join a community of farmers, traders, and consumers working together 
                for sustainable agriculture.
              </p>
            </Card>

            <Card hover className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Leaf className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Sustainable Farming</h3>
              <p className="text-gray-600">
                Access weather updates, farming news, and government schemes to 
                improve your farming practices.
              </p>
            </Card>

            <Card hover className="text-center">
              <div className="bg-orange-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Better Prices</h3>
              <p className="text-gray-600">
                Eliminate middlemen and get fair prices for your produce while 
                consumers pay reasonable rates.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How AgriXchange Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Simple steps to connect, trade, and grow your agricultural business.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Farmers */}
            <Card>
              <div className="text-center mb-6">
                <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                  1
                </div>
                <h3 className="text-2xl font-semibold text-primary-600 mb-2">For Farmers</h3>
              </div>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Register and verify your farming credentials</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>List your produce for retail or wholesale</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Set prices or start auctions for bulk orders</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Connect directly with buyers</span>
                </li>
              </ul>
            </Card>

            {/* Traders */}
            <Card>
              <div className="text-center mb-6">
                <div className="bg-secondary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                  2
                </div>
                <h3 className="text-2xl font-semibold text-secondary-600 mb-2">For Traders</h3>
              </div>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Register with GSTIN and trading license</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Browse wholesale produce listings</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Participate in live bidding auctions</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Secure best deals directly from farmers</span>
                </li>
              </ul>
            </Card>

            {/* Consumers */}
            <Card>
              <div className="text-center mb-6">
                <div className="bg-green-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                  3
                </div>
                <h3 className="text-2xl font-semibold text-green-600 mb-2">For Consumers</h3>
              </div>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Browse fresh produce from local farmers</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Filter by location, price, and quality</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Add items to cart and place orders</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                  <span>Choose delivery partners and pay directly</span>
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Transform Agriculture?
          </h2>
          <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
            Join thousands of farmers, traders, and consumers who are already 
            benefiting from direct agricultural connections.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                Start Your Journey
              </Button>
            </Link>
            <Link to="/products">
              <Button variant="outline" size="lg" className="w-full sm:w-auto border-white text-white hover:bg-white hover:text-primary-600">
                Explore Products
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
