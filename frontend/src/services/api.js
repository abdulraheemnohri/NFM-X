import axios from 'axios';

// Create API client
const apiClient = axios.create({
  baseURL: localStorage.getItem('nfmApiUrl') || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for API key
apiClient.interceptors.request.use(
  (config) => {
    const apiKey = localStorage.getItem('nfmApiKey');
    if (apiKey) {
      config.headers.Authorization = 'Bearer ' + apiKey;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Memory API calls
export const memoryApi = {
  getAll: (params = {}) => apiClient.get('/api/memory/', { params }),
  getById: (id) => apiClient.get('/api/memory/' + id),
  create: (data) => apiClient.post('/api/memory/', data),
  update: (id, data) => apiClient.put('/api/memory/' + id, data),
  delete: (id) => apiClient.delete('/api/memory/' + id),
  getVersions: (id, params = {}) => apiClient.get('/api/memory/' + id + '/versions', { params }),
  listTypes: () => apiClient.get('/api/memory/types'),
};

// Search API calls
export const searchApi = {
  search: (data) => apiClient.post('/api/search/', data),
  advancedSearch: (data) => apiClient.post('/api/search/advanced', data),
};

// Context API calls
export const contextApi = {
  getContext: (data) => apiClient.post('/api/context/', data),
};

// Evolution API calls
export const evolutionApi = {
  evolve: (data) => apiClient.post('/api/evolution/', data),
};

// Graph API calls
export const graphApi = {
  query: (data) => apiClient.post('/api/graph/', data),
  getNodes: (params = {}) => apiClient.get('/api/graph/nodes', { params }),
  getEdges: (params = {}) => apiClient.get('/api/graph/edges', { params }),
};

// Agent API calls
export const agentApi = {
  query: (data) => apiClient.post('/api/agents/', data),
};

// System API calls
export const systemApi = {
  healthCheck: () => apiClient.get('/health'),
  getInfo: () => apiClient.get('/info'),
  getStats: () => apiClient.get('/stats'),
};

// Configure API base URL
export const configureApi = (baseUrl) => {
  apiClient.defaults.baseURL = baseUrl;
  localStorage.setItem('nfmApiUrl', baseUrl);
};

// Configure API key
export const configureApiKey = (apiKey) => {
  if (apiKey) {
    localStorage.setItem('nfmApiKey', apiKey);
  } else {
    localStorage.removeItem('nfmApiKey');
  }
};

// Error handler
export const handleApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response;
    
    if (status === 401) {
      return { error: 'Unauthorized', message: 'Please check your API key' };
    }
    if (status === 404) {
      return { error: 'Not Found', message: 'Resource not found' };
    }
    if (status === 500) {
      return { error: 'Server Error', message: 'Internal server error' };
    }
    
    return { 
      error: 'API Error', 
      message: data?.detail || data?.error || 'An error occurred' 
    };
  } else if (error.request) {
    return { 
      error: 'Connection Error', 
      message: 'Could not connect to the server. Please check your connection.' 
    };
  } else {
    return { 
      error: 'Request Error', 
      message: error.message || 'An error occurred' 
    };
  }
};

// Export default client for custom requests
export default apiClient;

// Urdu: NFM-X API Service
// یہ frontend se backend API se bat cheet karne ke liye service file hai