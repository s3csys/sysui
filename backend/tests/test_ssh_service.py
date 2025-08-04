import pytest
from unittest.mock import patch, MagicMock
from app.services.ssh_service import SSHService, SSHConnectionError


@pytest.fixture
def mock_paramiko_client():
    """Create a mock for paramiko.SSHClient."""
    with patch('app.services.ssh_service.paramiko.SSHClient') as mock_client:
        # Setup the mock client
        instance = mock_client.return_value
        instance.connect = MagicMock()
        instance.exec_command = MagicMock()
        
        # Mock the channel and streams
        channel = MagicMock()
        stdin = MagicMock()
        stdout = MagicMock()
        stderr = MagicMock()
        
        # Configure exec_command to return our mocks
        instance.exec_command.return_value = (stdin, stdout, stderr)
        
        # Configure stdout to return test data
        stdout.channel = channel
        stdout.read.return_value = b"Command output"
        stdout.readlines.return_value = [b"Line 1\n", b"Line 2\n"]
        
        # Configure stderr
        stderr.read.return_value = b""
        
        # Configure channel
        channel.recv_exit_status.return_value = 0
        
        yield instance


def test_test_connection_success(mock_paramiko_client):
    """Test successful SSH connection."""
    # Configure the mock to simulate successful connection
    result = SSHService.test_connection(
        hostname="192.168.1.100",
        port=22,
        username="testuser",
        auth_type="password",
        password="password123",
        private_key=None
    )
    
    # Check that connect was called with the right parameters
    mock_paramiko_client.connect.assert_called_once_with(
        hostname="192.168.1.100",
        port=22,
        username="testuser",
        password="password123",
        pkey=None,
        timeout=5
    )
    
    # Check the result
    assert result is True


def test_test_connection_with_key(mock_paramiko_client):
    """Test SSH connection with private key authentication."""
    with patch('app.services.ssh_service.paramiko.RSAKey.from_private_key') as mock_key:
        # Configure the mock key
        mock_key_instance = MagicMock()
        mock_key.return_value = mock_key_instance
        
        # Test the connection
        result = SSHService.test_connection(
            hostname="192.168.1.100",
            port=22,
            username="testuser",
            auth_type="key",
            password=None,
            private_key="PRIVATE KEY CONTENT"
        )
        
        # Check that the key was loaded
        mock_key.assert_called_once()
        
        # Check that connect was called with the right parameters
        mock_paramiko_client.connect.assert_called_once_with(
            hostname="192.168.1.100",
            port=22,
            username="testuser",
            password=None,
            pkey=mock_key_instance,
            timeout=5
        )
        
        # Check the result
        assert result is True


def test_test_connection_failure(mock_paramiko_client):
    """Test SSH connection failure."""
    # Configure the mock to simulate connection failure
    mock_paramiko_client.connect.side_effect = Exception("Connection failed")
    
    # Test the connection
    result = SSHService.test_connection(
        hostname="192.168.1.100",
        port=22,
        username="testuser",
        auth_type="password",
        password="wrong_password",
        private_key=None
    )
    
    # Check the result
    assert result is False


def test_execute_command_success(mock_paramiko_client):
    """Test successful command execution."""
    # Configure the mock
    stdout = mock_paramiko_client.exec_command.return_value[1]
    stdout.read.return_value = b"Command output"
    
    # Execute the command
    output = SSHService.execute_command(
        hostname="192.168.1.100",
        port=22,
        username="testuser",
        auth_type="password",
        password="password123",
        private_key=None,
        command="ls -la"
    )
    
    # Check that connect and exec_command were called
    mock_paramiko_client.connect.assert_called_once()
    mock_paramiko_client.exec_command.assert_called_once_with("ls -la")
    
    # Check the output
    assert output == "Command output"


def test_execute_command_failure(mock_paramiko_client):
    """Test command execution failure."""
    # Configure the mock to simulate command failure
    channel = mock_paramiko_client.exec_command.return_value[1].channel
    channel.recv_exit_status.return_value = 1
    stderr = mock_paramiko_client.exec_command.return_value[2]
    stderr.read.return_value = b"Command failed"
    
    # Test the command execution
    with pytest.raises(SSHConnectionError) as excinfo:
        SSHService.execute_command(
            hostname="192.168.1.100",
            port=22,
            username="testuser",
            auth_type="password",
            password="password123",
            private_key=None,
            command="invalid_command"
        )
    
    # Check the error message
    assert "Command failed with exit code 1" in str(excinfo.value)


def test_get_system_info(mock_paramiko_client):
    """Test getting system information."""
    # Configure the mock to return different outputs for different commands
    def mock_exec_command(command):
        stdin = MagicMock()
        stdout = MagicMock()
        stderr = MagicMock()
        channel = MagicMock()
        stdout.channel = channel
        channel.recv_exit_status.return_value = 0
        stderr.read.return_value = b""
        
        if "uptime" in command:
            stdout.read.return_value = b" 12:34:56 up 7 days, 2:34, 1 user, load average: 0.01, 0.05, 0.10"
        elif "free" in command:
            stdout.read.return_value = b"              total        used        free      shared  buff/cache   available\nMem:        16280560     1224304    13018912      118784     2037344    14767304\nSwap:        2097148           0     2097148"
        elif "df" in command:
            stdout.read.return_value = b"Filesystem     1K-blocks    Used Available Use% Mounted on\n/dev/sda1      103081248 3800000  99281248   4% /"
        elif "cat /proc/cpuinfo" in command:
            stdout.read.return_value = b"processor\t: 0\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 142\nmodel name\t: Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz\n"
        elif "cat /etc/os-release" in command:
            stdout.read.return_value = b"NAME=\"Ubuntu\"\nVERSION=\"20.04.4 LTS (Focal Fossa)\"\nID=ubuntu\nID_LIKE=debian\n"
        else:
            stdout.read.return_value = b"Unknown command"
        
        return stdin, stdout, stderr
    
    # Set the side effect for exec_command
    mock_paramiko_client.exec_command.side_effect = mock_exec_command
    
    # Get system info
    system_info = SSHService.get_system_info(
        hostname="192.168.1.100",
        port=22,
        username="testuser",
        auth_type="password",
        password="password123",
        private_key=None
    )
    
    # Check that connect was called
    mock_paramiko_client.connect.assert_called_once()
    
    # Check that exec_command was called multiple times
    assert mock_paramiko_client.exec_command.call_count > 1
    
    # Check the system info
    assert "uptime" in system_info
    assert "memory" in system_info
    assert "disk" in system_info
    assert "cpu" in system_info
    assert "os" in system_info
    
    # Check specific values
    assert "7 days" in system_info["uptime"]
    assert "16280560" in system_info["memory"]
    assert "4%" in system_info["disk"]
    assert "Intel(R) Core(TM) i7-8565U" in system_info["cpu"]
    assert "Ubuntu 20.04.4 LTS" in system_info["os"]


def test_update_server_status(mock_paramiko_client):
    """Test updating server status."""
    # Configure the mock to return different outputs for different commands
    def mock_exec_command(command):
        stdin = MagicMock()
        stdout = MagicMock()
        stderr = MagicMock()
        channel = MagicMock()
        stdout.channel = channel
        channel.recv_exit_status.return_value = 0
        stderr.read.return_value = b""
        
        if "top -bn1" in command:
            stdout.read.return_value = b"top - 12:34:56 up 7 days,  2:34,  1 user,  load average: 0.01, 0.05, 0.10\nTasks: 100 total,   1 running,  99 sleeping,   0 stopped,   0 zombie\n%Cpu(s):  5.0 us,  2.0 sy,  0.0 ni, 93.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st\nMiB Mem :  16280.6 total,  13018.9 free,   1224.3 used,   2037.3 buff/cache\nMiB Swap:   2097.1 total,   2097.1 free,      0.0 used.  14767.3 avail Mem"
        elif "df" in command:
            stdout.read.return_value = b"Filesystem     1K-blocks    Used Available Use% Mounted on\n/dev/sda1      103081248 3800000  99281248   4% /"
        else:
            stdout.read.return_value = b"Unknown command"
        
        return stdin, stdout, stderr
    
    # Set the side effect for exec_command
    mock_paramiko_client.exec_command.side_effect = mock_exec_command
    
    # Update server status
    status = SSHService.update_server_status(
        hostname="192.168.1.100",
        port=22,
        username="testuser",
        auth_type="password",
        password="password123",
        private_key=None
    )
    
    # Check that connect was called
    mock_paramiko_client.connect.assert_called_once()
    
    # Check that exec_command was called multiple times
    assert mock_paramiko_client.exec_command.call_count > 1
    
    # Check the status
    assert status["status"] == "online"
    assert status["cpu_usage"] == 7.0  # 5.0 us + 2.0 sy
    assert status["memory_usage"] == 7.52  # 1224.3 / 16280.6 * 100
    assert status["disk_usage"] == 4.0  # 4%