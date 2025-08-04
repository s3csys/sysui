import axios from 'axios';
import { API_URL } from '../config';

// Types
export interface ServerTag {
  id: number;
  name: string;
  description?: string;
}

export interface ServerStatus {
  is_online: boolean;
  last_check?: string;
  error_message?: string;
}

export interface ServerCredential {
  username: string;
  auth_type: 'password' | 'key';
  password?: string;
  private_key?: string;
}

export interface Server {
  id: number;
  name: string;
  ip_address: string;
  ssh_port: number;
  description?: string;
  is_active: boolean;
  credentials: ServerCredential;
  status?: ServerStatus;
  tags: ServerTag[];
  created_at: string;
  updated_at: string;
}

export interface ServerListItem {
  id: number;
  name: string;
  ip_address: string;
  is_active: boolean;
  status?: ServerStatus;
  tags: string[];
}

export interface ServerDetail extends Server {
  system_info?: Record<string, any>;
}

export interface CreateServerData {
  name: string;
  ip_address: string;
  ssh_port: number;
  description?: string;
  is_active: boolean;
  credentials: {
    username: string;
    auth_type: 'password' | 'key';
    password?: string;
    private_key?: string;
  };
  tags?: string[];
}

export interface UpdateServerData {
  name?: string;
  ip_address?: string;
  ssh_port?: number;
  description?: string;
  is_active?: boolean;
  credentials?: {
    username?: string;
    auth_type?: 'password' | 'key';
    password?: string;
    private_key?: string;
  };
  tags?: string[];
}

export interface TestConnectionData {
  ip_address: string;
  ssh_port: number;
  username: string;
  auth_type: 'password' | 'key';
  password?: string;
  private_key?: string;
}

export interface TestConnectionResult {
  success: boolean;
  message: string;
}

// Server API Service
const serverService = {
  // Server Tags
  getTags: async (): Promise<ServerTag[]> => {
    const response = await axios.get(`${API_URL}/v1/servers/tags`);
    return response.data;
  },

  createTag: async (tag: { name: string; description?: string }): Promise<ServerTag> => {
    const response = await axios.post(`${API_URL}/v1/servers/tags`, tag);
    return response.data;
  },

  updateTag: async (id: number, tag: { name?: string; description?: string }): Promise<ServerTag> => {
    const response = await axios.put(`${API_URL}/v1/servers/tags/${id}`, tag);
    return response.data;
  },

  deleteTag: async (id: number): Promise<void> => {
    await axios.delete(`${API_URL}/v1/servers/tags/${id}`);
  },

  // Servers
  getServers: async (params?: { skip?: number; limit?: number; tag?: string }): Promise<ServerListItem[]> => {
    const response = await axios.get(`${API_URL}/v1/servers`, { params });
    return response.data;
  },

  getServer: async (id: number): Promise<ServerDetail> => {
    const response = await axios.get(`${API_URL}/v1/servers/${id}`);
    return response.data;
  },

  createServer: async (server: CreateServerData): Promise<Server> => {
    const response = await axios.post(`${API_URL}/v1/servers`, server);
    return response.data;
  },

  updateServer: async (id: number, server: UpdateServerData): Promise<Server> => {
    const response = await axios.put(`${API_URL}/v1/servers/${id}`, server);
    return response.data;
  },

  deleteServer: async (id: number): Promise<void> => {
    await axios.delete(`${API_URL}/v1/servers/${id}`);
  },

  checkServerStatus: async (id: number): Promise<ServerDetail> => {
    const response = await axios.post(`${API_URL}/v1/servers/${id}/check`);
    return response.data;
  },

  testConnection: async (data: TestConnectionData): Promise<TestConnectionResult> => {
    const response = await axios.post(`${API_URL}/v1/servers/test-connection`, data);
    return response.data;
  },
};

export default serverService;