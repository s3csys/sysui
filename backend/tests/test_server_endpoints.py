import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.server import Server, ServerTag, ServerCredential, ServerStatus
from app.api.v1.servers.schemas import (
    ServerCreate, ServerUpdate, ServerTagCreate, ServerTagUpdate,
    TestConnectionRequest
)
from app.services.ssh_service import SSHService
from app.services.server_monitor_service import ServerMonitorService


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    mock_session = MagicMock()
    return mock_session


@pytest.fixture
def mock_get_db(mock_db_session):
    """Mock the get_db dependency."""
    with patch("app.api.deps.get_db", return_value=mock_db_session):
        yield


@pytest.fixture
def mock_current_user():
    """Mock the current_user dependency."""
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.is_superuser = True
    
    with patch("app.api.deps.get_current_user", return_value=mock_user):
        yield mock_user


# Server Tag Tests
def test_get_server_tags(client, mock_get_db, mock_current_user, mock_db_session):
    """Test getting all server tags."""
    # Create mock tags
    tag1 = MagicMock(id=1, name="Production", description="Production servers", color="#FF0000")
    tag2 = MagicMock(id=2, name="Development", description="Development servers", color="#00FF00")
    
    # Configure the mock session to return our test tags
    mock_db_session.query.return_value.all.return_value = [tag1, tag2]
    
    # Make the request
    response = client.get("/api/v1/servers/tags")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Production"
    assert data[1]["name"] == "Development"


def test_create_server_tag(client, mock_get_db, mock_current_user, mock_db_session):
    """Test creating a server tag."""
    # Create a tag request
    tag_data = {
        "name": "Production",
        "description": "Production servers",
        "color": "#FF0000"
    }
    
    # Configure the mock session
    mock_db_session.query.return_value.filter.return_value.first.return_value = None  # Tag doesn't exist
    
    # Make the request
    response = client.post("/api/v1/servers/tags", json=tag_data)
    
    # Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Production"
    assert data["description"] == "Production servers"
    assert data["color"] == "#FF0000"
    
    # Check that the tag was added to the database
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_update_server_tag(client, mock_get_db, mock_current_user, mock_db_session):
    """Test updating a server tag."""
    # Create a tag update request
    tag_data = {
        "name": "Updated Production",
        "description": "Updated description",
        "color": "#0000FF"
    }
    
    # Create a mock tag
    tag = MagicMock(id=1, name="Production", description="Production servers", color="#FF0000")
    
    # Configure the mock session to return our test tag
    mock_db_session.query.return_value.filter.return_value.first.return_value = tag
    
    # Make the request
    response = client.put("/api/v1/servers/tags/1", json=tag_data)
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Production"
    assert data["description"] == "Updated description"
    assert data["color"] == "#0000FF"
    
    # Check that the tag was updated
    assert tag.name == "Updated Production"
    assert tag.description == "Updated description"
    assert tag.color == "#0000FF"
    mock_db_session.commit.assert_called_once()


def test_delete_server_tag(client, mock_get_db, mock_current_user, mock_db_session):
    """Test deleting a server tag."""
    # Create a mock tag
    tag = MagicMock(id=1, name="Production", description="Production servers", color="#FF0000")
    
    # Configure the mock session to return our test tag
    mock_db_session.query.return_value.filter.return_value.first.return_value = tag
    
    # Make the request
    response = client.delete("/api/v1/servers/tags/1")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Tag deleted successfully"
    
    # Check that the tag was deleted
    mock_db_session.delete.assert_called_once_with(tag)
    mock_db_session.commit.assert_called_once()


# Server Tests
def test_get_servers(client, mock_get_db, mock_current_user, mock_db_session):
    """Test getting all servers."""
    # Create mock servers
    server1 = MagicMock(id=1, name="Server 1", hostname="192.168.1.100", port=22, description="Test server 1", active=True)
    server2 = MagicMock(id=2, name="Server 2", hostname="192.168.1.101", port=22, description="Test server 2", active=True)
    
    # Configure server status
    server1.status = MagicMock(status="online", cpu_usage=25.5, memory_usage=40.2, disk_usage=30.0, last_checked_at="2023-01-01T12:00:00")
    server2.status = MagicMock(status="offline", cpu_usage=0, memory_usage=0, disk_usage=0, last_checked_at="2023-01-01T12:00:00")
    
    # Configure server tags
    tag1 = MagicMock(id=1, name="Production", description="Production servers", color="#FF0000")
    tag2 = MagicMock(id=2, name="Development", description="Development servers", color="#00FF00")
    server1.tags = [tag1]
    server2.tags = [tag2]
    
    # Configure the mock session to return our test servers
    mock_db_session.query.return_value.all.return_value = [server1, server2]
    
    # Make the request
    response = client.get("/api/v1/servers")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Server 1"
    assert data[0]["status"] == "online"
    assert data[0]["tags"][0]["name"] == "Production"
    assert data[1]["name"] == "Server 2"
    assert data[1]["status"] == "offline"
    assert data[1]["tags"][0]["name"] == "Development"


def test_create_server(client, mock_get_db, mock_current_user, mock_db_session):
    """Test creating a server."""
    # Create a server request
    server_data = {
        "name": "Test Server",
        "hostname": "192.168.1.100",
        "port": 22,
        "description": "Test server",
        "active": True,
        "tag_ids": [1],
        "credential": {
            "username": "testuser",
            "auth_type": "password",
            "password": "testpassword",
            "private_key": None
        }
    }
    
    # Create mock tags
    tag = MagicMock(id=1, name="Production", description="Production servers", color="#FF0000")
    
    # Configure the mock session
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [None, tag]  # Server doesn't exist, tag exists
    
    # Make the request
    response = client.post("/api/v1/servers", json=server_data)
    
    # Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Server"
    assert data["hostname"] == "192.168.1.100"
    assert data["port"] == 22
    assert data["description"] == "Test server"
    assert data["active"] is True
    assert len(data["tags"]) == 1
    assert data["tags"][0]["id"] == 1
    
    # Check that the server was added to the database
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called()


def test_get_server(client, mock_get_db, mock_current_user, mock_db_session):
    """Test getting a server by ID."""
    # Create a mock server
    server = MagicMock(id=1, name="Test Server", hostname="192.168.1.100", port=22, description="Test server", active=True)
    
    # Configure server status
    server.status = MagicMock(status="online", cpu_usage=25.5, memory_usage=40.2, disk_usage=30.0, last_checked_at="2023-01-01T12:00:00")
    
    # Configure server credential
    server.credential = MagicMock(username="testuser", auth_type="password")
    
    # Configure server tags
    tag = MagicMock(id=1, name="Production", description="Production servers", color="#FF0000")
    server.tags = [tag]
    
    # Configure the mock session to return our test server
    mock_db_session.query.return_value.filter.return_value.first.return_value = server
    
    # Make the request
    response = client.get("/api/v1/servers/1")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Server"
    assert data["hostname"] == "192.168.1.100"
    assert data["port"] == 22
    assert data["description"] == "Test server"
    assert data["active"] is True
    assert data["status"]["status"] == "online"
    assert data["status"]["cpu_usage"] == 25.5
    assert data["status"]["memory_usage"] == 40.2
    assert data["status"]["disk_usage"] == 30.0
    assert data["credential"]["username"] == "testuser"
    assert data["credential"]["auth_type"] == "password"
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "Production"


def test_update_server(client, mock_get_db, mock_current_user, mock_db_session):
    """Test updating a server."""
    # Create a server update request
    server_data = {
        "name": "Updated Server",
        "hostname": "192.168.1.200",
        "port": 2222,
        "description": "Updated description",
        "active": False,
        "tag_ids": [2],
        "credential": {
            "username": "updateduser",
            "auth_type": "password",
            "password": "updatedpassword",
            "private_key": None
        }
    }
    
    # Create a mock server
    server = MagicMock(id=1, name="Test Server", hostname="192.168.1.100", port=22, description="Test server", active=True)
    
    # Configure server credential
    server.credential = MagicMock(username="testuser", auth_type="password", password="testpassword", private_key=None)
    
    # Configure server tags
    old_tag = MagicMock(id=1, name="Production", description="Production servers", color="#FF0000")
    new_tag = MagicMock(id=2, name="Development", description="Development servers", color="#00FF00")
    server.tags = [old_tag]
    
    # Configure the mock session
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [server, new_tag]  # Server exists, new tag exists
    
    # Make the request
    response = client.put("/api/v1/servers/1", json=server_data)
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Server"
    assert data["hostname"] == "192.168.1.200"
    assert data["port"] == 2222
    assert data["description"] == "Updated description"
    assert data["active"] is False
    
    # Check that the server was updated
    assert server.name == "Updated Server"
    assert server.hostname == "192.168.1.200"
    assert server.port == 2222
    assert server.description == "Updated description"
    assert server.active is False
    mock_db_session.commit.assert_called()


def test_delete_server(client, mock_get_db, mock_current_user, mock_db_session):
    """Test deleting a server."""
    # Create a mock server
    server = MagicMock(id=1, name="Test Server", hostname="192.168.1.100", port=22, description="Test server", active=True)
    
    # Configure the mock session to return our test server
    mock_db_session.query.return_value.filter.return_value.first.return_value = server
    
    # Make the request
    response = client.delete("/api/v1/servers/1")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Server deleted successfully"
    
    # Check that the server was deleted
    mock_db_session.delete.assert_called_once_with(server)
    mock_db_session.commit.assert_called_once()


# SSH Connection Tests
def test_test_connection_success(client, mock_get_db, mock_current_user):
    """Test successful SSH connection test."""
    # Create a connection test request
    connection_data = {
        "hostname": "192.168.1.100",
        "port": 22,
        "username": "testuser",
        "auth_type": "password",
        "password": "testpassword",
        "private_key": None
    }
    
    # Mock the SSHService.test_connection method
    with patch("app.api.v1.servers.endpoints.SSHService.test_connection", return_value=True):
        # Make the request
        response = client.post("/api/v1/servers/test-connection", json=connection_data)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Connection successful"


def test_test_connection_failure(client, mock_get_db, mock_current_user):
    """Test failed SSH connection test."""
    # Create a connection test request
    connection_data = {
        "hostname": "192.168.1.100",
        "port": 22,
        "username": "testuser",
        "auth_type": "password",
        "password": "wrongpassword",
        "private_key": None
    }
    
    # Mock the SSHService.test_connection method
    with patch("app.api.v1.servers.endpoints.SSHService.test_connection", return_value=False):
        # Make the request
        response = client.post("/api/v1/servers/test-connection", json=connection_data)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Connection failed"


# Server Status Tests
def test_get_server_status(client, mock_get_db, mock_current_user, mock_db_session):
    """Test getting server status."""
    # Create a mock server
    server = MagicMock(id=1, name="Test Server", hostname="192.168.1.100", port=22, active=True)
    
    # Configure server credential
    server.credential = MagicMock(username="testuser", auth_type="password", password="testpassword", private_key=None)
    
    # Configure server status
    server.status = MagicMock(status="online", cpu_usage=25.5, memory_usage=40.2, disk_usage=30.0, last_checked_at="2023-01-01T12:00:00")
    
    # Configure the mock session to return our test server
    mock_db_session.query.return_value.filter.return_value.first.return_value = server
    
    # Make the request
    response = client.get("/api/v1/servers/1/status")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["cpu_usage"] == 25.5
    assert data["memory_usage"] == 40.2
    assert data["disk_usage"] == 30.0
    assert data["last_checked_at"] == "2023-01-01T12:00:00"


def test_refresh_server_status(client, mock_get_db, mock_current_user, mock_db_session):
    """Test refreshing server status."""
    # Create a mock server
    server = MagicMock(id=1, name="Test Server", hostname="192.168.1.100", port=22, active=True)
    
    # Configure server credential
    server.credential = MagicMock(username="testuser", auth_type="password", password="testpassword", private_key=None)
    
    # Configure server status
    server.status = MagicMock(status="online", cpu_usage=25.5, memory_usage=40.2, disk_usage=30.0, last_checked_at="2023-01-01T12:00:00")
    
    # Configure the mock session to return our test server
    mock_db_session.query.return_value.filter.return_value.first.return_value = server
    
    # Mock the SSHService.update_server_status method
    with patch("app.api.v1.servers.endpoints.SSHService.update_server_status") as mock_update_status:
        # Configure the mock to return updated status
        mock_update_status.return_value = {
            "status": "online",
            "cpu_usage": 30.0,
            "memory_usage": 45.0,
            "disk_usage": 35.0
        }
        
        # Make the request
        response = client.post("/api/v1/servers/1/refresh-status")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["cpu_usage"] == 30.0
        assert data["memory_usage"] == 45.0
        assert data["disk_usage"] == 35.0
        
        # Check that SSHService.update_server_status was called
        mock_update_status.assert_called_once_with(
            hostname="192.168.1.100",
            port=22,
            username="testuser",
            auth_type="password",
            password="testpassword",
            private_key=None
        )
        
        # Check that the status was updated in the database
        assert server.status.status == "online"
        assert server.status.cpu_usage == 30.0
        assert server.status.memory_usage == 45.0
        assert server.status.disk_usage == 35.0
        mock_db_session.commit.assert_called()


def test_get_server_details(client, mock_get_db, mock_current_user, mock_db_session):
    """Test getting server details."""
    # Create a mock server
    server = MagicMock(id=1, name="Test Server", hostname="192.168.1.100", port=22, active=True)
    
    # Configure the mock session to return our test server
    mock_db_session.query.return_value.filter.return_value.first.return_value = server
    
    # Mock the ServerMonitorService.get_server_details method
    with patch("app.api.v1.servers.endpoints.server_monitor_service.get_server_details") as mock_get_details:
        # Configure the mock to return server details
        mock_get_details.return_value = {
            "uptime": "7 days",
            "memory": "16GB total, 8GB used",
            "disk": "100GB total, 30GB used",
            "cpu": "Intel Core i7",
            "os": "Ubuntu 20.04 LTS"
        }
        
        # Make the request
        response = client.get("/api/v1/servers/1/details")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["uptime"] == "7 days"
        assert data["memory"] == "16GB total, 8GB used"
        assert data["disk"] == "100GB total, 30GB used"
        assert data["cpu"] == "Intel Core i7"
        assert data["os"] == "Ubuntu 20.04 LTS"
        
        # Check that ServerMonitorService.get_server_details was called
        mock_get_details.assert_called_once_with(1)