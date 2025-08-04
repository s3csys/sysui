import axios from 'axios';
import {
  getServerTags,
  createServerTag,
  updateServerTag,
  deleteServerTag,
  getServers,
  createServer,
  getServerById,
  updateServer,
  deleteServer,
  testConnection,
  getServerStatus,
  refreshServerStatus,
  getServerDetails
} from '../serverService';
import { API_URL } from '../../config';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Server Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Server Tags Tests
  describe('Server Tags', () => {
    test('getServerTags fetches tags correctly', async () => {
      const mockTags = [
        { id: 1, name: 'Production', description: 'Production servers', color: '#FF0000' },
        { id: 2, name: 'Development', description: 'Development servers', color: '#00FF00' }
      ];
      
      mockedAxios.get.mockResolvedValueOnce({ data: mockTags });
      
      const result = await getServerTags();
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/v1/servers/tags`);
      expect(result).toEqual(mockTags);
    });

    test('createServerTag creates a tag correctly', async () => {
      const newTag = { name: 'Testing', description: 'Testing servers', color: '#0000FF' };
      const mockResponse = { id: 3, ...newTag };
      
      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });
      
      const result = await createServerTag(newTag);
      
      expect(mockedAxios.post).toHaveBeenCalledWith(`${API_URL}/v1/servers/tags`, newTag);
      expect(result).toEqual(mockResponse);
    });

    test('updateServerTag updates a tag correctly', async () => {
      const tagId = 1;
      const updatedTag = { name: 'Updated', description: 'Updated description', color: '#FF00FF' };
      const mockResponse = { id: tagId, ...updatedTag };
      
      mockedAxios.put.mockResolvedValueOnce({ data: mockResponse });
      
      const result = await updateServerTag(tagId, updatedTag);
      
      expect(mockedAxios.put).toHaveBeenCalledWith(`${API_URL}/v1/servers/tags/${tagId}`, updatedTag);
      expect(result).toEqual(mockResponse);
    });

    test('deleteServerTag deletes a tag correctly', async () => {
      const tagId = 1;
      const mockResponse = { message: 'Tag deleted successfully' };
      
      mockedAxios.delete.mockResolvedValueOnce({ data: mockResponse });
      
      const result = await deleteServerTag(tagId);
      
      expect(mockedAxios.delete).toHaveBeenCalledWith(`${API_URL}/v1/servers/tags/${tagId}`);
      expect(result).toEqual(mockResponse);
    });
  });

  // Servers Tests
  describe('Servers', () => {
    test('getServers fetches servers correctly', async () => {
      const mockServers = [
        { id: 1, name: 'Server 1', hostname: '192.168.1.1', port: 22, active: true },
        { id: 2, name: 'Server 2', hostname: '192.168.1.2', port: 22, active: false }
      ];
      
      mockedAxios.get.mockResolvedValueOnce({ data: { items: mockServers, total: 2 } });
      
      const result = await getServers();
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/v1/servers`);
      expect(result).toEqual({ items: mockServers, total: 2 });
    });

    test('createServer creates a server correctly', async () => {
      const newServer = {
        name: 'New Server',
        hostname: '192.168.1.3',
        port: 22,
        description: 'New server description',
        active: true,
        tags: [1, 2],
        credential: {
          username: 'admin',
          auth_type: 'password',
          password: 'password123'
        }
      };
      
      const mockResponse = { id: 3, ...newServer, credential: { ...newServer.credential, password: undefined } };
      
      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });
      
      const result = await createServer(newServer);
      
      expect(mockedAxios.post).toHaveBeenCalledWith(`${API_URL}/v1/servers`, newServer);
      expect(result).toEqual(mockResponse);
    });

    test('getServerById fetches a server correctly', async () => {
      const serverId = 1;
      const mockServer = {
        id: serverId,
        name: 'Server 1',
        hostname: '192.168.1.1',
        port: 22,
        description: 'Server description',
        active: true,
        tags: [{ id: 1, name: 'Production', color: '#FF0000' }],
        credential: {
          username: 'admin',
          auth_type: 'password'
        }
      };
      
      mockedAxios.get.mockResolvedValueOnce({ data: mockServer });
      
      const result = await getServerById(serverId);
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/v1/servers/${serverId}`);
      expect(result).toEqual(mockServer);
    });

    test('updateServer updates a server correctly', async () => {
      const serverId = 1;
      const updatedServer = {
        name: 'Updated Server',
        hostname: '192.168.1.1',
        port: 2222,
        description: 'Updated description',
        active: false,
        tags: [1],
        credential: {
          username: 'updated_admin',
          auth_type: 'password',
          password: 'newpassword'
        }
      };
      
      const mockResponse = { id: serverId, ...updatedServer, credential: { ...updatedServer.credential, password: undefined } };
      
      mockedAxios.put.mockResolvedValueOnce({ data: mockResponse });
      
      const result = await updateServer(serverId, updatedServer);
      
      expect(mockedAxios.put).toHaveBeenCalledWith(`${API_URL}/v1/servers/${serverId}`, updatedServer);
      expect(result).toEqual(mockResponse);
    });

    test('deleteServer deletes a server correctly', async () => {
      const serverId = 1;
      const mockResponse = { message: 'Server deleted successfully' };
      
      mockedAxios.delete.mockResolvedValueOnce({ data: mockResponse });
      
      const result = await deleteServer(serverId);
      
      expect(mockedAxios.delete).toHaveBeenCalledWith(`${API_URL}/v1/servers/${serverId}`);
      expect(result).toEqual(mockResponse);
    });
  });

  // Connection Tests
  describe('Connection', () => {
    test('testConnection tests connection correctly', async () => {
      const connectionData = {
        hostname: '192.168.1.1',
        port: 22,
        username: 'admin',
        auth_type: 'password',
        password: 'password123'
      };
      
      const mockResponse = { success: true, message: 'Connection successful' };
      
      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });
      
      const result = await testConnection(connectionData);
      
      expect(mockedAxios.post).toHaveBeenCalledWith(`${API_URL}/v1/servers/test-connection`, connectionData);
      expect(result).toEqual(mockResponse);
    });

    test('getServerStatus fetches server status correctly', async () => {
      const serverId = 1;
      const mockStatus = {
        status: 'online',
        cpu_usage: 25.5,
        memory_usage: 40.2,
        disk_usage: 30.0,
        last_checked_at: '2023-01-01T12:00:00'
      };
      
      mockedAxios.get.mockResolvedValueOnce({ data: mockStatus });
      
      const result = await getServerStatus(serverId);
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/v1/servers/${serverId}/status`);
      expect(result).toEqual(mockStatus);
    });

    test('refreshServerStatus refreshes server status correctly', async () => {
      const serverId = 1;
      const mockStatus = {
        status: 'online',
        cpu_usage: 25.5,
        memory_usage: 40.2,
        disk_usage: 30.0,
        last_checked_at: '2023-01-01T12:00:00'
      };
      
      mockedAxios.post.mockResolvedValueOnce({ data: mockStatus });
      
      const result = await refreshServerStatus(serverId);
      
      expect(mockedAxios.post).toHaveBeenCalledWith(`${API_URL}/v1/servers/${serverId}/refresh-status`);
      expect(result).toEqual(mockStatus);
    });

    test('getServerDetails fetches server details correctly', async () => {
      const serverId = 1;
      const mockDetails = {
        id: serverId,
        name: 'Server 1',
        hostname: '192.168.1.1',
        port: 22,
        description: 'Server description',
        active: true,
        tags: [{ id: 1, name: 'Production', color: '#FF0000' }],
        credential: {
          username: 'admin',
          auth_type: 'password'
        },
        status: {
          status: 'online',
          cpu_usage: 25.5,
          memory_usage: 40.2,
          disk_usage: 30.0,
          last_checked_at: '2023-01-01T12:00:00'
        },
        system_info: {
          hostname: 'server1',
          os: 'Ubuntu 22.04 LTS',
          kernel: '5.15.0-56-generic',
          cpu_model: 'Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz',
          cpu_cores: 4,
          total_memory: 16384,
          total_disk: 512000
        },
        created_at: '2023-01-01T00:00:00',
        updated_at: '2023-01-01T00:00:00'
      };
      
      mockedAxios.get.mockResolvedValueOnce({ data: mockDetails });
      
      const result = await getServerDetails(serverId);
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/v1/servers/${serverId}/details`);
      expect(result).toEqual(mockDetails);
    });
  });

  // Error Handling Tests
  describe('Error Handling', () => {
    test('handles network errors correctly', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Network Error'));
      
      await expect(getServerTags()).rejects.toThrow('Network Error');
    });

    test('handles API errors correctly', async () => {
      const errorResponse = {
        response: {
          data: {
            detail: 'Not found'
          },
          status: 404
        }
      };
      
      mockedAxios.get.mockRejectedValueOnce(errorResponse);
      
      try {
        await getServerById(999);
        fail('Expected an error to be thrown');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
        expect(error.response.data.detail).toBe('Not found');
      }
    });
  });
});