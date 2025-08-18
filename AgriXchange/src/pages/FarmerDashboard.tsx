import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Loader } from '../components/ui';
import { 
  Sprout, 
  Package, 
  TrendingUp, 
  Calendar, 
  MapPin,
  Phone,
  Mail,
  Edit,
  Plus,
  Eye
} from 'lucide-react';

interface Product {
  id: string;
  name: string;
  category: string;
  quantity: number;
  price: number;
  unit: string; // Add unit field
  status: 'active' | 'sold' | 'expired';
  type: 'retail' | 'wholesale';
  image: string;
  createdAt: string;
}

export const FarmerDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalProducts: 0,
    activeListings: 0,
    totalRevenue: 0,
    pendingOrders: 0
  });

  useEffect(() => {
    if (isAuthenticated && user?.role === 'farmer') {
      fetchDashboardData();
    }
  }, [isAuthenticated, user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch real products from backend
      const token = localStorage.getItem('agrixchange_token');
      const response = await fetch('https://agrixchange.onrender.com/api/products/my/products', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Fetched products:', data);
        
        if (data.success && data.data) {
          // Map backend products to frontend format
          const mappedProducts: Product[] = data.data.data.map((product: any) => ({
            id: product._id,
            name: product.name,
            category: product.category,
            quantity: product.quantity,
            price: product.price || product.startingPrice || 0,
            unit: product.unit || 'kg', // Map unit from backend, fallback to 'kg'
            status: 'active', // You might want to add status field to backend
            type: product.type,
            image: product.images?.[0] || 'https://images.unsplash.com/photo-1546470427-e5f5e7e7ff34?w=150&h=150&fit=crop',
            createdAt: new Date(product.createdAt).toISOString().split('T')[0]
          }));

          setProducts(mappedProducts);
          setStats({
            totalProducts: mappedProducts.length,
            activeListings: mappedProducts.filter(p => p.status === 'active').length,
            totalRevenue: 0, // Calculate from orders if available
            pendingOrders: 0 // Fetch from orders API if available
          });
        } else {
          console.warn('No products found or invalid response structure');
          setProducts([]);
        }
      } else {
        console.error('Failed to fetch products:', response.status, response.statusText);
        // Fall back to empty array
        setProducts([]);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Fall back to empty array
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  if (!isAuthenticated || user?.role !== 'farmer') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-8">This page is only accessible to farmers.</p>
          <Button onClick={() => window.location.href = '/signin'}>
            Sign In as Farmer
          </Button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <Loader size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Farmer Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, {user?.name}!</p>
        </div>
        <div className="mt-4 md:mt-0 flex space-x-3">
          <Button variant="outline" className="flex items-center">
            <Edit className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
          <Button className="flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            Add Product
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100">
              <Package className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Products</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalProducts}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100">
              <Sprout className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Listings</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeListings}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100">
              <TrendingUp className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalRevenue)}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Orders</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pendingOrders}</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Products */}
        <div className="lg:col-span-2">
          <Card>
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recent Products</h2>
                <div className="flex space-x-2">
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => navigate('/farmer/add-product')}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Product
                  </Button>
                  <Button variant="outline" size="sm">
                    View All
                  </Button>
                </div>
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {products.map((product) => (
                  <div key={product.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                    <div className="flex items-center space-x-4">
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-12 h-12 object-cover rounded-lg"
                      />
                      <div>
                        <h3 className="font-medium text-gray-900">{product.name}</h3>
                        <p className="text-sm text-gray-600">{product.category} • {product.type}</p>
                        <p className="text-xs text-gray-500">In Stock: {product.quantity} {product.unit}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{formatCurrency(product.price)}/{product.unit}</p>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                          product.status === 'active' 
                            ? 'bg-green-100 text-green-800'
                            : product.status === 'sold'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {product.status}
                        </span>
                        <Button variant="ghost" size="sm">
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>

        {/* Profile & Quick Actions */}
        <div className="space-y-6">
          {/* Profile Summary */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Summary</h2>
            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <MapPin className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-600">{user?.address}</span>
              </div>
              <div className="flex items-center text-sm">
                <Phone className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-600">{user?.phone}</span>
              </div>
              {user?.email && (
                <div className="flex items-center text-sm">
                  <Mail className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-gray-600">{user.email}</span>
                </div>
              )}
            </div>
          </Card>

          {/* Quick Actions */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Button className="w-full justify-start" variant="outline">
                <Plus className="w-4 h-4 mr-2" />
                List New Product
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <TrendingUp className="w-4 h-4 mr-2" />
                View Analytics
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Package className="w-4 h-4 mr-2" />
                Manage Inventory
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Calendar className="w-4 h-4 mr-2" />
                Schedule Delivery
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
