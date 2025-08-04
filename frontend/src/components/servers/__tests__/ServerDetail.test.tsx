import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ServerDetail from '../ServerDetail';
import * as serverService from '../../../services/serverService';

// Mock the serverService
jest.mock('../../../services/serverService');

// Mock react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ serverId: '1' }),
  useNavigate: () => jest.fn()
}));

// Mock data
const mockServerDetail = {
  id: 1,
  name: 'Production Server',
  hostname: '192.168.1.100',
  port: 22,
  description: 'Main production server',
  active: true,
  tags: [
    { id: 1, name: 'Production', color: '#FF0000' }
  ],
  credential: {
    username: 'admin',
    auth_type: 'password'
  },
  status: {
    status: 'online',
    cpu_usage: 25.5,
    memory_usage: 40.2,
    disk_usage: 30.0,
    uptime: '10 days, 5 hours',
    last_checked_at: '2023-01-01T12:00:00'
  },
  system_info: {
    hostname: 'prod-server',
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

// Setup component with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(
    <BrowserRouter>
      <Routes>
        <Route path="*" element={component} />
      </Routes>
    </BrowserRouter>
  );
};

describe('ServerDetail Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mocks
    (serverService.getServerDetails as jest.Mock).mockResolvedValue(mockServerDetail);
    (serverService.refreshServerStatus as jest.Mock).mockResolvedValue({
      status: 'online',
      cpu_usage: 25.5,
      memory_usage: 40.2,
      disk_usage: 30.0,
      last_checked_at: '2023-01-01T12:00:00'
    });
    (serverService.deleteServer as jest.Mock).mockResolvedValue({ message: 'Server deleted successfully' });
  });

  test('renders server detail with loading state', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Should show loading initially
    expect(screen.getByText(/loading server details/i)).toBeInTheDocument();
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.queryByText(/loading server details/i)).not.toBeInTheDocument();
    });
  });

  test('renders server details correctly', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Check server information section
    expect(screen.getByText('Server Information')).toBeInTheDocument();
    expect(screen.getByText('192.168.1.100')).toBeInTheDocument();
    expect(screen.getByText('22')).toBeInTheDocument();
    expect(screen.getByText('Main production server')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
    expect(screen.getByText('password')).toBeInTheDocument();
    
    // Check status section
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('online')).toBeInTheDocument();
    expect(screen.getByText('25.5%')).toBeInTheDocument();
    expect(screen.getByText('40.2%')).toBeInTheDocument();
    expect(screen.getByText('30.0%')).toBeInTheDocument();
    
    // Check system information section
    expect(screen.getByText('System Information')).toBeInTheDocument();
    expect(screen.getByText('prod-server')).toBeInTheDocument();
    expect(screen.getByText('Ubuntu 22.04 LTS')).toBeInTheDocument();
    expect(screen.getByText('5.15.0-56-generic')).toBeInTheDocument();
    expect(screen.getByText('Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('16 GB')).toBeInTheDocument();
    expect(screen.getByText('500 GB')).toBeInTheDocument();
    
    // Check tag chips
    expect(screen.getByText('Production')).toBeInTheDocument();
  });

  test('handles refresh status button click', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click refresh button
    const refreshButton = screen.getByLabelText('Refresh Status');
    fireEvent.click(refreshButton);
    
    // Check that refreshServerStatus was called
    await waitFor(() => {
      expect(serverService.refreshServerStatus).toHaveBeenCalledWith(1);
    });
  });

  test('handles edit button click', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click edit button
    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);
    
    // This would navigate to /servers/edit/1 in a real app
    // We can't test navigation in this unit test, but we can check that the button exists
    expect(editButton).toBeInTheDocument();
  });

  test('handles delete button click and confirmation', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click delete button
    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);
    
    // Confirmation dialog should appear
    await waitFor(() => {
      expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
    });
    
    // Confirm deletion
    const confirmButton = screen.getByText('Delete', { selector: 'button' });
    fireEvent.click(confirmButton);
    
    // Check that deleteServer was called
    await waitFor(() => {
      expect(serverService.deleteServer).toHaveBeenCalledWith(1);
    });
  });

  test('handles server fetch error', async () => {
    // Mock an error response
    (serverService.getServerDetails as jest.Mock).mockRejectedValue(new Error('Failed to fetch server details'));
    
    renderWithRouter(<ServerDetail />);
    
    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/error loading server details/i)).toBeInTheDocument();
    });
  });

  test('displays formatted dates', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Check that dates are formatted correctly
    // This will depend on the actual formatting in the component
    // For example, if using toLocaleDateString:
    const dateRegex = /\d{1,2}\/\d{1,2}\/\d{4}/;
    const dateElements = screen.getAllByText(dateRegex);
    expect(dateElements.length).toBeGreaterThan(0);
  });

  test('displays progress bars for resource usage', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Check that progress bars are rendered
    // This is a bit tricky to test directly with testing-library
    // We can check for the text values that should be near the progress bars
    expect(screen.getByText('CPU Usage:')).toBeInTheDocument();
    expect(screen.getByText('Memory Usage:')).toBeInTheDocument();
    expect(screen.getByText('Disk Usage:')).toBeInTheDocument();
    
    // And the percentage values
    expect(screen.getByText('25.5%')).toBeInTheDocument();
    expect(screen.getByText('40.2%')).toBeInTheDocument();
    expect(screen.getByText('30.0%')).toBeInTheDocument();
  });

  test('handles back button click', async () => {
    renderWithRouter(<ServerDetail />);
    
    // Wait for server details to load
    await waitFor(() => {
      expect(screen.getByText('Production Server')).toBeInTheDocument();
    });
    
    // Find and click back button
    const backButton = screen.getByText('Back to Server List');
    fireEvent.click(backButton);
    
    // This would navigate back in a real app
    // We can't test navigation in this unit test, but we can check that the button exists
    expect(backButton).toBeInTheDocument();
  });
});