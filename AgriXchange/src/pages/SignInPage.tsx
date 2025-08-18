import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, Phone, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button, Input, Card } from '../components/ui';
import type { UserRole } from '../types';

const signInSchema = z.object({
  phone: z.string().min(10, 'Phone number must be at least 10 digits'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  role: z.enum(['farmer', 'trader', 'user'] as const),
});

type SignInForm = z.infer<typeof signInSchema>;

export const SignInPage: React.FC = () => {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('user');

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<SignInForm>({
    resolver: zodResolver(signInSchema),
    defaultValues: {
      role: selectedRole,
    },
  });

  const onSubmit = async (data: SignInForm) => {
    try {
      await login(data.phone, data.password, data.role);
      
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
        message: error instanceof Error ? error.message : 'Login failed',
      });
    }
  };

  const handleRoleChange = (role: UserRole) => {
    setSelectedRole(role);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Welcome Back</h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to your AgriXchange account
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
            <input
              type="hidden"
              {...register('role')}
              value={selectedRole}
            />
          </div>

          {/* Phone Number */}
          <Input
            {...register('phone')}
            label="Phone Number"
            type="tel"
            placeholder="Enter your phone number"
            leftIcon={<Phone className="w-5 h-5" />}
            error={errors.phone?.message}
          />

          {/* Password */}
          <Input
            {...register('password')}
            label="Password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Enter your password"
            leftIcon={<Lock className="w-5 h-5" />}
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
            Sign In
          </Button>
        </form>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="font-medium text-primary-600 hover:text-primary-500">
              Sign up here
            </Link>
          </p>
        </div>

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-gray-100 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">Demo Credentials:</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <p><strong>Phone:</strong> Any 10-digit number</p>
            <p><strong>Password:</strong> Any 6+ characters</p>
            <p className="text-xs text-gray-500 mt-2">
              This is a demo application. Any valid phone number and password will work.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
