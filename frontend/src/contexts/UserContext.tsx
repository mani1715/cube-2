/**
 * PHASE 12 - User Authentication Context
 * Manages user authentication state, login, logout, and token refresh
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { userAuthAPI } from '../lib/phase12Api';
import { toast } from 'sonner';

interface User {
  user_id: string;
  email: string;
  name: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface UserContextType {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string, phone?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (profileData: { name?: string; phone?: string }) => Promise<void>;
  refreshUserData: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedAccessToken = localStorage.getItem('user_access_token');
        const storedRefreshToken = localStorage.getItem('user_refresh_token');
        const storedUser = localStorage.getItem('user_data');

        if (storedAccessToken && storedUser) {
          setAccessToken(storedAccessToken);
          setRefreshToken(storedRefreshToken);
          setUser(JSON.parse(storedUser));

          // Verify token by fetching profile
          try {
            const response = await userAuthAPI.getProfile(storedAccessToken);
            setUser(response.user);
          } catch (error) {
            // Token might be expired, try refreshing
            if (storedRefreshToken) {
              try {
                const refreshResponse = await userAuthAPI.refreshToken(storedRefreshToken);
                setAccessToken(refreshResponse.access_token);
                localStorage.setItem('user_access_token', refreshResponse.access_token);

                // Fetch profile again
                const profileResponse = await userAuthAPI.getProfile(refreshResponse.access_token);
                setUser(profileResponse.user);
              } catch (refreshError) {
                // Refresh failed, clear everything
                handleLogoutCleanup();
              }
            } else {
              handleLogoutCleanup();
            }
          }
        }
      } catch (error) {
        console.error('Error loading user:', error);
        handleLogoutCleanup();
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const handleLogoutCleanup = () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem('user_access_token');
    localStorage.removeItem('user_refresh_token');
    localStorage.removeItem('user_data');
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await userAuthAPI.login({ email, password });

      if (response.success) {
        setUser(response.user);
        setAccessToken(response.access_token);
        setRefreshToken(response.refresh_token);

        // Store in localStorage
        localStorage.setItem('user_access_token', response.access_token);
        localStorage.setItem('user_refresh_token', response.refresh_token);
        localStorage.setItem('user_data', JSON.stringify(response.user));

        toast.success(`Welcome back, ${response.user.name}!`);
      } else {
        throw new Error('Login failed');
      }
    } catch (error: any) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials.';
      toast.error(errorMessage);
      throw error;
    }
  };

  const signup = async (email: string, password: string, name: string, phone?: string) => {
    try {
      const response = await userAuthAPI.signup({ email, password, name, phone });

      if (response.success) {
        setUser(response.user);
        setAccessToken(response.access_token);
        setRefreshToken(response.refresh_token);

        // Store in localStorage
        localStorage.setItem('user_access_token', response.access_token);
        localStorage.setItem('user_refresh_token', response.refresh_token);
        localStorage.setItem('user_data', JSON.stringify(response.user));

        toast.success(`Welcome to A-Cube, ${response.user.name}!`);
      } else {
        throw new Error('Signup failed');
      }
    } catch (error: any) {
      console.error('Signup error:', error);
      const errorMessage = error.response?.data?.detail || 'Signup failed. Please try again.';
      toast.error(errorMessage);
      throw error;
    }
  };

  const logout = async () => {
    try {
      if (accessToken && refreshToken) {
        await userAuthAPI.logout(refreshToken, accessToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      handleLogoutCleanup();
      toast.success('Logged out successfully');
    }
  };

  const updateProfile = async (profileData: { name?: string; phone?: string }) => {
    if (!accessToken) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await userAuthAPI.updateProfile(profileData, accessToken);

      if (response.success) {
        setUser(response.user);
        localStorage.setItem('user_data', JSON.stringify(response.user));
        toast.success('Profile updated successfully');
      }
    } catch (error: any) {
      console.error('Profile update error:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to update profile';
      toast.error(errorMessage);
      throw error;
    }
  };

  const refreshUserData = async () => {
    if (!accessToken) return;

    try {
      const response = await userAuthAPI.getProfile(accessToken);
      setUser(response.user);
      localStorage.setItem('user_data', JSON.stringify(response.user));
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  };

  const value = {
    user,
    accessToken,
    refreshToken,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    updateProfile,
    refreshUserData
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
