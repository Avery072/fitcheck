import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';
import { apiConfig } from '../config';

const api = axios.create({
  baseURL: apiConfig.endpoint,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (error) {
    console.error('Error getting auth token:', error);
  }
  return config;
});

// API Methods
export const uploadApi = {
  getUploadUrl: async (type = 'body', extension = 'png') => {
    const response = await api.get('/upload-url', {
      params: { type, extension }
    });
    return response.data;
  },

  uploadFile: async (url, file) => {
    await axios.put(url, file, {
      headers: { 'Content-Type': file.type }
    });
  }
};

export const multiFitApi = {
  startTryOn: async (items, bodyAssetKey, sessionId = null) => {
    const response = await api.post('/multi-fit', {
      items,
      body_asset_key: bodyAssetKey,
      session_id: sessionId
    });
    return response.data;
  },

  getStatus: async (sessionId) => {
    const response = await api.get('/multi-fit', {
      params: { session_id: sessionId }
    });
    return response.data;
  }
};

export const userAssetsApi = {
  getAssets: async () => {
    const response = await api.get('/user-assets');
    return response.data;
  }
};

export const profileApi = {
  getProfile: async () => {
    const response = await api.get('/profile');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.post('/profile', profileData);
    return response.data;
  }
};

export default api;
