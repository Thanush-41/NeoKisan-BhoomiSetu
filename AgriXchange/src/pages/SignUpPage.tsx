import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, User, Phone, Mail, MapPin, Building } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button, Input, Card } from '../components/ui';
import type { UserRole } from '../types';

const signUpSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  phone: z.string().min(10, 'Phone number must be at least 10 digits'),
  email: z.string().email('Invalid email address').optional().or(z.literal('')),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
  role: z.enum(['farmer', 'trader', 'user'] as const),
  address: z.string().min(5, 'Address must be at least 5 characters'),
  // Farmer specific
  farmSize: z.string().optional(),
  cropTypes: z.string().optional(),
  // Trader specific
  gstin: z.string().optional(),
  licenseNumber: z.string().optional(),
  companyName: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignUpForm = z.infer<typeof signUpSchema>;

export const SignUpPage: React.FC = () => {
  const { register: registerUser, isLoading } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('user');

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    watch,
    setValue,
  } = useForm<SignUpForm>({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      role: 'user',
    },
  });

  const watchRole = watch('role');

  const onSubmit = async (data: SignUpForm) => {
    try {
      console.log('Form data before sending:', data);
      // Remove confirmPassword before sending to backend
      const { confirmPassword, ...registrationData } = data;
      console.log('Registration data to send:', registrationData);
      await registerUser(registrationData);
      
      // Redirect based on role
      switch (data.role) {
        case 'farmer':
          navigate('/farmer/dashboard');
          break;
        case 'trader':
          navigate('/trader/dashboard');
          break;
        case 'user':
          navigate('/user/dashboard');
          break;
        default:
          navigate('/');
      }
    } catch (error) {
      setError('root', {
        message: error instanceof Error ? error.message : 'Registration failed',
      });
    }
  };

  const handleRoleChange = (role: UserRole) => {
    setSelectedRole(role);
    setValue('role', role); // Update form value
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Join AgriXchange</h2>
          <p className="mt-2 text-sm text-gray-600">
            Create your account to get started
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              I am a:
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'user', label: 'Consumer' },
                { value: 'farmer', label: 'Farmer' },
                { value: 'trader', label: 'Trader' },
              ].map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => handleRoleChange(value as UserRole)}
                  className={`p-3 rounded-lg border text-sm font-medium transition-colors ${
                    selectedRole === value
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            {/* Register the role field properly */}
            <input type="hidden" {...register('role')} />
          </div>

          {/* Basic Information */}
          <Input
            {...register('name')}
            label="Full Name"
            placeholder="Enter your full name"
            leftIcon={<User className="w-5 h-5" />}
            error={errors.name?.message}
          />

          <Input
            {...register('phone')}
            label="Phone Number"
            type="tel"
            placeholder="Enter your phone number"
            leftIcon={<Phone className="w-5 h-5" />}
            error={errors.phone?.message}
          />

          <Input
            {...register('email')}
            label="Email Address (Optional)"
            type="email"
            placeholder="Enter your email address"
            leftIcon={<Mail className="w-5 h-5" />}
            error={errors.email?.message}
          />

          <Input
            {...register('address')}
            label="Address"
            placeholder="Enter your address"
            leftIcon={<MapPin className="w-5 h-5" />}
            error={errors.address?.message}
          />

          {/* Role-specific fields */}
          {watchRole === 'farmer' && (
            <>
              <Input
                {...register('farmSize')}
                label="Farm Size (Optional)"
                placeholder="e.g., 5 acres"
                error={errors.farmSize?.message}
              />
              <Input
                {...register('cropTypes')}
                label="Crop Types (Optional)"
                placeholder="e.g., Rice, Wheat, Vegetables"
                error={errors.cropTypes?.message}
              />
            </>
          )}

          {watchRole === 'trader' && (
            <>
              <Input
                {...register('gstin')}
                label="GSTIN"
                placeholder="Enter your GSTIN"
                leftIcon={<Building className="w-5 h-5" />}
                error={errors.gstin?.message}
              />
              <Input
                {...register('licenseNumber')}
                label="License Number"
                placeholder="Enter your trading license number"
                error={errors.licenseNumber?.message}
              />
              <Input
                {...register('companyName')}
                label="Company Name (Optional)"
                placeholder="Enter your company name"
                error={errors.companyName?.message}
              />
            </>
          )}

          {/* Password */}
          <Input
            {...register('password')}
            label="Password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Create a password"
            rightIcon={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            }
            error={errors.password?.message}
          />

          <Input
            {...register('confirmPassword')}
            label="Confirm Password"
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="Confirm your password"
            rightIcon={
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="text-gray-400 hover:text-gray-600"
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            }
            error={errors.confirmPassword?.message}
          />

          {/* Error Message */}
          {errors.root && (
            <div className="text-red-600 text-sm text-center">
              {errors.root.message}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
          >
            Create Account
          </Button>
        </form>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/signin" className="font-medium text-primary-600 hover:text-primary-500">
              Sign in here
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
};
