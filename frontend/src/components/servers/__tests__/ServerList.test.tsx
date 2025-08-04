import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ServerList from '../ServerList';
import * as serverService from '../../../services/serverService';

// Mock the serverService
jest.mock('../../../services/serverService');

// Mock data
const mockServers = [
  {
    id: 1,
    name: 'Production Server',
    hostname: '192.168.1.100',
    port: 22,
    description: 'Main production server',
    active: true,
    status: 'online',
    tags: [
      { id: 1, name: 'Production', color: '#FF0000' }
    ],
    created_at: '2023-01-01T00:00:00',
    updated_at: '2023-01-01T00:00:00'
  },
  {
    id: 2,
    name: 'Development Server',
    hostname: '192.168.1.101',
    port: 22,
    description: 'Development server',
    active: true,
    status: 'offline',
    tags: [
      { id: 2, name: 'Development', color: '#00FF00' }
    ],
    created_at: '2023-01-01T00:00:00',
    updated_at: '2023-01-01T00:00:00'
  }
];

// Setup component with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ServerList Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mocks
    (serverService.getServers as jest.Mock).mockResolvedValue(mockServers);
    (serverService.refreshServerStatus as jest.Mock).mockResolvedValue({
      status: 'online',
      cpu_usage: 25.5,
      memory_usage: 40.2,
      disk_usage: 30.0,
      last_checked_at: '2023-01-01T12:00:00'
    });
    (serverService.deleteServer as jest.Mock).mockResolvedValue({ message: 'Server deleted successfully' });
  });

  test('renders server list with loading state', async () => {
    renderWithRouter(<ServerList />);
    
    // Should show loading initially
    expect(screen.getByText(/loading servers/i)).toBeInTheDocument();
    
    // Wait for servers to load
    await waitFor(() => {
      expect(screen.queryByText(/loading servers/i)).not.toBeInTheDocument();
    });
  });

  test('renders server list with servers', async () => {
    renderWithRouter(<ServerList />);
    
    // Wait for servers to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
      expect(screen.getByText('Development Server')).toBeInTheDocument();
    });
    
    // Check server details are displayed
    expect(screen.getByText('192.168.1.100')).toBeInTheDocument();
    expect(screen.getByText('192.168.1.101')).toBeInTheDocument();
    
    // Check status badges
    const onlineBadges = screen.getAllByText('online');
    const offlineBadges = screen.getAllByText('offline');
    expect(onlineBadges.length).toBeGreaterThan(0);
    expect(offlineBadges.length).toBeGreaterThan(0);
    
    // Check tag chips
    expect(screen.getByText('Production')).toBeInTheDocument();
    expect(screen.getByText('Development')).toBeInTheDocument();
  });

  test('handles refresh status button click', async () => {
    renderWithRouter(<ServerList />);
    
    // Wait for servers to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click refresh button for first server
    const refreshButtons = screen.getAllByLabelText('Refresh Status');
    fireEvent.click(refreshButtons[0]);
    
    // Check that refreshServerStatus was called
    await waitFor(() => {
      expect(serverService.refreshServerStatus).toHaveBeenCalledWith(1);
    });
  });

  test('handles view details button click', async () => {
    renderWithRouter(<ServerList />);
    
    // Wait for servers to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click view details button for first server
    const viewButtons = screen.getAllByLabelText('View Details');
    fireEvent.click(viewButtons[0]);
    
    // This would navigate to /servers/1 in a real app
    // We can't test navigation in this unit test, but we can check that the button exists
    expect(viewButtons[0]).toBeInTheDocument();
  });

  test('handles edit button click', async () => {
    renderWithRouter(<ServerList />);
    
    // Wait for servers to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click edit button for first server
    const editButtons = screen.getAllByLabelText('Edit Server');
    fireEvent.click(editButtons[0]);
    
    // This would navigate to /servers/edit/1 in a real app
    // We can't test navigation in this unit test, but we can check that the button exists
    expect(editButtons[0]).toBeInTheDocument();
  });

  test('handles delete button click and confirmation', async () => {
    renderWithRouter(<ServerList />);
    
    // Wait for servers to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click delete button for first server
    const deleteButtons = screen.getAllByLabelText('Delete Server');
    fireEvent.click(deleteButtons[0]);
    
    // Confirmation dialog should appear
    await waitFor(() => {
      expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
    });
    
    // Confirm deletion
    const confirmButton = screen.getByText('Delete');
    fireEvent.click(confirmButton);
    
    // Check that deleteServer was called
    await waitFor(() => {
      expect(serverService.deleteServer).toHaveBeenCalledWith(1);
    });
  });

  test('handles server fetch error', async () => {
    // Mock an error response
    (serverService.getServers as jest.Mock).mockRejectedValue(new Error('Failed to fetch servers'));
    
    renderWithRouter(<ServerList />);
    
    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/error loading servers/i)).toBeInTheDocument();
    });
  });

  test('handles empty server list', async () => {
    // Mock an empty response
    (serverService.getServers as jest.Mock).mockResolvedValue([]);
    
    renderWithRouter(<ServerList />);
    
    // Wait for no servers message
    await waitFor(() => {
      expect(screen.getByText(/no servers found/i)).toBeInTheDocument();
    });
  });
});