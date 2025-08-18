import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Loader } from '../components/ui';
import { 
  TrendingUp, 
  Package, 
  Clock, 
  Trophy,
  MapPin,
  Phone,
  Mail,
  Edit,
  Eye,
  Gavel
} from 'lucide-react';

interface Bid {
  id: string;
  productName: string;
  farmerName: string;
  amount: number;
  status: 'winning' | 'outbid' | 'won' | 'lost';
  timestamp: string;
  endTime: string;
  image: string;
}

export const TraderDashboard: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [bids, setBids] = useState<Bid[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalBids: 0,
    winningBids: 0,
    totalSpent: 0,
    activeBiddings: 0
  });

  useEffect(() => {
    if (isAuthenticated && user?.role === 'trader') {
      fetchDashboardData();
    }
  }, [isAuthenticated, user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // Simulate API call for all bids by this trader
      // In real app, fetch from backend using user.id
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Mock bids data (all biddings for this trader)
      const mockBids: Bid[] = [
        {
          id: '1',
          productName: 'Premium Basmati Rice',
          farmerName: 'Rajesh Kumar',
          amount: 12000,
          status: 'winning',
          timestamp: '2025-01-25T10:30:00Z',
          endTime: '2025-01-26T18:00:00Z',
          image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=150&h=150&fit=crop'
        },
        {
          id: '2',
          productName: 'Organic Wheat',
          farmerName: 'Priya Sharma',
          amount: 8500,
          status: 'outbid',
          timestamp: '2025-01-24T14:20:00Z',
          endTime: '2025-01-25T20:00:00Z',
          image: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=150&h=150&fit=crop'
        },
        {
          id: '3',
          productName: 'Fresh Tomatoes',
          farmerName: 'Amit Patel',
          amount: 4500,
          status: 'won',
          timestamp: '2025-01-23T09:15:00Z',
          endTime: '2025-01-24T16:00:00Z',
          image: 'https://images.unsplash.com/photo-1546470427-e5f5e7e7ff34?w=150&h=150&fit=crop'
        }
      ];
      // In a real app, filter by user.id from backend. For demo, show all mock bids.
      setBids(mockBids);
      setStats({
        totalBids: mockBids.length,
        winningBids: mockBids.filter(b => b.status === 'winning' || b.status === 'won').length,
        totalSpent: 125000,
        activeBiddings: 5
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTimeRemaining = (endTime: string) => {
    const now = new Date();
    const end = new Date(endTime);
    const diff = end.getTime() - now.getTime();
    
    if (diff <= 0) return 'Ended';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }
    
    return `${hours}h ${minutes}m`;
  };

  if (!isAuthenticated || user?.role !== 'trader') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-8">This page is only accessible to traders.</p>
          <Button onClick={() => window.location.href = '/signin'}>
            Sign In as Trader
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
          <h1 className="text-3xl font-bold text-gray-900">Trader Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, {user?.name}!</p>
        </div>
        <div className="mt-4 md:mt-0 flex space-x-3">
          <Button variant="outline" className="flex items-center">
            <Edit className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
          <Button className="flex items-center" onClick={() => window.location.href = '/bidding'}>
            <Gavel className="w-4 h-4 mr-2" />
            View Live Biddings
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100">
              <Gavel className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Bids</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalBids}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100">
              <Trophy className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Winning Bids</p>
              <p className="text-2xl font-bold text-gray-900">{stats.winningBids}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100">
              <TrendingUp className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Spent</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalSpent)}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100">
              <Clock className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Biddings</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeBiddings}</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Bids */}
        <div className="lg:col-span-2">
          <Card>
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recent Bids</h2>
                <Button variant="outline" size="sm">
                  View All
                </Button>
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {bids.map((bid) => (
                  <div key={bid.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                    <div className="flex items-center space-x-4">
                      <img
                        src={bid.image}
                        alt={bid.productName}
                        className="w-12 h-12 object-cover rounded-lg"
                      />
                      <div>
                        <h3 className="font-medium text-gray-900">{bid.productName}</h3>
                        <p className="text-sm text-gray-600">by {bid.farmerName}</p>
                        <p className="text-xs text-gray-500">Bid placed: {formatDate(bid.timestamp)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{formatCurrency(bid.amount)}</p>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                          bid.status === 'winning' 
                            ? 'bg-green-100 text-green-800'
                            : bid.status === 'won'
                            ? 'bg-blue-100 text-blue-800'
                            : bid.status === 'outbid'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {bid.status}
                        </span>
                        <Button variant="ghost" size="sm">
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                      {(bid.status === 'winning' || bid.status === 'outbid') && (
                        <p className="text-xs text-gray-500 mt-1">
                          Ends: {getTimeRemaining(bid.endTime)}
                        </p>
                      )}
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
              <Button className="w-full justify-start" variant="outline" onClick={() => window.location.href = '/bidding'}>
                <Gavel className="w-4 h-4 mr-2" />
                Browse Biddings
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Trophy className="w-4 h-4 mr-2" />
                My Winning Bids
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <TrendingUp className="w-4 h-4 mr-2" />
                View Analytics
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Package className="w-4 h-4 mr-2" />
                Purchase History
              </Button>
            </div>
          </Card>

          {/* Active Biddings */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Biddings</h2>
            <div className="space-y-3">
              <div className="text-center py-6">
                <Clock className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                <p className="text-sm text-gray-600">
                  {stats.activeBiddings} active biddings available
                </p>
                <Button size="sm" className="mt-2" onClick={() => window.location.href = '/bidding'}>
                  View All
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
