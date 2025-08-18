import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Card, Input } from '../components/ui';
import { Upload, X } from 'lucide-react';
import type { ProductCategory } from '../types';

const productSchema = z.object({
  name: z.string().min(1, 'Product name is required'),
  category: z.string().min(1, 'Category is required'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  type: z.enum(['retail', 'wholesale']),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  location: z.object({
    latitude: z.number().min(-90).max(90),
    longitude: z.number().min(-180).max(180),
    address: z.string().min(1, 'Address is required')
  }),
  // Retail specific fields
  price: z.number().min(0.01, 'Price must be greater than 0').optional(),
  unit: z.string().min(1, 'Unit is required').optional(),
  // Wholesale specific fields
  startingPrice: z.number().min(0.01, 'Starting price must be greater than 0').optional(),
  biddingDuration: z.number().min(1, 'Bidding duration must be at least 1 hour').optional(),
  qualityCertificate: z.string().url('Must be a valid URL').optional(),
}).refine((data) => {
  if (data.type === 'retail') {
    return data.price && data.unit;
  }
  // For wholesale, require startingPrice, biddingDuration, unit, qualityCertificate
  return data.startingPrice && data.biddingDuration && data.unit && data.qualityCertificate;
}, {
  message: 'Missing required fields for the selected product type',
  path: ['type'],
});

type ProductFormData = z.infer<typeof productSchema>;

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

export const AddProductPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      type: 'retail',
      unit: 'kg',
      quantity: 1,
      location: {
        latitude: 0,
        longitude: 0,
        address: '',
      },
    },
  });

  const productType = watch('type');

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedImages(prev => [...prev, ...files].slice(0, 5)); // Max 5 images
  };

  const removeImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
  };

  const onSubmit = async (data: ProductFormData) => {
    setIsSubmitting(true);
    try {
      // Build FormData for multipart upload
      const formData = new FormData();
      formData.append('name', data.name);
      formData.append('category', data.category);
      formData.append('description', data.description);
      formData.append('type', data.type);
      formData.append('quantity', String(data.quantity));
      formData.append('unit', data.unit || '');
      formData.append('location', JSON.stringify(data.location));
      if (data.type === 'wholesale') {
        formData.append('startingPrice', String(data.startingPrice));
        formData.append('biddingDuration', String(data.biddingDuration));
        formData.append('qualityCertificate', data.qualityCertificate || '');
      } else if (data.type === 'retail') {
        formData.append('price', String(data.price));
      }
      // Append images
      selectedImages.forEach((file) => {
        formData.append('images', file);
      });
      const response = await fetch('https://agrixchange.onrender.com/api/products', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('agrixchange_token')}`,
        },
        body: formData,
      });

      console.log('Payload sent:', formData);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (response.ok) {
        alert('Product added successfully!');
        navigate('/farmer/dashboard');
      } else {
        let errorText = await response.text();
        let errorMsg = errorText;
        try {
          const error = JSON.parse(errorText);
          errorMsg = error.message || errorText;
        } catch (parseError) {}
        alert(`Failed to add product: ${response.status} ${response.statusText}\n${errorMsg}`);
        console.error('Full error response:', errorText);
      }
    } catch (error) {
      alert('Failed to add product. JS error: ' + (error instanceof Error ? error.message : String(error)));
      console.error('Error adding product:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Add New Product</h1>
          <p className="text-gray-600">List your products for sale</p>
        </div>

        <Card className="p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Product Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product Type
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="retail"
                    {...register('type')}
                    className="mr-2"
                  />
                  Retail (Direct Sale)
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="wholesale"
                    {...register('type')}
                    className="mr-2"
                  />
                  Wholesale (Bidding)
                </label>
              </div>
            </div>

            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Input
                  label="Product Name"
                  id="product-name"
                  autoComplete="off"
                  {...register('name')}
                  error={errors.name?.message}
                  placeholder="e.g., Fresh Tomatoes"
                />
              </div>
              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  id="category"
                  autoComplete="off"
                  {...register('category')}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select Category</option>
                  {categories.map(category => (
                    <option key={category.value} value={category.value}>
                      {category.label}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="text-red-600 text-sm mt-1">{errors.category.message}</p>
                )}
              </div>
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                autoComplete="off"
                {...register('description')}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Describe your product..."
              />
              {errors.description && (
                <p className="text-red-600 text-sm mt-1">{errors.description.message}</p>
              )}
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Input
                    label="Latitude"
                    type="number"
                    step="0.000001"
                    {...register('location.latitude', { valueAsNumber: true })}
                    error={errors.location?.latitude?.message}
                    placeholder="12.9716"
                  />
                </div>
                <div>
                  <Input
                    label="Longitude"
                    type="number"
                    step="0.000001"
                    {...register('location.longitude', { valueAsNumber: true })}
                    error={errors.location?.longitude?.message}
                    placeholder="77.5946"
                  />
                </div>
                <div>
                  <Input
                    label="Address"
                    {...register('location.address')}
                    error={errors.location?.address?.message}
                    placeholder="Farm address"
                  />
                </div>
              </div>
            </div>

            {/* Pricing and Quantity */}
            {productType === 'retail' ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <Input
                    label="Price per Unit"
                    type="number"
                    step="0.01"
                    {...register('price', { valueAsNumber: true })}
                    error={errors.price?.message}
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <Input
                    label="Unit"
                    {...register('unit')}
                    error={errors.unit?.message}
                    placeholder="kg, pieces, etc."
                  />
                </div>
                <div>
                  <Input
                    label="Available Quantity"
                    type="number"
                    {...register('quantity', { valueAsNumber: true })}
                    error={errors.quantity?.message}
                    placeholder="100"
                  />
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Input
                    label="Starting Price"
                    type="number"
                    step="0.01"
                    {...register('startingPrice', { valueAsNumber: true })}
                    error={errors.startingPrice?.message}
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <Input
                    label="Available Quantity"
                    type="number"
                    {...register('quantity', { valueAsNumber: true })}
                    error={errors.quantity?.message}
                    placeholder="100"
                  />
                </div>
                <div>
                  <Input
                    label="Unit"
                    {...register('unit')}
                    error={errors.unit?.message}
                    placeholder="kg, pieces, etc."
                  />
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {productType === 'wholesale' && (
                <div>
                  <Input
                    label="Bidding Duration (hours)"
                    type="number"
                    {...register('biddingDuration', { valueAsNumber: true })}
                    error={errors.biddingDuration?.message}
                    placeholder="24"
                  />
                </div>
              )}
            </div>

            {/* Quality Certificate URL */}
            {productType === 'wholesale' && (
              <div className="mb-4">
                <label htmlFor="qualityCertificate" className="block text-sm font-medium text-gray-700">
                  Quality Certificate (URL)
                </label>
                <input
                  id="qualityCertificate"
                  type="url"
                  {...register('qualityCertificate', { required: 'Quality certificate URL is required' })}
                  name="qualityCertificate"
                  autoComplete="url"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring focus:ring-primary-500 focus:ring-opacity-50"
                  placeholder="https://example.com/cert1.pdf"
                  aria-invalid={!!errors.qualityCertificate}
                  aria-describedby="qualityCertificate-error"
                />
                {errors.qualityCertificate && (
                  <p id="qualityCertificate-error" className="mt-2 text-sm text-red-600">
                    {errors.qualityCertificate.message as string}
                  </p>
                )}
              </div>
            )}

            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product Images (Max 5)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="cursor-pointer flex flex-col items-center justify-center"
                >
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  <p className="text-gray-600">Click to upload images</p>
                  <p className="text-sm text-gray-500">PNG, JPG up to 5MB each</p>
                </label>
                
                {selectedImages.length > 0 && (
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4">
                    {selectedImages.map((image, index) => (
                      <div key={index} className="relative">
                        <img
                          src={URL.createObjectURL(image)}
                          alt={`Preview ${index + 1}`}
                          className="w-full h-24 object-cover rounded-lg"
                        />
                        <button
                          type="button"
                          onClick={() => removeImage(index)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex space-x-4">
              <Button
                type="submit"
                disabled={isSubmitting}
                className="flex-1"
              >
                {isSubmitting ? 'Adding Product...' : 'Add Product'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/farmer/dashboard')}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};
