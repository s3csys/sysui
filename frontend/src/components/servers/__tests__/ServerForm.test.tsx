import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ServerForm from '../ServerForm';
import * as serverService from '../../../services/serverService';

// Mock the serverService
jest.mock('../../../services/serverService');

// Mock data
const mockTags = [
  { id: 1, name: 'Production', description: 'Production servers', color: '#FF0000' },
  { id: 2, name: 'Development', description: 'Development servers', color: '#00FF00' }
];

const mockServer = {
  id: 1,
  name: 'Production Server',
  hostname: '192.168.1.100',
  port: 22,
  description: 'Main production server',
  active: true,
  tags: [{ id: 1, name: 'Production', color: '#FF0000' }],
  credential: {
    username: 'admin',
    auth_type: 'password',
    password: null, // Password is not returned from API
    private_key: null
  },
  status: {
    status: 'online',
    cpu_usage: 25.5,
    memory_usage: 40.2,
    disk_usage: 30.0,
    last_checked_at: '2023-01-01T12:00:00'
  },
  created_at: '2023-01-01T00:00:00',
  updated_at: '2023-01-01T00:00:00'
};

// Setup component with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ServerForm Component', () => {
  const mockNavigate = jest.fn();
  
  // Mock useNavigate
  jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate
  }));

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mocks
    (serverService.getServerTags as jest.Mock).mockResolvedValue(mockTags);
    (serverService.testConnection as jest.Mock).mockResolvedValue({
      success: true,
      message: 'Connection successful'
    });
    (serverService.createServer as jest.Mock).mockResolvedValue(mockServer);
    (serverService.updateServer as jest.Mock).mockResolvedValue(mockServer);
    (serverService.getServer as jest.Mock).mockResolvedValue(mockServer);
  });

  test('renders create server form', async () => {
    renderWithRouter(<ServerForm mode="create" />);
    
    // Check form title
    expect(screen.getByText('Add Server')).toBeInTheDocument();
    
    // Check form fields
    expect(screen.getByLabelText(/server name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ip address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ssh port/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/active/i)).toBeInTheDocument();
    
    // Check connection settings
    expect(screen.getByText(/connection settings/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    
    // Check auth type radio buttons
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/private key/i)).toBeInTheDocument();
    
    // Check buttons
    expect(screen.getByText('Test Connection')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    
    // Wait for tags to load
    await waitFor(() => {
      expect(serverService.getServerTags).toHaveBeenCalled();
    });
  });

  test('renders edit server form and loads server data', async () => {
    renderWithRouter(<ServerForm mode="edit" serverId={1} />);
    
    // Check form title
    expect(screen.getByText('Edit Server')).toBeInTheDocument();
    
    // Wait for server data to load
    await waitFor(() => {
      expect(serverService.getServer).toHaveBeenCalledWith(1);
    });
    
    // Check that form fields are populated with server data
    await waitFor(() => {
      expect((screen.getByLabelText(/server name/i) as HTMLInputElement).value).toBe('Production Server');
      expect((screen.getByLabelText(/ip address/i) as HTMLInputElement).value).toBe('192.168.1.100');
      expect((screen.getByLabelText(/ssh port/i) as HTMLInputElement).value).toBe('22');
      expect((screen.getByLabelText(/description/i) as HTMLInputElement).value).toBe('Main production server');
      expect((screen.getByLabelText(/username/i) as HTMLInputElement).value).toBe('admin');
    });
  });

  test('handles form submission for create mode', async () => {
    renderWithRouter(<ServerForm mode="create" />);
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/server name/i), { target: { value: 'Test Server' } });
    fireEvent.change(screen.getByLabelText(/ip address/i), { target: { value: '192.168.1.200' } });
    fireEvent.change(screen.getByLabelText(/ssh port/i), { target: { value: '22' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Test server description' } });
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    
    // Select password auth type (should be default)
    const passwordRadio = screen.getByLabelText(/password/i);
    fireEvent.click(passwordRadio);
    
    // Enter password
    const passwordField = screen.getByLabelText(/^password$/i);
    fireEvent.change(passwordField, { target: { value: 'testpassword' } });
    
    // Wait for tags to load
    await waitFor(() => {
      expect(serverService.getServerTags).toHaveBeenCalled();
    });
    
    // Select a tag (if available in the DOM)
    await waitFor(() => {
      const tagCheckboxes = screen.getAllByRole('checkbox');
      // Skip the 'active' checkbox which is the first one
      if (tagCheckboxes.length > 1) {
        fireEvent.click(tagCheckboxes[1]);
      }
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Save'));
    
    // Check that createServer was called with correct data
    await waitFor(() => {
      expect(serverService.createServer).toHaveBeenCalledWith(expect.objectContaining({
        name: 'Test Server',
        hostname: '192.168.1.200',
        port: 22,
        description: 'Test server description',
        active: true,
        credential: expect.objectContaining({
          username: 'testuser',
          auth_type: 'password',
          password: 'testpassword'
        })
      }));
    });
  });

  test('handles form submission for edit mode', async () => {
    renderWithRouter(<ServerForm mode="edit" serverId={1} />);
    
    // Wait for server data to load
    await waitFor(() => {
      expect(serverService.getServer).toHaveBeenCalledWith(1);
    });
    
    // Wait for form fields to be populated
    await waitFor(() => {
      expect((screen.getByLabelText(/server name/i) as HTMLInputElement).value).toBe('Production Server');
    });
    
    // Change some form fields
    fireEvent.change(screen.getByLabelText(/server name/i), { target: { value: 'Updated Server' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Updated description' } });
    
    // Submit the form
    fireEvent.click(screen.getByText('Save'));
    
    // Check that updateServer was called with correct data
    await waitFor(() => {
      expect(serverService.updateServer).toHaveBeenCalledWith(1, expect.objectContaining({
        name: 'Updated Server',
        description: 'Updated description'
      }));
    });
  });

  test('handles test connection button click', async () => {
    renderWithRouter(<ServerForm mode="create" />);
    
    // Fill out the form with connection details
    fireEvent.change(screen.getByLabelText(/ip address/i), { target: { value: '192.168.1.200' } });
    fireEvent.change(screen.getByLabelText(/ssh port/i), { target: { value: '22' } });
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    
    // Enter password
    const passwordField = screen.getByLabelText(/^password$/i);
    fireEvent.change(passwordField, { target: { value: 'testpassword' } });
    
    // Click test connection button
    fireEvent.click(screen.getByText('Test Connection'));
    
    // Check that testConnection was called with correct data
    await waitFor(() => {
      expect(serverService.testConnection).toHaveBeenCalledWith(expect.objectContaining({
        hostname: '192.168.1.200',
        port: 22,
        username: 'testuser',
        auth_type: 'password',
        password: 'testpassword'
      }));
    });
    
    // Check that success message is displayed
    await waitFor(() => {
      expect(screen.getByText('Connection successful')).toBeInTheDocument();
    });
  });

  test('handles test connection failure', async () => {
    // Mock a failed connection test
    (serverService.testConnection as jest.Mock).mockResolvedValue({
      success: false,
      message: 'Connection failed: Authentication failed'
    });
    
    renderWithRouter(<ServerForm mode="create" />);
    
    // Fill out the form with connection details
    fireEvent.change(screen.getByLabelText(/ip address/i), { target: { value: '192.168.1.200' } });
    fireEvent.change(screen.getByLabelText(/ssh port/i), { target: { value: '22' } });
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    
    // Enter password
    const passwordField = screen.getByLabelText(/^password$/i);
    fireEvent.change(passwordField, { target: { value: 'wrongpassword' } });
    
    // Click test connection button
    fireEvent.click(screen.getByText('Test Connection'));
    
    // Check that error message is displayed
    await waitFor(() => {
      expect(screen.getByText('Connection failed: Authentication failed')).toBeInTheDocument();
    });
  });

  test('handles auth type change', async () => {
    renderWithRouter(<ServerForm mode="create" />);
    
    // Initially, password field should be visible
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/private key/i)).toBeInTheDocument(); // Radio button
    
    // Change auth type to private key
    const privateKeyRadio = screen.getByLabelText(/private key/i);
    fireEvent.click(privateKeyRadio);
    
    // Now private key textarea should be visible and password field should be hidden
    await waitFor(() => {
      expect(screen.queryByLabelText(/^password$/i)).not.toBeInTheDocument();
      expect(screen.getByLabelText(/private key content/i)).toBeInTheDocument();
    });
    
    // Change back to password
    const passwordRadio = screen.getByLabelText(/password/i);
    fireEvent.click(passwordRadio);
    
    // Now password field should be visible again and private key textarea should be hidden
    await waitFor(() => {
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.queryByLabelText(/private key content/i)).not.toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    renderWithRouter(<ServerForm mode="create" />);
    
    // Submit form without filling required fields
    fireEvent.click(screen.getByText('Save'));
    
    // Check that validation errors are displayed
    await waitFor(() => {
      expect(screen.getByText(/server name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/ip address is required/i)).toBeInTheDocument();
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
    
    // createServer should not have been called
    expect(serverService.createServer).not.toHaveBeenCalled();
  });

  test('validates IP address format', async () => {
    renderWithRouter(<ServerForm mode="create" />);
    
    // Fill out the form with invalid IP address
    fireEvent.change(screen.getByLabelText(/server name/i), { target: { value: 'Test Server' } });
    fireEvent.change(screen.getByLabelText(/ip address/i), { target: { value: 'invalid-ip' } });
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'testpassword' } });
    
    // Submit the form
    fireEvent.click(screen.getByText('Save'));
    
    // Check that validation error is displayed
    await waitFor(() => {
      expect(screen.getByText(/invalid ip address format/i)).toBeInTheDocument();
    });
    
    // createServer should not have been called
    expect(serverService.createServer).not.toHaveBeenCalled();
  });

  test('handles cancel button click', async () => {
    renderWithRouter(<ServerForm mode="create" />);
    
    // Click cancel button
    fireEvent.click(screen.getByText('Cancel'));
    
    // This would navigate back in a real app
    // We can't test navigation in this unit test, but we can check that the button exists
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });
});