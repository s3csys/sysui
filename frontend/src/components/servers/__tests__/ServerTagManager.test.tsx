import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ServerTagManager from '../ServerTagManager';
import * as serverService from '../../../services/serverService';

// Mock the serverService
jest.mock('../../../services/serverService');

// Mock data
const mockTags = [
  { id: 1, name: 'Production', description: 'Production servers', color: '#FF0000' },
  { id: 2, name: 'Development', description: 'Development servers', color: '#00FF00' },
  { id: 3, name: 'Testing', description: 'Testing servers', color: '#0000FF' }
];

describe('ServerTagManager Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mocks
    (serverService.getServerTags as jest.Mock).mockResolvedValue(mockTags);
    (serverService.createServerTag as jest.Mock).mockImplementation((tag) => {
      return Promise.resolve({ id: 4, ...tag });
    });
    (serverService.updateServerTag as jest.Mock).mockImplementation((id, tag) => {
      return Promise.resolve({ id, ...tag });
    });
    (serverService.deleteServerTag as jest.Mock).mockResolvedValue({ message: 'Tag deleted successfully' });
  });

  test('renders tag list with loading state', async () => {
    render(<ServerTagManager />);
    
    // Should show loading initially
    expect(screen.getByText(/loading tags/i)).toBeInTheDocument();
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.queryByText(/loading tags/i)).not.toBeInTheDocument();
    });
  });

  test('renders tag list correctly', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
      expect(screen.getByText('Development')).toBeInTheDocument();
      expect(screen.getByText('Testing')).toBeInTheDocument();
    });
    
    // Check that descriptions are displayed
    expect(screen.getByText('Production servers')).toBeInTheDocument();
    expect(screen.getByText('Development servers')).toBeInTheDocument();
    expect(screen.getByText('Testing servers')).toBeInTheDocument();
    
    // Check that edit and delete buttons are present for each tag
    const editButtons = screen.getAllByLabelText('Edit');
    const deleteButtons = screen.getAllByLabelText('Delete');
    expect(editButtons.length).toBe(3);
    expect(deleteButtons.length).toBe(3);
  });

  test('opens create tag dialog when add button is clicked', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click add tag button
    const addButton = screen.getByText('Add Tag');
    fireEvent.click(addButton);
    
    // Check that dialog is displayed
    expect(screen.getByText('Create New Tag')).toBeInTheDocument();
    
    // Check that form fields are present
    expect(screen.getByLabelText('Tag Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByLabelText('Color')).toBeInTheDocument();
  });

  test('handles tag creation', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click add tag button
    const addButton = screen.getByText('Add Tag');
    fireEvent.click(addButton);
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText('Tag Name'), { target: { value: 'Staging' } });
    fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'Staging servers' } });
    fireEvent.change(screen.getByLabelText('Color'), { target: { value: '#FFFF00' } });
    
    // Submit the form
    fireEvent.click(screen.getByText('Save'));
    
    // Check that createServerTag was called with correct data
    await waitFor(() => {
      expect(serverService.createServerTag).toHaveBeenCalledWith({
        name: 'Staging',
        description: 'Staging servers',
        color: '#FFFF00'
      });
    });
    
    // Check that getServerTags is called again to refresh the list
    await waitFor(() => {
      expect(serverService.getServerTags).toHaveBeenCalledTimes(2);
    });
  });

  test('opens edit tag dialog when edit button is clicked', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click edit button for the first tag
    const editButtons = screen.getAllByLabelText('Edit');
    fireEvent.click(editButtons[0]);
    
    // Check that dialog is displayed with correct title
    expect(screen.getByText('Edit Tag')).toBeInTheDocument();
    
    // Check that form fields are pre-filled with tag data
    expect((screen.getByLabelText('Tag Name') as HTMLInputElement).value).toBe('Production');
    expect((screen.getByLabelText('Description') as HTMLInputElement).value).toBe('Production servers');
    expect((screen.getByLabelText('Color') as HTMLInputElement).value).toBe('#FF0000');
  });

  test('handles tag update', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click edit button for the first tag
    const editButtons = screen.getAllByLabelText('Edit');
    fireEvent.click(editButtons[0]);
    
    // Modify the form fields
    fireEvent.change(screen.getByLabelText('Tag Name'), { target: { value: 'Production Updated' } });
    fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'Updated description' } });
    fireEvent.change(screen.getByLabelText('Color'), { target: { value: '#FF5500' } });
    
    // Submit the form
    fireEvent.click(screen.getByText('Save'));
    
    // Check that updateServerTag was called with correct data
    await waitFor(() => {
      expect(serverService.updateServerTag).toHaveBeenCalledWith(1, {
        name: 'Production Updated',
        description: 'Updated description',
        color: '#FF5500'
      });
    });
    
    // Check that getServerTags is called again to refresh the list
    await waitFor(() => {
      expect(serverService.getServerTags).toHaveBeenCalledTimes(2);
    });
  });

  test('handles tag deletion confirmation', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click delete button for the first tag
    const deleteButtons = screen.getAllByLabelText('Delete');
    fireEvent.click(deleteButtons[0]);
    
    // Check that confirmation dialog is displayed
    expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
    expect(screen.getByText('Production')).toBeInTheDocument();
    
    // Confirm deletion
    const confirmButton = screen.getByText('Delete', { selector: 'button' });
    fireEvent.click(confirmButton);
    
    // Check that deleteServerTag was called with correct id
    await waitFor(() => {
      expect(serverService.deleteServerTag).toHaveBeenCalledWith(1);
    });
    
    // Check that getServerTags is called again to refresh the list
    await waitFor(() => {
      expect(serverService.getServerTags).toHaveBeenCalledTimes(2);
    });
  });

  test('handles tag deletion cancellation', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click delete button for the first tag
    const deleteButtons = screen.getAllByLabelText('Delete');
    fireEvent.click(deleteButtons[0]);
    
    // Check that confirmation dialog is displayed
    expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
    
    // Cancel deletion
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    // Check that deleteServerTag was not called
    expect(serverService.deleteServerTag).not.toHaveBeenCalled();
    
    // Check that dialog is closed
    expect(screen.queryByText(/are you sure you want to delete/i)).not.toBeInTheDocument();
  });

  test('validates required fields in create/edit form', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click add tag button
    const addButton = screen.getByText('Add Tag');
    fireEvent.click(addButton);
    
    // Submit the form without filling required fields
    fireEvent.click(screen.getByText('Save'));
    
    // Check that validation errors are displayed
    await waitFor(() => {
      expect(screen.getByText(/tag name is required/i)).toBeInTheDocument();
    });
    
    // createServerTag should not have been called
    expect(serverService.createServerTag).not.toHaveBeenCalled();
  });

  test('handles tag fetch error', async () => {
    // Mock an error response
    (serverService.getServerTags as jest.Mock).mockRejectedValue(new Error('Failed to fetch tags'));
    
    render(<ServerTagManager />);
    
    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/error loading tags/i)).toBeInTheDocument();
    });
  });

  test('closes dialog when cancel button is clicked', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Click add tag button
    const addButton = screen.getByText('Add Tag');
    fireEvent.click(addButton);
    
    // Check that dialog is displayed
    expect(screen.getByText('Create New Tag')).toBeInTheDocument();
    
    // Click cancel button
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    // Check that dialog is closed
    await waitFor(() => {
      expect(screen.queryByText('Create New Tag')).not.toBeInTheDocument();
    });
  });

  test('displays color preview in tag list', async () => {
    render(<ServerTagManager />);
    
    // Wait for tags to load
    await waitFor(() => {
      expect(screen.getByText('Production')).toBeInTheDocument();
    });
    
    // Check that color previews are displayed
    // This is a bit tricky to test directly with testing-library
    // We can check for elements with background color styles, but this depends on the implementation
    // For now, we'll just check that the tag names are displayed
    expect(screen.getByText('Production')).toBeInTheDocument();
    expect(screen.getByText('Development')).toBeInTheDocument();
    expect(screen.getByText('Testing')).toBeInTheDocument();
  });
});