import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ServersPage from '../ServersPage';

// Mock the components used in ServersPage
jest.mock('../../components/servers/ServerList', () => {
  return function MockServerList() {
    return <div data-testid="server-list">Server List Component</div>;
  };
});

jest.mock('../../components/servers/ServerDetail', () => {
  return function MockServerDetail() {
    return <div data-testid="server-detail">Server Detail Component</div>;
  };
});

jest.mock('../../components/servers/ServerForm', () => {
  return function MockServerForm() {
    return <div data-testid="server-form">Server Form Component</div>;
  };
});

jest.mock('../../components/servers/ServerTagManager', () => {
  return function MockServerTagManager() {
    return <div data-testid="server-tag-manager">Server Tag Manager Component</div>;
  };
});

// Mock react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => ({
    pathname: '/servers'
  }),
  useNavigate: () => jest.fn()
}));

// Setup component with router
const renderWithRouter = (initialPath: string) => {
  // Override the mocked useLocation to return the initialPath
  (require('react-router-dom') as any).useLocation = () => ({
    pathname: initialPath
  });

  return render(
    <BrowserRouter>
      <Routes>
        <Route path="/servers/*" element={<ServersPage />} />
      </Routes>
    </BrowserRouter>
  );
};

describe('ServersPage Component', () => {
  test('renders the page title', () => {
    renderWithRouter('/servers');
    expect(screen.getByText('Server Management')).toBeInTheDocument();
  });

  test('renders tabs correctly', () => {
    renderWithRouter('/servers');
    expect(screen.getByText('Server List')).toBeInTheDocument();
    expect(screen.getByText('Manage Tags')).toBeInTheDocument();
  });

  test('renders ServerList component on default route', () => {
    renderWithRouter('/servers');
    expect(screen.getByTestId('server-list')).toBeInTheDocument();
  });

  test('renders ServerList component on /servers route', () => {
    renderWithRouter('/servers');
    expect(screen.getByTestId('server-list')).toBeInTheDocument();
  });

  test('renders ServerDetail component on /servers/view/:id route', () => {
    renderWithRouter('/servers/view/1');
    expect(screen.getByTestId('server-detail')).toBeInTheDocument();
  });

  test('renders ServerForm component on /servers/add route', () => {
    renderWithRouter('/servers/add');
    expect(screen.getByTestId('server-form')).toBeInTheDocument();
  });

  test('renders ServerForm component on /servers/edit/:id route', () => {
    renderWithRouter('/servers/edit/1');
    expect(screen.getByTestId('server-form')).toBeInTheDocument();
  });

  test('renders ServerTagManager component on /servers/tags route', () => {
    renderWithRouter('/servers/tags');
    expect(screen.getByTestId('server-tag-manager')).toBeInTheDocument();
  });

  test('activates correct tab based on route', () => {
    // Test Server List tab activation
    renderWithRouter('/servers');
    const serverListTab = screen.getByText('Server List');
    expect(serverListTab.closest('button')).toHaveAttribute('aria-selected', 'true');
    
    // Test Manage Tags tab activation
    renderWithRouter('/servers/tags');
    const manageTagsTab = screen.getByText('Manage Tags');
    expect(manageTagsTab.closest('button')).toHaveAttribute('aria-selected', 'true');
  });
});