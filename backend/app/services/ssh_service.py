import paramiko
import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime

from app.models.server import Server, ServerCredential

logger = logging.getLogger(__name__)

class SSHConnectionError(Exception):
    """Exception raised for SSH connection errors"""
    pass

class SSHService:
    """Service for handling SSH connections to servers"""
    
    @staticmethod
    async def test_connection(server: Server) -> Tuple[bool, Optional[str]]:
        """Test SSH connection to a server
        
        Args:
            server: Server model instance
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not server.credentials:
            return False, "No credentials found for server"
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Get credentials
            creds = server.credentials
            
            # Connect based on auth type
            if creds.auth_type == 'password':
                client.connect(
                    hostname=server.ip_address,
                    port=server.ssh_port,
                    username=creds.username,
                    password=creds.password,  # This is already hashed, we need to handle this
                    timeout=10
                )
            elif creds.auth_type == 'key':
                if not creds.private_key:
                    return False, "No private key provided"
                
                # Create key object from private key string
                private_key = paramiko.RSAKey.from_private_key(
                    file_obj=None, 
                    password=None, 
                    pkey_obj=creds.private_key
                )
                
                client.connect(
                    hostname=server.ip_address,
                    port=server.ssh_port,
                    username=creds.username,
                    pkey=private_key,
                    timeout=10
                )
            else:
                return False, f"Unsupported authentication type: {creds.auth_type}"
            
            # If we get here, connection was successful
            return True, None
            
        except Exception as e:
            logger.error(f"SSH connection error to {server.ip_address}: {str(e)}")
            return False, str(e)
        finally:
            client.close()
    
    @staticmethod
    async def execute_command(server: Server, command: str) -> Tuple[bool, str, Optional[str]]:
        """Execute a command on the server via SSH
        
        Args:
            server: Server model instance
            command: Command to execute
            
        Returns:
            Tuple of (success: bool, output: str, error: Optional[str])
        """
        if not server.credentials:
            return False, "", "No credentials found for server"
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Get credentials
            creds = server.credentials
            
            # Connect based on auth type
            if creds.auth_type == 'password':
                client.connect(
                    hostname=server.ip_address,
                    port=server.ssh_port,
                    username=creds.username,
                    password=creds.password,  # This is already hashed, we need to handle this
                    timeout=10
                )
            elif creds.auth_type == 'key':
                if not creds.private_key:
                    return False, "", "No private key provided"
                
                # Create key object from private key string
                private_key = paramiko.RSAKey.from_private_key(
                    file_obj=None, 
                    password=None, 
                    pkey_obj=creds.private_key
                )
                
                client.connect(
                    hostname=server.ip_address,
                    port=server.ssh_port,
                    username=creds.username,
                    pkey=private_key,
                    timeout=10
                )
            else:
                return False, "", f"Unsupported authentication type: {creds.auth_type}"
            
            # Execute command
            stdin, stdout, stderr = client.exec_command(command)
            
            # Get output
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            # Check exit status
            exit_status = stdout.channel.recv_exit_status()
            success = exit_status == 0
            
            return success, output, error if error else None
            
        except Exception as e:
            logger.error(f"SSH command execution error on {server.ip_address}: {str(e)}")
            return False, "", str(e)
        finally:
            client.close()
    
    @staticmethod
    async def get_system_info(server: Server) -> Dict[str, Any]:
        """Get basic system information from the server
        
        Args:
            server: Server model instance
            
        Returns:
            Dictionary with system information
        """
        info = {
            "hostname": None,
            "os": None,
            "kernel": None,
            "uptime": None,
            "cpu_count": None,
            "memory_total": None,
            "memory_free": None,
            "disk_usage": None,
        }
        
        # Get hostname
        success, output, _ = await SSHService.execute_command(server, "hostname")
        if success:
            info["hostname"] = output.strip()
        
        # Get OS info
        success, output, _ = await SSHService.execute_command(
            server, "cat /etc/os-release | grep PRETTY_NAME | cut -d\"=\" -f2"
        )
        if success:
            info["os"] = output.strip().strip('"')
        
        # Get kernel version
        success, output, _ = await SSHService.execute_command(server, "uname -r")
        if success:
            info["kernel"] = output.strip()
        
        # Get uptime
        success, output, _ = await SSHService.execute_command(server, "uptime -p")
        if success:
            info["uptime"] = output.strip()
        
        # Get CPU count
        success, output, _ = await SSHService.execute_command(
            server, "nproc --all"
        )
        if success:
            try:
                info["cpu_count"] = int(output.strip())
            except ValueError:
                pass
        
        # Get memory info
        success, output, _ = await SSHService.execute_command(
            server, "free -m | grep Mem"
        )
        if success:
            try:
                parts = output.strip().split()
                if len(parts) >= 3:
                    info["memory_total"] = f"{parts[1]} MB"
                    info["memory_free"] = f"{parts[3]} MB"
            except (ValueError, IndexError):
                pass
        
        # Get disk usage
        success, output, _ = await SSHService.execute_command(
            server, "df -h / | tail -1"
        )
        if success:
            try:
                parts = output.strip().split()
                if len(parts) >= 5:
                    info["disk_usage"] = parts[4]  # Usage percentage
            except (ValueError, IndexError):
                pass
        
        return info
    
    @staticmethod
    async def update_server_status(server: Server) -> None:
        """Update the server status by testing the connection
        
        Args:
            server: Server model instance
        """
        is_online, error_message = await SSHService.test_connection(server)
        
        # Update server status
        if server.status:
            server.status.is_online = is_online
            server.status.last_check = datetime.now().isoformat()
            server.status.error_message = error_message
        else:
            # Create new status if it doesn't exist
            from app.models.server import ServerStatus
            server.status = ServerStatus(
                is_online=is_online,
                last_check=datetime.now().isoformat(),
                error_message=error_message
            )