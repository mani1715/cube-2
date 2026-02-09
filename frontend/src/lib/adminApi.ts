// Admin API Configuration
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || '';

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

// Refresh access token using refresh token
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('adminRefreshToken');
  
  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/admin/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Refresh token is invalid, clear tokens and redirect to login
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminRefreshToken');
      window.location.href = '/admin/login';
      return null;
    }

    const data = await response.json();
    localStorage.setItem('adminToken', data.access_token);
    localStorage.setItem('adminRefreshToken', data.refresh_token);
    return data.access_token;
  } catch (error) {
    console.error('Token refresh failed:', error);
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminRefreshToken');
    window.location.href = '/admin/login';
    return null;
  }
}

// Helper function for making authenticated admin API requests with token refresh
async function adminApiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Get token from localStorage
  let token = localStorage.getItem('adminToken');
  
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Add authorization header if token exists
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    // Handle 401 Unauthorized - try to refresh token
    if (response.status === 401) {
      if (!isRefreshing) {
        isRefreshing = true;
        const newToken = await refreshAccessToken();
        isRefreshing = false;
        
        if (newToken) {
          onTokenRefreshed(newToken);
          // Retry original request with new token
          config.headers = {
            ...config.headers,
            'Authorization': `Bearer ${newToken}`,
          };
          return adminApiRequest(endpoint, options);
        }
      } else {
        // Wait for the ongoing token refresh
        return new Promise((resolve) => {
          addRefreshSubscriber((newToken: string) => {
            config.headers = {
              ...config.headers,
              'Authorization': `Bearer ${newToken}`,
            };
            resolve(adminApiRequest(endpoint, options));
          });
        });
      }
    }
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Admin API request failed:', error);
    throw error;
  }
}

// Admin Auth API
export const adminAuthAPI = {
  login: async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    localStorage.setItem('adminToken', data.access_token);
    localStorage.setItem('adminRefreshToken', data.refresh_token);
    return data;
  },

  logout: async () => {
    const refreshToken = localStorage.getItem('adminRefreshToken');
    if (refreshToken) {
      try {
        await adminApiRequest('/api/admin/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch (error) {
        console.error('Logout API failed:', error);
      }
    }
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminRefreshToken');
  },

  verifyToken: async () => {
    return adminApiRequest('/api/admin/auth/verify');
  },

  getCurrentAdmin: async () => {
    return adminApiRequest('/api/admin/me');
  },
};

// Admin Dashboard API
export const adminDashboardAPI = {
  getDashboard: async () => {
    return adminApiRequest('/api/admin/dashboard');
  },
};

// Admin Sessions API
export const adminSessionsAPI = {
  getSessions: async (page: number = 1, limit: number = 10, statusFilter?: string) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    if (statusFilter && statusFilter !== 'all') {
      params.append('status_filter', statusFilter);
    }
    return adminApiRequest(`/api/admin/sessions?${params.toString()}`);
  },

  createSession: async (sessionData: any) => {
    return adminApiRequest('/api/admin/sessions', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  },

  updateSession: async (sessionId: string, sessionData: any) => {
    return adminApiRequest(`/api/admin/sessions/${sessionId}`, {
      method: 'PUT',
      body: JSON.stringify(sessionData),
    });
  },

  updateSessionStatus: async (sessionId: string, status: string) => {
    return adminApiRequest(`/api/admin/sessions/${sessionId}/status?status=${status}`, {
      method: 'PATCH',
    });
  },

  deleteSession: async (sessionId: string) => {
    return adminApiRequest(`/api/admin/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  },
};

// Admin Search API
export const adminSearchAPI = {
  search: async (query: string) => {
    return adminApiRequest(`/api/admin/search?q=${encodeURIComponent(query)}`);
  },
};

// Admin Audit Logs API
export const adminAuditLogsAPI = {
  getLogs: async (page: number = 1, limit: number = 50, filters?: {
    action?: string;
    entity?: string;
    admin_email?: string;
  }) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    if (filters?.action) params.append('action', filters.action);
    if (filters?.entity) params.append('entity', filters.entity);
    if (filters?.admin_email) params.append('admin_email', filters.admin_email);
    return adminApiRequest(`/api/admin/audit-logs?${params.toString()}`);
  },

  getStats: async () => {
    return adminApiRequest('/api/admin/audit-logs/stats');
  },
};

// Admin Events API
export const adminEventsAPI = {
  getEvents: async (page: number = 1, limit: number = 10) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    return adminApiRequest(`/api/admin/events?${params.toString()}`);
  },

  createEvent: async (eventData: any) => {
    return adminApiRequest('/api/admin/events', {
      method: 'POST',
      body: JSON.stringify(eventData),
    });
  },

  updateEvent: async (eventId: string, eventData: any) => {
    return adminApiRequest(`/api/admin/events/${eventId}`, {
      method: 'PUT',
      body: JSON.stringify(eventData),
    });
  },

  deleteEvent: async (eventId: string) => {
    return adminApiRequest(`/api/admin/events/${eventId}`, {
      method: 'DELETE',
    });
  },
};

// Admin Blogs API
export const adminBlogsAPI = {
  getBlogs: async (page: number = 1, limit: number = 10) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    return adminApiRequest(`/api/admin/blogs?${params.toString()}`);
  },

  createBlog: async (blogData: any) => {
    return adminApiRequest('/api/admin/blogs', {
      method: 'POST',
      body: JSON.stringify(blogData),
    });
  },

  updateBlog: async (blogId: string, blogData: any) => {
    return adminApiRequest(`/api/admin/blogs/${blogId}`, {
      method: 'PUT',
      body: JSON.stringify(blogData),
    });
  },

  deleteBlog: async (blogId: string) => {
    return adminApiRequest(`/api/admin/blogs/${blogId}`, {
      method: 'DELETE',
    });
  },
};

// Admin Jobs API
export const adminJobsAPI = {
  getJobs: async (page: number = 1, limit: number = 10) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    return adminApiRequest(`/api/admin/jobs?${params.toString()}`);
  },

  createJob: async (jobData: any) => {
    return adminApiRequest('/api/admin/jobs', {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
  },

  updateJob: async (jobId: string, jobData: any) => {
    return adminApiRequest(`/api/admin/jobs/${jobId}`, {
      method: 'PUT',
      body: JSON.stringify(jobData),
    });
  },

  deleteJob: async (jobId: string) => {
    return adminApiRequest(`/api/admin/jobs/${jobId}`, {
      method: 'DELETE',
    });
  },
};

// Admin Psychologists API
export const adminPsychologistsAPI = {
  getPsychologists: async (page: number = 1, limit: number = 10) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    return adminApiRequest(`/api/admin/psychologists?${params.toString()}`);
  },

  createPsychologist: async (psychologistData: any) => {
    return adminApiRequest('/api/admin/psychologists', {
      method: 'POST',
      body: JSON.stringify(psychologistData),
    });
  },

  updatePsychologist: async (psychologistId: string, psychologistData: any) => {
    return adminApiRequest(`/api/admin/psychologists/${psychologistId}`, {
      method: 'PUT',
      body: JSON.stringify(psychologistData),
    });
  },

  deletePsychologist: async (psychologistId: string) => {
    return adminApiRequest(`/api/admin/psychologists/${psychologistId}`, {
      method: 'DELETE',
    });
  },
};

// Admin Volunteers API
export const adminVolunteersAPI = {
  getVolunteers: async (page: number = 1, limit: number = 10, status?: string) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    if (status) params.append('status', status);
    return adminApiRequest(`/api/admin/volunteers?${params.toString()}`);
  },

  updateVolunteer: async (volunteerId: string, volunteerData: any) => {
    return adminApiRequest(`/api/admin/volunteers/${volunteerId}`, {
      method: 'PUT',
      body: JSON.stringify(volunteerData),
    });
  },

  deleteVolunteer: async (volunteerId: string) => {
    return adminApiRequest(`/api/admin/volunteers/${volunteerId}`, {
      method: 'DELETE',
    });
  },
};

// Admin Contacts API
export const adminContactsAPI = {
  getContacts: async (page: number = 1, limit: number = 10, status?: string) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    if (status) params.append('status', status);
    return adminApiRequest(`/api/admin/contacts?${params.toString()}`);
  },

  updateContact: async (contactId: string, contactData: any) => {
    return adminApiRequest(`/api/admin/contacts/${contactId}`, {
      method: 'PUT',
      body: JSON.stringify(contactData),
    });
  },

  deleteContact: async (contactId: string) => {
    return adminApiRequest(`/api/admin/contacts/${contactId}`, {
      method: 'DELETE',
    });
  },
};

// Admin Logs API (alias for audit logs)
export const adminLogsAPI = {
  getLogs: async (page: number = 1, limit: number = 50, filters?: any) => {
    return adminAuditLogsAPI.getLogs(page, limit, filters);
  },
  getStats: async () => {
    return adminAuditLogsAPI.getStats();
  },
};

// Admin Settings API
export const adminAPI = {
  getSettings: async () => {
    return adminApiRequest('/api/admin/settings');
  },
  
  updateSettings: async (settings: any) => {
    return adminApiRequest('/api/admin/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  },
};

// Admin File Upload API
export const adminFileAPI = {
  uploadFile: async (file: File) => {
    const token = localStorage.getItem('adminToken');
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/admin/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'File upload failed');
    }

    return await response.json();
  },
};

// Alias for compatibility
export const adminFileUploadAPI = adminFileAPI;

// Admin Bulk Operations API
export const adminBulkAPI = {
  bulkDelete: async (entity: string, ids: string[]) => {
    return await adminApiRequest('/api/admin/bulk/delete', {
      method: 'POST',
      body: JSON.stringify({ entity, ids }),
    });
  },

  bulkExport: async (entity: string, format: string = 'csv', status?: string) => {
    const params = new URLSearchParams({ format });
    if (status) params.append('status', status);
    
    const data = await adminApiRequest(`/api/admin/bulk/export/${entity}?${params.toString()}`);
    return data;
  },

  globalSearch: async (query: string, limit: number = 20) => {
    const params = new URLSearchParams({ q: query, limit: limit.toString() });
    return await adminApiRequest(`/api/admin/search/global?${params.toString()}`);
  },
};

// Admin Error Tracking API
export const adminErrorAPI = {
  logError: async (errorData: {
    error_type: string;
    severity: string;
    message: string;
    stack_trace?: string;
    component?: string;
    url?: string;
    context?: any;
  }) => {
    return await adminApiRequest('/api/admin/errors/log', {
      method: 'POST',
      body: JSON.stringify(errorData),
    });
  },

  getErrors: async (page: number = 1, limit: number = 50, filters?: {
    severity?: string;
    error_type?: string;
    resolved?: boolean;
  }) => {
    const params = new URLSearchParams({ 
      page: page.toString(), 
      limit: limit.toString() 
    });
    
    if (filters?.severity) params.append('severity', filters.severity);
    if (filters?.error_type) params.append('error_type', filters.error_type);
    if (filters?.resolved !== undefined) params.append('resolved', filters.resolved.toString());
    
    return await adminApiRequest(`/api/admin/errors/list?${params.toString()}`);
  },

  getErrorStats: async () => {
    return await adminApiRequest('/api/admin/errors/stats');
  },

  resolveError: async (errorId: string) => {
    return await adminApiRequest(`/api/admin/errors/${errorId}/resolve`, {
      method: 'PATCH',
    });
  },

  deleteError: async (errorId: string) => {
    return await adminApiRequest(`/api/admin/errors/${errorId}`, {
      method: 'DELETE',
    });
  },
};

// Phase 8 - AI Blog Assistant API
export const adminAIAPI = {
  generateBlogDraft: async (data: {
    topic: string;
    keywords?: string[];
    tone?: string;
    length?: string;
  }) => {
    return await adminApiRequest('/api/admin/phase8/ai/blog/draft', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  improveContent: async (data: {
    content: string;
    improvement_type?: string;
  }) => {
    return await adminApiRequest('/api/admin/phase8/ai/blog/improve', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  suggestTags: async (data: {
    title: string;
    content: string;
  }) => {
    return await adminApiRequest('/api/admin/phase8/ai/blog/suggest-tags', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  suggestTitles: async (data: {
    content: string;
    count?: number;
  }) => {
    return await adminApiRequest('/api/admin/phase8/ai/blog/suggest-titles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  generateSummary: async (data: {
    content: string;
    max_length?: number;
  }) => {
    return await adminApiRequest('/api/admin/phase8/ai/blog/generate-summary', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  qualityCheck: async (data: {
    title: string;
    content: string;
  }) => {
    return await adminApiRequest('/api/admin/phase8/ai/blog/quality-check', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getAIStatus: async () => {
    return await adminApiRequest('/api/admin/phase8/ai/status');
  },
};

// Default export combining all APIs
export default {
  ...adminAuthAPI,
  ...adminSessionsAPI,
  ...adminEventsAPI,
  ...adminBlogsAPI,
  ...adminPsychologistsAPI,
  ...adminVolunteersAPI,
  ...adminJobsAPI,
  ...adminContactsAPI,
  ...adminLogsAPI,
  ...adminAPI,
};
