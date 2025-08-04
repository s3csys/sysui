import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.future import select

from app.models.server import Server, ServerStatus
from app.services.ssh_service import SSHService

logger = logging.getLogger(__name__)

class ServerMonitorService:
    """Service for monitoring server status and health"""
    
    def __init__(self, db: Session):
        """Initialize the server monitor service
        
        Args:
            db: Database session
        """
        self.db = db
        self._monitoring_task = None
        self._is_running = False
        self._check_interval = 300  # 5 minutes in seconds
    
    async def start_monitoring(self, check_interval: int = 300) -> None:
        """Start the server monitoring background task
        
        Args:
            check_interval: Interval in seconds between status checks
        """
        if self._is_running:
            logger.warning("Server monitoring is already running")
            return
        
        self._check_interval = check_interval
        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitor_servers())
        logger.info(f"Started server monitoring with interval of {check_interval} seconds")
    
    async def stop_monitoring(self) -> None:
        """Stop the server monitoring background task"""
        if not self._is_running or not self._monitoring_task:
            logger.warning("Server monitoring is not running")
            return
        
        self._is_running = False
        if not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self._monitoring_task = None
        logger.info("Stopped server monitoring")
    
    async def _monitor_servers(self) -> None:
        """Background task to periodically check server status"""
        while self._is_running:
            try:
                # Get all active servers
                result = await self.db.execute(select(Server).where(Server.is_active == True))
                servers = result.scalars().all()
                
                # Check each server's status
                for server in servers:
                    await self._check_server_status(server)
                
                # Commit changes
                await self.db.commit()
                
            except Exception as e:
                logger.error(f"Error in server monitoring: {str(e)}")
                await self.db.rollback()
            
            # Wait for next check interval
            await asyncio.sleep(self._check_interval)
    
    async def _check_server_status(self, server: Server) -> None:
        """Check the status of a single server
        
        Args:
            server: Server model instance
        """
        try:
            # Skip if last check was recent (within 80% of check interval)
            if server.status and server.status.last_check:
                last_check = datetime.fromisoformat(server.status.last_check)
                time_since_check = datetime.now() - last_check
                if time_since_check < timedelta(seconds=self._check_interval * 0.8):
                    return
            
            # Update server status
            await SSHService.update_server_status(server)
            
            logger.info(f"Updated status for server {server.name} ({server.ip_address}): " 
                      f"{'Online' if server.status.is_online else 'Offline'}")
            
        except Exception as e:
            logger.error(f"Error checking status for server {server.name} ({server.ip_address}): {str(e)}")
    
    async def check_all_servers(self) -> List[Dict[str, Any]]:
        """Check status of all active servers immediately
        
        Returns:
            List of server status dictionaries
        """
        try:
            # Get all active servers
            result = await self.db.execute(select(Server).where(Server.is_active == True))
            servers = result.scalars().all()
            
            # Check each server's status
            status_list = []
            for server in servers:
                await self._check_server_status(server)
                
                # Add status to list
                if server.status:
                    status_list.append({
                        "id": server.id,
                        "name": server.name,
                        "ip_address": server.ip_address,
                        "is_online": server.status.is_online,
                        "last_check": server.status.last_check,
                        "error_message": server.status.error_message
                    })
            
            # Commit changes
            await self.db.commit()
            
            return status_list
            
        except Exception as e:
            logger.error(f"Error checking all servers: {str(e)}")
            await self.db.rollback()
            return []
    
    async def get_server_info(self, server_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a server
        
        Args:
            server_id: ID of the server
            
        Returns:
            Dictionary with server information or None if server not found
        """
        try:
            # Get server by ID
            result = await self.db.execute(select(Server).where(Server.id == server_id))
            server = result.scalars().first()
            
            if not server:
                return None
            
            # Update server status
            await SSHService.update_server_status(server)
            
            # Get system info if server is online
            system_info = {}
            if server.status and server.status.is_online:
                system_info = await SSHService.get_system_info(server)
            
            # Commit changes
            await self.db.commit()
            
            # Build response
            server_info = {
                "id": server.id,
                "name": server.name,
                "ip_address": server.ip_address,
                "ssh_port": server.ssh_port,
                "description": server.description,
                "is_active": server.is_active,
                "status": {
                    "is_online": server.status.is_online if server.status else False,
                    "last_check": server.status.last_check if server.status else None,
                    "error_message": server.status.error_message if server.status else None
                },
                "system_info": system_info,
                "tags": [tag.name for tag in server.tags] if server.tags else []
            }
            
            return server_info
            
        except Exception as e:
            logger.error(f"Error getting server info for ID {server_id}: {str(e)}")
            await self.db.rollback()
            return None