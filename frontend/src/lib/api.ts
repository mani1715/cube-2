// API Configuration
const API_BASE_URL = import.meta.env.VITE_REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || '';

// Helper function for making API requests
async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Session Booking API
export const sessionAPI = {
  bookSession: async (bookingData: any) => {
    return apiRequest('/api/sessions/book', {
      method: 'POST',
      body: JSON.stringify(bookingData),
    });
  },

  getAllSessions: async (statusFilter?: string) => {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return apiRequest(`/api/sessions${query}`);
  },

  getSession: async (sessionId: string) => {
    return apiRequest(`/api/sessions/${sessionId}`);
  },

  updateSessionStatus: async (sessionId: string, newStatus: string) => {
    return apiRequest(`/api/sessions/${sessionId}/status?new_status=${newStatus}`, {
      method: 'PATCH',
    });
  },
};

// Event API
export const eventAPI = {
  createEvent: async (eventData: any) => {
    return apiRequest('/api/events', {
      method: 'POST',
      body: JSON.stringify(eventData),
    });
  },

  getAllEvents: async (isActive?: boolean) => {
    const query = isActive !== undefined ? `?is_active=${isActive}` : '';
    return apiRequest(`/api/events${query}`);
  },

  getEvent: async (eventId: string) => {
    return apiRequest(`/api/events/${eventId}`);
  },

  registerForEvent: async (eventId: string, registrationData: any) => {
    return apiRequest(`/api/events/${eventId}/register?full_name=${encodeURIComponent(registrationData.fullName)}&email=${encodeURIComponent(registrationData.email)}&phone=${encodeURIComponent(registrationData.phone || '')}`, {
      method: 'POST',
    });
  },
};

// Blog API
export const blogAPI = {
  createBlog: async (blogData: any) => {
    return apiRequest('/api/blogs', {
      method: 'POST',
      body: JSON.stringify(blogData),
    });
  },

  getAllBlogs: async (category?: string, featured?: boolean) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (featured !== undefined) params.append('featured', String(featured));
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/api/blogs${query}`);
  },

  getBlog: async (blogId: string) => {
    return apiRequest(`/api/blogs/${blogId}`);
  },
};

// Career API
export const careerAPI = {
  createJob: async (jobData: any) => {
    return apiRequest('/api/careers', {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
  },

  getAllJobs: async (isActive?: boolean) => {
    const query = isActive !== undefined ? `?is_active=${isActive}` : '';
    return apiRequest(`/api/careers${query}`);
  },

  getJob: async (jobId: string) => {
    return apiRequest(`/api/careers/${jobId}`);
  },

  applyForJob: async (jobId: string, applicationData: any) => {
    return apiRequest(`/api/careers/${jobId}/apply`, {
      method: 'POST',
      body: JSON.stringify(applicationData),
    });
  },
};

// Volunteer API
export const volunteerAPI = {
  submitApplication: async (volunteerData: any) => {
    return apiRequest('/api/volunteers', {
      method: 'POST',
      body: JSON.stringify(volunteerData),
    });
  },

  getAllVolunteers: async (statusFilter?: string) => {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return apiRequest(`/api/volunteers${query}`);
  },
};

// Psychologist API
export const psychologistAPI = {
  createProfile: async (psychologistData: any) => {
    return apiRequest('/api/psychologists', {
      method: 'POST',
      body: JSON.stringify(psychologistData),
    });
  },

  getAllPsychologists: async (isActive?: boolean) => {
    const query = isActive !== undefined ? `?is_active=${isActive}` : '';
    return apiRequest(`/api/psychologists${query}`);
  },

  getPsychologist: async (psychologistId: string) => {
    return apiRequest(`/api/psychologists/${psychologistId}`);
  },
};

// Contact Form API
export const contactAPI = {
  submitForm: async (contactData: any) => {
    return apiRequest('/api/contact', {
      method: 'POST',
      body: JSON.stringify(contactData),
    });
  },

  getAllForms: async (statusFilter?: string) => {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return apiRequest(`/api/contact${query}`);
  },
};

// Payment API
export const paymentAPI = {
  processPayment: async (paymentData: any) => {
    return apiRequest('/api/payments', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    });
  },

  getPayment: async (paymentId: string) => {
    return apiRequest(`/api/payments/${paymentId}`);
  },
};

// Health Check
export const healthAPI = {
  check: async () => {
    return apiRequest('/api/health');
  },
};

export default {
  session: sessionAPI,
  event: eventAPI,
  blog: blogAPI,
  career: careerAPI,
  volunteer: volunteerAPI,
  psychologist: psychologistAPI,
  contact: contactAPI,
  payment: paymentAPI,
  health: healthAPI,
};
