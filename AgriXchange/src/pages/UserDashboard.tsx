import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShoppingBag, 
  Clock, 
  MapPin, 
  Star,
  Package,
  TrendingUp
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { Card, Button } from '../components/ui';

export const UserDashboard: React.FC = () => {
  const { user } = useAuth();
  const { totalItems, totalAmount } = useCart();

  // Mock data for user's recent orders
  const recentOrders = [
    {
      id: 'order1',
      date: '2024-01-15',
      items: 3,
      total: 450,
      status: 'delivered',
      farmer: 'Ravi Kumar',
    },
    {
      id: 'order2',
      date: '2024-01-12',
      items: 2,
      total: 320,
      status: 'shipped',
      farmer: 'Priya Sharma',
    },
  ];

  const recommendedProducts = [
    {
      id: '1',
      name: 'Fresh Tomatoes',
      price: 40,
      unit: 'kg',
      farmer: 'Ravi Kumar',
      image: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80',
    },
    {
      id: '2',
      name: 'Organic Rice',
      price: 120,
      unit: 'kg',
      farmer: 'Priya Sharma',
      image: 'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name}! 👋
          </h1>
          <p className="text-gray-600">
            Discover fresh produce from local farmers and manage your orders
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <ShoppingBag className="w-8 h-8 text-primary-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{totalItems}</div>
            <div className="text-sm text-gray-600">Items in Cart</div>
            <div className="text-lg font-semibold text-primary-600 mt-1">₹{totalAmount}</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Package className="w-8 h-8 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{recentOrders.length}</div>
            <div className="text-sm text-gray-600">Recent Orders</div>
            <div className="text-sm text-blue-600 mt-1">View All</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Star className="w-8 h-8 text-yellow-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">4.8</div>
            <div className="text-sm text-gray-600">Avg Rating</div>
            <div className="text-sm text-yellow-600 mt-1">Excellent</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center mb-2">
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">₹{recentOrders.reduce((sum, order) => sum + order.total, 0)}</div>
            <div className="text-sm text-gray-600">Total Spent</div>
            <div className="text-sm text-green-600 mt-1">This Month</div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Orders */}
          <div className="lg:col-span-2">
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Recent Orders</h2>
                <Link to="/orders" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View All
                </Link>
              </div>

              <div className="space-y-4">
                {recentOrders.map((order) => (
                  <div key={order.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                        <Package className="w-6 h-6 text-primary-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">Order #{order.id}</div>
                        <div className="text-sm text-gray-600">{order.items} items • ₹{order.total}</div>
                        <div className="text-sm text-gray-500">From {order.farmer}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                        order.status === 'delivered' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {order.status}
                      </div>
                      <div className="text-sm text-gray-500 mt-1">{order.date}</div>
                    </div>
                  </div>
                ))}
              </div>

              {recentOrders.length === 0 && (
                <div className="text-center py-8">
                  <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
                  <p className="text-gray-600 mb-4">Start shopping to see your orders here</p>
                  <Link to="/products">
                    <Button>Browse Products</Button>
                  </Link>
                </div>
              )}
            </Card>
          </div>

          {/* Quick Actions & Recommendations */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <Link to="/products" className="block">
                  <Button fullWidth variant="outline" className="justify-start">
                    <ShoppingBag className="w-5 h-5 mr-3" />
                    Browse Products
                  </Button>
                </Link>
                <Link to="/cart" className="block">
                  <Button fullWidth variant="outline" className="justify-start">
                    <Package className="w-5 h-5 mr-3" />
                    View Cart ({totalItems})
                  </Button>
                </Link>
                <Link to="/orders" className="block">
                  <Button fullWidth variant="outline" className="justify-start">
                    <Clock className="w-5 h-5 mr-3" />
                    Order History
                  </Button>
                </Link>
                <Link to="/profile" className="block">
                  <Button fullWidth variant="outline" className="justify-start">
                    <MapPin className="w-5 h-5 mr-3" />
                    Delivery Addresses
                  </Button>
                </Link>
              </div>
            </Card>

            {/* Recommended Products */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommended for You</h2>
              <div className="space-y-4">
                {recommendedProducts.map((product) => (
                  <div key={product.id} className="flex items-center space-x-3">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-16 h-16 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{product.name}</div>
                      <div className="text-sm text-gray-600">By {product.farmer}</div>
                      <div className="text-primary-600 font-semibold">₹{product.price}/{product.unit}</div>
                    </div>
                    <Button size="sm">Add</Button>
                  </div>
                ))}
              </div>
              <Link to="/products" className="block mt-4">
                <Button fullWidth variant="outline">View More Products</Button>
              </Link>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
