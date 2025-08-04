import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from app.services.server_monitor_service import ServerMonitorService
from app.services.ssh_service import SSHService
from app.models.server import Server, ServerStatus


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    mock_session = MagicMock()
    
    # Mock query results for servers
    server1 = Server(id=1, name="Server 1", hostname="192.168.1.100", port=22, active=True)
    server2 = Server(id=2, name="Server 2", hostname="192.168.1.101", port=22, active=True)
    inactive_server = Server(id=3, name="Inactive Server", hostname="192.168.1.102", port=22, active=False)
    
    # Mock credentials for servers
    server1.credential = MagicMock(username="user1", auth_type="password", password="pass1", private_key=None)
    server2.credential = MagicMock(username="user2", auth_type="key", password=None, private_key="key_content")
    inactive_server.credential = MagicMock(username="user3", auth_type="password", password="pass3", private_key=None)
    
    # Configure the mock session to return our test servers
    mock_session.query.return_value.filter.return_value.all.return_value = [server1, server2]
    
    # Configure the mock session to handle server status updates
    def mock_query_filter_first(model):
        mock_filter = MagicMock()
        
        def mock_filter_by(**kwargs):
            mock_first = MagicMock()
            mock_first.first.return_value = None  # No existing status
            return mock_first
        
        mock_filter.filter_by = mock_filter_by
        return mock_filter
    
    mock_session.query.side_effect = mock_query_filter_first
    
    return mock_session


@pytest.fixture
def mock_ssh_service():
    """Create a mock for the SSHService."""
    with patch('app.services.server_monitor_service.SSHService') as mock_service:
        # Configure update_server_status to return test data
        mock_service.update_server_status.return_value = {
            "status": "online",
            "cpu_usage": 25.5,
            "memory_usage": 40.2,
            "disk_usage": 30.0
        }
        
        # Configure get_system_info to return test data
        mock_service.get_system_info.return_value = {
            "uptime": "7 days",
            "memory": "16GB total, 8GB used",
            "disk": "100GB total, 30GB used",
            "cpu": "Intel Core i7",
            "os": "Ubuntu 20.04 LTS"
        }
        
        yield mock_service


@pytest.mark.asyncio
async def test_monitor_servers(mock_db_session, mock_ssh_service):
    """Test the monitor_servers method."""
    # Create a ServerMonitorService instance with our mocks
    service = ServerMonitorService()
    
    # Mock the get_db dependency
    with patch('app.services.server_monitor_service.get_db', return_value=mock_db_session):
        # Run the monitor_servers method
        await service.monitor_servers()
        
        # Check that the database session was used to query active servers
        mock_db_session.query.assert_called()
        
        # Check that SSHService.update_server_status was called for each active server
        assert mock_ssh_service.update_server_status.call_count == 2
        
        # Check that the session was committed
        mock_db_session.commit.assert_called()
        
        # Check that the session was closed
        mock_db_session.close.assert_called()


@pytest.mark.asyncio
async def test_start_monitoring(mock_db_session, mock_ssh_service):
    """Test starting the monitoring task."""
    # Create a ServerMonitorService instance
    service = ServerMonitorService()
    
    # Mock asyncio.create_task
    with patch('app.services.server_monitor_service.asyncio.create_task') as mock_create_task:
        # Mock the monitoring task
        mock_task = MagicMock()
        mock_create_task.return_value = mock_task
        
        # Start monitoring
        service.start_monitoring()
        
        # Check that create_task was called
        mock_create_task.assert_called_once()
        
        # Check that the task was stored
        assert service.monitoring_task == mock_task


@pytest.mark.asyncio
async def test_stop_monitoring():
    """Test stopping the monitoring task."""
    # Create a ServerMonitorService instance
    service = ServerMonitorService()
    
    # Create a mock task
    mock_task = MagicMock()
    mock_task.cancel = MagicMock()
    service.monitoring_task = mock_task
    
    # Stop monitoring
    service.stop_monitoring()
    
    # Check that the task was cancelled
    mock_task.cancel.assert_called_once()
    
    # Check that the task was cleared
    assert service.monitoring_task is None


@pytest.mark.asyncio
async def test_get_server_details(mock_db_session, mock_ssh_service):
    """Test getting server details."""
    # Create a ServerMonitorService instance
    service = ServerMonitorService()
    
    # Create a mock server
    server = Server(id=1, name="Test Server", hostname="192.168.1.100", port=22, active=True)
    server.credential = MagicMock(username="testuser", auth_type="password", password="testpass", private_key=None)
    
    # Mock the get_db dependency
    with patch('app.services.server_monitor_service.get_db', return_value=mock_db_session):
        # Configure the mock session to return our test server
        mock_db_session.query.return_value.filter.return_value.first.return_value = server
        
        # Get server details
        details = await service.get_server_details(1)
        
        # Check that SSHService.get_system_info was called
        mock_ssh_service.get_system_info.assert_called_once_with(
            hostname="192.168.1.100",
            port=22,
            username="testuser",
            auth_type="password",
            password="testpass",
            private_key=None
        )
        
        # Check the details
        assert details == {
            "uptime": "7 days",
            "memory": "16GB total, 8GB used",
            "disk": "100GB total, 30GB used",
            "cpu": "Intel Core i7",
            "os": "Ubuntu 20.04 LTS"
        }


@pytest.mark.asyncio
async def test_get_server_details_error(mock_db_session, mock_ssh_service):
    """Test error handling when getting server details."""
    # Create a ServerMonitorService instance
    service = ServerMonitorService()
    
    # Create a mock server
    server = Server(id=1, name="Test Server", hostname="192.168.1.100", port=22, active=True)
    server.credential = MagicMock(username="testuser", auth_type="password", password="testpass", private_key=None)
    
    # Configure SSHService to raise an exception
    mock_ssh_service.get_system_info.side_effect = Exception("Connection failed")
    
    # Mock the get_db dependency
    with patch('app.services.server_monitor_service.get_db', return_value=mock_db_session):
        # Configure the mock session to return our test server
        mock_db_session.query.return_value.filter.return_value.first.return_value = server
        
        # Get server details
        details = await service.get_server_details(1)
        
        # Check that SSHService.get_system_info was called
        mock_ssh_service.get_system_info.assert_called_once()
        
        # Check that error details were returned
        assert details == {"error": "Failed to get server details: Connection failed"}