import React, { useEffect, useState } from 'react';
import { Card, Loader } from '../components/ui';
import { TrendingUp, Clock, User } from 'lucide-react';
import type { WholesaleProduct } from '../types';
import { useAuth } from '../context/AuthContext';

interface BidHistoryItem {
  product: WholesaleProduct;
  amount: number;
  time: string;
  status: 'won' | 'lost' | 'active';
  userId?: string;
}

export const TraderBiddingHistoryPage: React.FC = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState<BidHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    // Simulate API call for demo: filter by user
    setTimeout(() => {
      // Use the actual user id from the logged-in user for mock/demo
      const currentUserId = user?.id || 'trader1';
      const allHistory: BidHistoryItem[] = [
        {
          product: {
            id: '1',
            name: 'Premium Basmati Rice',
            images: ['https://images.unsplash.com/photo-1502741338009-cac2772e18bc?w=400'],
            quantity: 1000,
            unit: 'kg',
            description: 'High quality basmati rice from Punjab.',
            startingPrice: 40000,
            farmer: { name: 'Ravi Kumar' },
          } as WholesaleProduct,
          amount: 42000,
          time: '2025-07-12T14:30:00Z',
          status: 'won',
          userId: currentUserId,
        },
        {
          product: {
            id: '2',
            name: 'Fresh Tomatoes',
            images: ['https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=400'],
            quantity: 500,
            unit: 'kg',
            description: 'Organic tomatoes, hand-picked.',
            startingPrice: 12000,
            farmer: { name: 'Priya Sharma' },
          } as WholesaleProduct,
          amount: 13500,
          time: '2025-07-10T10:00:00Z',
          status: 'lost',
          userId: currentUserId,
        },
        {
          product: {
            id: '3',
            name: 'Wheat Bulk Lot',
            images: ['https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=400'],
            quantity: 2000,
            unit: 'kg',
            description: 'Bulk wheat, best for flour mills.',
            startingPrice: 30000,
            farmer: { name: 'Amit Singh' },
          } as WholesaleProduct,
          amount: 31000,
          time: '2025-07-13T09:00:00Z',
          status: 'active',
          userId: currentUserId,
        },
      ];
      // Only show history for the logged-in trader
      const filtered = user ? allHistory.filter(h => h.userId === currentUserId) : [];
      setHistory(filtered);
      setLoading(false);
    }, 1000);
  }, [user]);

  if (loading) return <Loader text="Loading bidding history..." />;
  if (error) return <div className="text-red-600 text-center py-8">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Bidding History</h1>
        {history.length === 0 ? (
          <div className="text-center py-12">
            <TrendingUp className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No bidding history found</h3>
            <p className="text-gray-600">You haven't participated in any auctions yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {history.map((item, idx) => (
              <Card key={idx} className="overflow-hidden">
                <img
                  src={item.product.images[0]}
                  alt={item.product.name}
                  className="w-full h-40 object-cover"
                />
                <div className="p-4">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{item.product.name}</h3>
                    <span
                      className={
                        'text-xs px-2 py-1 rounded-full font-medium ' +
                        (item.status === 'won'
                          ? 'bg-green-100 text-green-700'
                          : item.status === 'lost'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-yellow-100 text-yellow-700')
                      }
                    >
                      {item.status === 'won' ? 'Won' : item.status === 'lost' ? 'Lost' : 'Active'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-1">Bid Amount: <b>₹{item.amount.toLocaleString()}</b></div>
                  <div className="text-sm text-gray-600 mb-1">Quantity: {item.product.quantity} {item.product.unit}</div>
                  <div className="text-sm text-gray-600 mb-1 flex items-center"><User className="w-4 h-4 mr-1" /> {item.product.farmer?.name}</div>
                  <div className="text-xs text-gray-500 mb-2 flex items-center"><Clock className="w-4 h-4 mr-1" /> {new Date(item.time).toLocaleString()}</div>
                  <div className="text-xs text-gray-500">{item.product.description}</div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TraderBiddingHistoryPage;
