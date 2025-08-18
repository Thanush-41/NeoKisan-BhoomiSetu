import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Loader } from '../components/ui';
import { Package, Clock, CheckCircle, XCircle, Truck } from 'lucide-react';

interface Order {
  id: string;
  orderNumber: string;
  date: string;
  total: number;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  items: Array<{
    id: string;
    name: string;
    quantity: number;
    price: number;
    image: string;
  }>;
  deliveryAddress: string;
  paymentMethod: string;
}

const statusConfig = {
  pending: { icon: Clock, color: 'text-yellow-600 bg-yellow-50', label: 'Pending' },
  confirmed: { icon: CheckCircle, color: 'text-blue-600 bg-blue-50', label: 'Confirmed' },
  shipped: { icon: Truck, color: 'text-purple-600 bg-purple-50', label: 'Shipped' },
  delivered: { icon: CheckCircle, color: 'text-green-600 bg-green-50', label: 'Delivered' },
  cancelled: { icon: XCircle, color: 'text-red-600 bg-red-50', label: 'Cancelled' },
};

export const OrdersPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  useEffect(() => {
    if (isAuthenticated) {
      fetchOrders();
    }
  }, [isAuthenticated]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock orders data
      const mockOrders: Order[] = [
        {
          id: '1',
          orderNumber: 'ORD-2025-001',
          date: '2025-01-15',
          total: 2500,
          status: 'delivered',
          items: [
            {
              id: '1',
              name: 'Organic Tomatoes',
              quantity: 5,
              price: 400,
              image: 'https://images.unsplash.com/photo-1546470427-e5f5e7e7ff34?w=100&h=100&fit=crop'
            },
            {
              id: '2',
              name: 'Fresh Spinach',
              quantity: 3,
              price: 300,
              image: 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=100&h=100&fit=crop'
            }
          ],
          deliveryAddress: '123 Main St, City, State, 12345',
          paymentMethod: 'UPI'
        },
        {
          id: '2',
          orderNumber: 'ORD-2025-002',
          date: '2025-01-20',
          total: 1800,
          status: 'shipped',
          items: [
            {
              id: '3',
              name: 'Farm Fresh Carrots',
              quantity: 4,
              price: 450,
              image: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=100&h=100&fit=crop'
            }
          ],
          deliveryAddress: '456 Oak Ave, City, State, 67890',
          paymentMethod: 'Cash on Delivery'
        },
        {
          id: '3',
          orderNumber: 'ORD-2025-003',
          date: '2025-01-25',
          total: 3200,
          status: 'pending',
          items: [
            {
              id: '4',
              name: 'Premium Basmati Rice',
              quantity: 2,
              price: 1600,
              image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=100&h=100&fit=crop'
            }
          ],
          deliveryAddress: '789 Pine Rd, City, State, 54321',
          paymentMethod: 'Credit Card'
        }
      ];

      setOrders(mockOrders);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = orders.filter(order => 
    selectedStatus === 'all' || order.status === selectedStatus
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Please Sign In</h1>
          <p className="text-gray-600 mb-8">You need to be logged in to view your orders.</p>
          <Button onClick={() => window.location.href = '/signin'}>
            Sign In
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
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Orders</h1>
        <div className="flex items-center space-x-4">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="all">All Orders</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="shipped">Shipped</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {filteredOrders.length === 0 ? (
        <Card className="p-8 text-center">
          <Package className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Orders Found</h3>
          <p className="text-gray-600 mb-6">
            {selectedStatus === 'all' 
              ? "You haven't placed any orders yet."
              : `No orders found with status: ${selectedStatus}`
            }
          </p>
          <Button onClick={() => window.location.href = '/products'}>
            Start Shopping
          </Button>
        </Card>
      ) : (
        <div className="space-y-6">
          {filteredOrders.map((order) => {
            const StatusIcon = statusConfig[order.status].icon;
            return (
              <Card key={order.id} className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4">
                  <div className="flex items-center space-x-4 mb-4 lg:mb-0">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Order #{order.orderNumber}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Placed on {formatDate(order.date)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusConfig[order.status].color}`}>
                      <StatusIcon className="w-4 h-4 mr-1" />
                      {statusConfig[order.status].label}
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900">
                        {formatCurrency(order.total)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {order.items.length} item{order.items.length !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex items-center space-x-4 py-3 border-b border-gray-100 last:border-b-0">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{item.name}</h4>
                        <p className="text-sm text-gray-600">
                          Quantity: {item.quantity} kg
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">
                          {formatCurrency(item.price)}
                        </p>
                        <p className="text-sm text-gray-600">
                          per kg
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-2 sm:space-y-0">
                    <div className="text-sm text-gray-600">
                      <p><strong>Delivery Address:</strong> {order.deliveryAddress}</p>
                      <p><strong>Payment Method:</strong> {order.paymentMethod}</p>
                    </div>
                    <div className="flex space-x-3">
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                      {order.status === 'pending' && (
                        <Button variant="outline" size="sm" className="text-red-600 border-red-600 hover:bg-red-50">
                          Cancel Order
                        </Button>
                      )}
                      {order.status === 'delivered' && (
                        <Button variant="outline" size="sm">
                          Reorder
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
