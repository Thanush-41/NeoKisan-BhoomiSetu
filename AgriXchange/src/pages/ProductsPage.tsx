import React, { useState, useEffect } from 'react';
import { Search, Filter, Grid, List, MapPin, Star } from 'lucide-react';
import { Button, Card, Input, Loader } from '../components/ui';
import { QuantityDialog } from '../components/ui/QuantityDialog';
import { useCart } from '../context/CartContext';
import type { RetailProduct, ProductCategory } from '../types';

// NOTE: If you see GET /uploads/products/temp 500 errors, it means a product image is set to a file that does not exist on disk. This usually happens if a product was created without a real image upload and the backend used a placeholder path. To fix: always use a real placeholder image URL in the backend or handle missing images gracefully in the frontend (see onError fallback in <img> tags).

const categories: { value: ProductCategory; label: string }[] = [
  { value: 'vegetables', label: 'Vegetables' },
  { value: 'fruits', label: 'Fruits' },
  { value: 'grains', label: 'Grains' },
  { value: 'pulses', label: 'Pulses' },
  { value: 'spices', label: 'Spices' },
  { value: 'herbs', label: 'Herbs' },
  { value: 'dairy', label: 'Dairy' },
  { value: 'other', label: 'Other' },
];

export const ProductsPage: React.FC = () => {
  const { addToCart } = useCart();
  const [allProducts, setAllProducts] = useState<RetailProduct[]>([]);
  const [products, setProducts] = useState<RetailProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [priceRange, setPriceRange] = useState({ min: 0, max: 1000 });
  const [sortBy, setSortBy] = useState<'price-asc' | 'price-desc' | 'latest' | 'popular'>('latest');

  // Fetch products from backend (run only once on mount)
  const fetchProducts = async () => {
    try {
      setLoading(true);
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const response = await fetch('https://agrixchange.onrender.com/api/products', { headers });
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          const mappedProducts: RetailProduct[] = data.data.data.map((product: any) => ({
            id: product._id,
            name: product.name,
            category: product.category,
            description: product.description || '',
            images: product.images || ['https://images.unsplash.com/photo-1546470427-e5f5e7e7ff34?w=150&h=150&fit=crop'],
            farmerId: product.farmerId._id || product.farmerId,
            farmer: {
              id: product.farmerId._id || product.farmerId,
              name: product.farmerId.name || 'Unknown Farmer',
              phone: product.farmerId.phone || '',
              role: 'farmer',
              address: product.location?.address || '',
              createdAt: new Date(),
              updatedAt: new Date(),
              verificationStatus: 'verified' as const,
            },
            location: product.location || { latitude: 0, longitude: 0, address: '' },
            type: product.type,
            price: product.price || product.startingPrice || 0,
            unit: product.unit || '',
            quantity: product.quantity || 0,
            isActive: true,
            createdAt: new Date(product.createdAt),
            updatedAt: new Date(product.updatedAt),
            ratings: product.ratings || [],
            averageRating: product.averageRating || 0,
          }));
          setAllProducts(mappedProducts);
        } else {
          setAllProducts([]);
        }
      } else {
        setAllProducts([]);
      }
    } catch (error) {
      setAllProducts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Simulated auth context (replace with real auth context if available)
  const user = JSON.parse(localStorage.getItem('agrixchange_user') || 'null');
  const token = localStorage.getItem('agrixchange_token');
  const userId = user?.id;
  const isFarmerUser = user && user.role === 'farmer';

  // DEBUG: Log cart context items to verify cart state
  const { items: cartItems } = useCart();
  useEffect(() => {
    console.log('Cart items:', cartItems);
  }, [cartItems]);

  // Remove "My Products" category logic
  const categoriesWithMyProducts = categories;

  useEffect(() => {
    // Filter and sort products
    let filteredProducts = [...allProducts];

    if (searchQuery) {
      filteredProducts = filteredProducts.filter(product =>
        product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Fix: farmerId may be an object or string, always compare as string
    if (selectedCategory) {
      filteredProducts = filteredProducts.filter(product => product.category === selectedCategory);
    }

    filteredProducts = filteredProducts.filter(
      product => product.price >= priceRange.min && product.price <= priceRange.max
    );

    // Sort products
    filteredProducts.sort((a, b) => {
      switch (sortBy) {
        case 'price-asc':
          return a.price - b.price;
        case 'price-desc':
          return b.price - a.price;
        case 'latest':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        default:
          return 0;
      }
    });

    setProducts(filteredProducts);
  }, [allProducts, searchQuery, selectedCategory, priceRange, sortBy, isFarmerUser, userId]);

  const getImageUrl = (imgPath: string) => {
    if (!imgPath) return 'https://images.unsplash.com/photo-1546470427-e5f5e7e7ff34?w=150&h=150&fit=crop';
    if (imgPath.startsWith('http')) return imgPath;
    // Prepend backend URL for relative paths
    return `https://agrixchange.onrender.com/${imgPath}`;
  };

  // ProductCard now accepts handlers as props
  const ProductCard: React.FC<{
    product: RetailProduct;
  }> = ({ product }) => {
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [localAvg, setLocalAvg] = useState<number | undefined>(product.averageRating);
    const [showQtyDialog, setShowQtyDialog] = useState(false);
    const [qty, setQty] = useState(product.minOrderQuantity);
    const [hoveredStar, setHoveredStar] = useState<number | null>(null);

    const userRating = product.ratings?.find((r: any) => r.userId === userId);

    const handleAddToCart = () => {
      setShowQtyDialog(true);
    };

    const handleConfirmAdd = async () => {
      await addToCart(product, qty);
      setShowQtyDialog(false);
      setQty(product.minOrderQuantity);
      // Do not call fetchProducts here
    };

    const handleStarClick = async (val: number) => {
      if (!token) return;
      setSubmitting(true);
      setError(null);
      try {
        const res = await fetch(`https://agrixchange.onrender.com/api/products/${product.id}/rate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ value: val }),
        });
        const data = await res.json();
        if (res.ok && data.success) {
          setLocalAvg(data.data.averageRating);
          setSubmitting(false);
        } else {
          setError(data.message || 'Failed to submit rating');
        }
      } catch (e) {
        setError('Failed to submit rating');
      } finally {
        setSubmitting(false);
      }
    };

    return (
      <Card hover className="overflow-hidden">
        <div className="aspect-w-16 aspect-h-9">
          <img
            src={getImageUrl(product.images[0])}
            alt={product.name}
            className="w-full h-48 object-cover"
            onError={e => {
              // Only set src to empty string once to prevent repeated fetches
              const img = e.target as HTMLImageElement;
              if (img.src && !img.dataset.failed) {
                img.src = '';
                img.dataset.failed = 'true';
              }
            }}
          />
        </div>
        <div className="p-4">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
            <span className="text-xl font-bold text-primary-600">₹{product.price}/{product.unit}</span>
          </div>
          <p className="text-gray-600 text-sm mb-3">{product.description}</p>
          <div className="flex items-center space-x-2 mb-3">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">{product.location.address}</span>
          </div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-primary-600">
                  {product.farmer.name.charAt(0)}
                </span>
              </div>
              <span className="text-sm text-gray-600">{product.farmer.name}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="text-sm text-gray-600">{(localAvg ?? 0).toFixed(1)}</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mb-1">In Stock: {product.quantity} {product.unit}</p>
          {/* Rating input for users (not farmer, must be logged in) */}
          {user && !isFarmerUser && (
            <div className="mb-2">
              <div className="flex items-center space-x-1">
                {[1,2,3,4,5].map(val => (
                  <button
                    key={val}
                    type="button"
                    aria-label={`Rate ${val} star${val > 1 ? 's' : ''}`}
                    className={`focus:outline-none transition-colors duration-100 ${
                      (hoveredStar !== null ? hoveredStar >= val : (userRating ? userRating.value >= val : (localAvg ?? 0) >= val))
                        ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                    onMouseEnter={() => setHoveredStar(val)}
                    onMouseLeave={() => setHoveredStar(null)}
                    onClick={() => handleStarClick(val)}
                    disabled={submitting || !!userRating}
                    style={{ fontSize: 20, cursor: submitting || !!userRating ? 'not-allowed' : 'pointer' }}
                  >
                    <Star className="w-5 h-5 fill-current" />
                  </button>
                ))}
                {userRating && (
                  <span className="ml-2 text-xs text-green-600">Your rating: {userRating.value}</span>
                )}
              </div>
              {error && <div className="text-xs text-red-600 mt-1">{error}</div>}
            </div>
          )}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Min order: {product.minOrderQuantity} {product.unit}</span>
            {!isFarmerUser && (
              <Button size="sm" onClick={handleAddToCart}>Add to Cart</Button>
            )}
          </div>
          {/* In manage mode, show Edit and Remove buttons for farmer's own products */}
          {/* Edit and Remove buttons removed as per latest requirements */}
        </div>
        {/* Quantity selection dialog */}
        {showQtyDialog && (
          <QuantityDialog
            open={showQtyDialog}
            min={product.minOrderQuantity}
            max={product.quantity}
            value={qty}
            onChange={setQty}
            onClose={() => setShowQtyDialog(false)}
            onConfirm={handleConfirmAdd}
          />
        )}
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Fresh Products</h1>
          <p className="text-gray-600">Discover fresh produce directly from verified farmers</p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <Input
                placeholder="Search for products..."
                leftIcon={<Search className="w-5 h-5" />}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <div className="w-full lg:w-48">
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                {categoriesWithMyProducts.map((category: any) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort */}
            <div className="w-full lg:w-48">
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              >
                <option value="latest">Latest First</option>
                <option value="price-asc">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
                <option value="popular">Most Popular</option>
              </select>
            </div>

            {/* View Toggle */}
            <div className="flex border border-gray-300 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-3 ${viewMode === 'grid' ? 'bg-primary-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-3 ${viewMode === 'list' ? 'bg-primary-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>

            {/* Filter Toggle */}
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="w-5 h-5 mr-2" />
              Filters
            </Button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price Range (₹)
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      placeholder="Min"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                      value={priceRange.min}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, min: Number(e.target.value) }))}
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                      value={priceRange.max}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, max: Number(e.target.value) }))}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <Input placeholder="Enter location..." />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quality Rating
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500">
                    <option value="">Any Rating</option>
                    <option value="4">4+ Stars</option>
                    <option value="3">3+ Stars</option>
                    <option value="2">2+ Stars</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="flex justify-between items-center mb-6">
          <p className="text-gray-600">
            Showing {products.length} of {allProducts.length} products
          </p>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Loader size="lg" />
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map(product => (
              <ProductCard
                key={product.id}
                product={product}
              />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {products.map(product => (
              <Card key={product.id} className="flex flex-col lg:flex-row overflow-hidden">
                <div className="lg:w-1/3">
                  <img
                    src={getImageUrl(product.images[0])}
                    alt={product.name}
                    className="w-full h-48 lg:h-full object-cover"
                    onError={e => {
                      (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1546470427-e5f5e7e7ff34?w=150&h=150&fit=crop';
                    }}
                  />
                </div>
                <div className="flex-1 p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{product.name}</h3>
                      <p className="text-gray-600 mb-2">{product.description}</p>
                      <div className="flex items-center space-x-2 mb-2">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{product.location.address}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-primary-600">
                            {product.farmer.name.charAt(0)}
                          </span>
                        </div>
                        <span className="text-sm text-gray-600">{product.farmer.name}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary-600 mb-2">
                        ₹{product.price}/{product.unit}
                      </div>
                      <div className="flex items-center space-x-1 mb-4">
                        <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        <span className="text-sm text-gray-600">4.5</span>
                      </div>
                      <Button>Add to Cart</Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Empty State */}
        {products.length === 0 && !loading && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Search className="w-16 h-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your search criteria or filters</p>
            <Button onClick={() => {
              setSearchQuery('');
              setSelectedCategory('');
              setPriceRange({ min: 0, max: 1000 });
            }}>
              Clear Filters
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
