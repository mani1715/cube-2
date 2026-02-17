/**
 * PHASE 12 - User Authentication API
 * Handles user signup, login, logout, and profile management
 */

import axios from 'axios';

const API_URL = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// User Auth API
export const userAuthAPI = {
  signup: async (userData: {
    email: string;
    password: string;
    name: string;
    phone?: string;
  }) => {
    const response = await axios.post(`${API_URL}/api/phase12/users/signup`, userData);
    return response.data;
  },

  login: async (credentials: { email: string; password: string }) => {
    const response = await axios.post(`${API_URL}/api/phase12/users/login`, credentials);
    return response.data;
  },

  logout: async (refreshToken: string, accessToken: string) => {
    const response = await axios.post(
      `${API_URL}/api/phase12/users/logout`,
      { refresh_token: refreshToken },
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  refreshToken: async (refreshToken: string) => {
    const response = await axios.post(`${API_URL}/api/phase12/users/refresh`, {
      refresh_token: refreshToken
    });
    return response.data;
  },

  getProfile: async (accessToken: string) => {
    const response = await axios.get(`${API_URL}/api/phase12/users/profile`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data;
  },

  updateProfile: async (profileData: { name?: string; phone?: string }, accessToken: string) => {
    const response = await axios.put(
      `${API_URL}/api/phase12/users/profile`,
      profileData,
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  changePassword: async (
    passwordData: { old_password: string; new_password: string },
    accessToken: string
  ) => {
    const response = await axios.post(
      `${API_URL}/api/phase12/users/change-password`,
      passwordData,
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  deleteAccount: async (password: string, accessToken: string) => {
    const response = await axios.delete(`${API_URL}/api/phase12/users/account`, {
      data: { password },
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data;
  }
};

// Payment API
export const paymentAPI = {
  getConfig: async () => {
    const response = await axios.get(`${API_URL}/api/phase12/payments/config`);
    return response.data;
  },

  createOrder: async (orderData: {
    amount: number;
    item_type: string;
    item_id: string;
    item_name: string;
    user_email?: string;
    user_name?: string;
    user_phone?: string;
  }) => {
    const response = await axios.post(`${API_URL}/api/phase12/payments/create-order`, orderData);
    return response.data;
  },

  verifyPayment: async (paymentData: {
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
  }) => {
    const response = await axios.post(`${API_URL}/api/phase12/payments/verify-payment`, paymentData);
    return response.data;
  },

  getTransaction: async (transactionId: string) => {
    const response = await axios.get(`${API_URL}/api/phase12/payments/transaction/${transactionId}`);
    return response.data;
  },

  getAllTransactions: async (filters?: { status?: string; item_type?: string; page?: number }) => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.item_type) params.append('item_type', filters.item_type);
    if (filters?.page) params.append('page', filters.page.toString());

    const response = await axios.get(`${API_URL}/api/phase12/payments/transactions?${params}`);
    return response.data;
  }
};

// User Dashboard API
export const dashboardAPI = {
  getOverview: async (accessToken: string) => {
    const response = await axios.get(`${API_URL}/api/phase12/dashboard/overview`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data;
  },

  getUserSessions: async (accessToken: string, status?: string) => {
    const params = status ? `?status=${status}` : '';
    const response = await axios.get(`${API_URL}/api/phase12/dashboard/sessions${params}`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data;
  },

  getUserEvents: async (accessToken: string) => {
    const response = await axios.get(`${API_URL}/api/phase12/dashboard/events`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data;
  },

  getUserPayments: async (accessToken: string, status?: string) => {
    const params = status ? `?status=${status}` : '';
    const response = await axios.get(`${API_URL}/api/phase12/dashboard/payments${params}`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data;
  },

  saveBlog: async (blogId: string, accessToken: string) => {
    const response = await axios.post(
      `${API_URL}/api/phase12/dashboard/blogs/save`,
      { blog_id: blogId },
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  unsaveBlog: async (blogId: string, accessToken: string) => {
    const response = await axios.delete(
      `${API_URL}/api/phase12/dashboard/blogs/save/${blogId}`,
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  getSavedBlogs: async (accessToken: string) => {
    const response = await axios.get(`${API_URL}/api/phase12/dashboard/blogs/saved`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    return response.data;
  },

  isBlogSaved: async (blogId: string, accessToken: string) => {
    const response = await axios.get(
      `${API_URL}/api/phase12/dashboard/blogs/is-saved/${blogId}`,
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  likeBlog: async (blogId: string, accessToken: string) => {
    const response = await axios.post(
      `${API_URL}/api/phase12/dashboard/blogs/like`,
      { blog_id: blogId },
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  unlikeBlog: async (blogId: string, accessToken: string) => {
    const response = await axios.delete(
      `${API_URL}/api/phase12/dashboard/blogs/like/${blogId}`,
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  isBlogLiked: async (blogId: string, accessToken: string) => {
    const response = await axios.get(
      `${API_URL}/api/phase12/dashboard/blogs/is-liked/${blogId}`,
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );
    return response.data;
  },

  getBlogStats: async (blogId: string) => {
    const response = await axios.get(`${API_URL}/api/phase12/dashboard/blogs/${blogId}/stats`);
    return response.data;
  }
};

// Email Service API (for admin/testing purposes)
export const emailAPI = {
  getStatus: async () => {
    const response = await axios.get(`${API_URL}/api/phase12/emails/status`);
    return response.data;
  },

  sendEmail: async (emailData: {
    recipient_email: string;
    subject: string;
    html_content: string;
  }) => {
    const response = await axios.post(`${API_URL}/api/phase12/emails/send`, emailData);
    return response.data;
  }
};
