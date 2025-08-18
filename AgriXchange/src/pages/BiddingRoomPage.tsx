import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Button, Input, Loader } from '../components/ui';
import { TrendingUp, Users, Send } from 'lucide-react';
import { getSocket } from '../utils/socket';

interface Bid {
  _id: string;
  amount: number;
  trader: { _id: string; name: string };
  timestamp: string;
}

const BiddingRoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const [room, setRoom] = useState<any>(null);
  const [bids, setBids] = useState<Bid[]>([]);
  const [bidAmount, setBidAmount] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [placingBid, setPlacingBid] = useState(false);
  const socketRef = useRef<any>(null);
  const user = JSON.parse(localStorage.getItem('agrixchange_user') || 'null');
  const token = localStorage.getItem('agrixchange_token');

  useEffect(() => {
    if (!roomId) return;
    setLoading(true);
    fetch(`https://agrixchange.onrender.com/api/bidding/room/${roomId}`)
      .then(res => res.json())
      .then(data => {
        if (data.success && data.data) {
          setRoom(data.data);
          setBids(data.data.bids || []);
        } else {
          setError(data.message || 'Failed to load bidding room');
        }
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load bidding room');
        setLoading(false);
      });
  }, [roomId]);

  useEffect(() => {
    if (!roomId || !token) return;
    const socket = getSocket(token);
    socketRef.current = socket;
    socket.emit('authenticate', token);
    socket.once('authenticated', () => {
      socket.emit('join-bidding-room', roomId);
    });
    socket.on('bid-placed', async (bid: any) => {
      // Prevent duplicate bid in history
      setBids(prev => prev.some(b => b._id === bid._id) ? prev : [
        {
          _id: bid._id,
          amount: bid.amount,
          trader: bid.trader || bid.traderId,
          timestamp: bid.timestamp,
        },
        ...prev
      ]);
      // Fetch latest room data to update currentHighestBid and all fields
      if (roomId) {
        try {
          const res = await fetch(`https://agrixchange.onrender.com/api/bidding/room/${roomId}`);
          const data = await res.json();
          if (data.success && data.data) {
            setRoom(data.data);
          }
        } catch {}
      }
    });
    socket.on('bidding-ended', ({ winningBid }: any) => {
      setRoom((prev: any) => prev ? { ...prev, isActive: false, winningBid } : prev);
    });
    socket.on('error', (msg: string) => {
      setError(msg);
    });
    return () => {
      socket.emit('leave-bidding-room', roomId);
      socket.disconnect();
    };
  }, [roomId, token]);

  const handlePlaceBid = () => {
    if (!user || !token) {
      setError('Please log in as a trader to place a bid.');
      return;
    }
    if (!bidAmount || isNaN(Number(bidAmount))) {
      setError('Enter a valid bid amount.');
      return;
    }
    setPlacingBid(true);
    setError('');
    socketRef.current.emit('place-bid', { roomId, amount: Number(bidAmount) });
    socketRef.current.once('error', (msg: string) => {
      setError(msg);
      setPlacingBid(false);
    });
    socketRef.current.once('bid-placed', () => {
      setBidAmount('');
      setPlacingBid(false);
    });
  };

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen"><Loader size="lg" /></div>;
  }
  if (error) {
    return <div className="flex justify-center items-center min-h-screen text-red-600">{error}</div>;
  }
  if (!room) {
    return <div className="flex justify-center items-center min-h-screen">Bidding room not found.</div>;
  }

  const product = room.productId;
  const isActive = room.isActive;
  const highestBid = room.currentHighestBid?.amount || product.startingPrice;
  const timeLeft = (() => {
    if (!isActive) return 'Ended';
    const end = new Date(room.endTime);
    const now = new Date();
    const diff = end.getTime() - now.getTime();
    if (diff <= 0) return 'Ended';
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    return `${h}h ${m}m`;
  })();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        <Card className="mb-8 p-6">
          <div className="flex flex-col md:flex-row gap-6 items-center">
            <img src={product.images?.[0]} alt={product.name} className="w-40 h-40 object-cover rounded-lg border" />
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">{product.name}</h2>
              <div className="flex flex-wrap gap-4 mb-2 text-gray-600 text-sm">
                <span>Quantity: <b>{product.quantity} {product.unit}</b></span>
                <span>By: <b>{(product.farmerId as any)?.name || 'Unknown'}</b></span>
                <span>Ends in: <b>{timeLeft}</b></span>
                <span>Status: <b className={isActive ? 'text-green-600' : 'text-red-600'}>{isActive ? 'Active' : 'Ended'}</b></span>
              </div>
              <div className="flex gap-8 mb-2">
                <span className="flex items-center gap-1"><TrendingUp className="w-4 h-4" /> {bids.length} bids</span>
                <span className="flex items-center gap-1"><Users className="w-4 h-4" /> {room.participants?.length || 0} bidders</span>
              </div>
              <div className="flex gap-8 mb-2">
                <span>Starting Price: <b>₹{product.startingPrice.toLocaleString()}</b></span>
                <span>Highest Bid: <b className="text-primary-600">₹{highestBid.toLocaleString()}</b></span>
              </div>
              {room.winningBid && !isActive && (
                <div className="mt-2 text-green-700 font-semibold">Winning Bid: ₹{room.winningBid.amount.toLocaleString()} by {room.winningBid.trader?.name || 'Unknown'}</div>
              )}
            </div>
          </div>
        </Card>
        <Card className="p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4">Place Your Bid</h3>
          {isActive ? (
            <div className="flex gap-2 items-center">
              <Input
                type="number"
                min={highestBid + 1}
                value={bidAmount}
                onChange={e => setBidAmount(e.target.value)}
                placeholder={`Min ₹${highestBid + 1}`}
                className="w-40"
                disabled={placingBid}
              />
              <Button onClick={handlePlaceBid} disabled={placingBid}>
                <Send className="w-4 h-4 mr-1" /> Place Bid
              </Button>
              {placingBid && <Loader size="sm" />}
            </div>
          ) : (
            <div className="text-gray-500">Bidding has ended.</div>
          )}
          {error && <div className="text-red-600 mt-2">{error}</div>}
        </Card>
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Bid History</h3>
          <div className="max-h-72 overflow-y-auto divide-y">
            {bids.length === 0 && <div className="text-gray-500">No bids yet.</div>}
            {bids.map(bid => (
              <div key={bid._id} className="flex justify-between items-center py-2">
                <div>
                  <span className="font-medium">₹{bid.amount.toLocaleString()}</span>
                  <span className="ml-2 text-gray-500 text-sm">by {bid.trader?.name || 'Unknown'}</span>
                </div>
                <div className="text-xs text-gray-400">{new Date(bid.timestamp).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default BiddingRoomPage;
