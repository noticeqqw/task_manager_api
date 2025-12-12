import axios from 'axios';
import type { 
  AuthTokens, LoginCredentials, RegisterData, User, Task, TaskCreate, TaskUpdate,
  Team, TeamCreate, TeamMember
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена к запросам
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Интерцептор для обработки ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  
  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
  
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  refresh: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
};

// Tasks API
export const tasksApi = {
  getAll: async (): Promise<Task[]> => {
    const response = await api.get('/tasks/');
    return response.data;
  },
  
  getById: async (id: string): Promise<Task> => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },
  
  create: async (data: TaskCreate, idempotencyKey?: string): Promise<Task> => {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    const response = await api.post('/tasks/', data, { headers });
    return response.data;
  },
  
  update: async (id: string, data: TaskUpdate): Promise<Task> => {
    const response = await api.patch(`/tasks/${id}`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },
};

// Teams API
export const teamsApi = {
  getAll: async (): Promise<Team[]> => {
    const response = await api.get('/teams/');
    return response.data;
  },
  
  getMyTeams: async (): Promise<Team[]> => {
    const response = await api.get('/teams/my');
    return response.data;
  },
  
  getById: async (id: string): Promise<Team> => {
    const response = await api.get(`/teams/${id}`);
    return response.data;
  },
  
  getMembers: async (teamId: string): Promise<TeamMember[]> => {
    const response = await api.get(`/teams/${teamId}/members`);
    return response.data;
  },
  
  create: async (data: TeamCreate): Promise<Team> => {
    const response = await api.post('/teams/', data);
    return response.data;
  },
  
  join: async (teamId: string): Promise<void> => {
    await api.post(`/teams/${teamId}/join`);
  },
  
  leave: async (teamId: string): Promise<void> => {
    await api.post(`/teams/${teamId}/leave`);
  },
  
  updateMemberRole: async (teamId: string, userId: string, role: string): Promise<void> => {
    await api.patch(`/teams/${teamId}/members/${userId}`, { role });
  },
  
  removeMember: async (teamId: string, userId: string): Promise<void> => {
    await api.delete(`/teams/${teamId}/members/${userId}`);
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/teams/${id}`);
  },
};

export default api;
