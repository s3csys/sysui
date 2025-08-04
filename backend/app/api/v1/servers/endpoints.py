from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.server import Server, ServerCredential, ServerStatus, ServerTag, server_tag_association
from app.services.ssh_service import SSHService
from app.services.server_monitor_service import ServerMonitorService
from .schemas import (
    ServerCreate, ServerUpdate, ServerResponse, ServerListResponse, 
    ServerDetailResponse, ServerTagCreate, ServerTagResponse, ServerTagUpdate,
    TestConnectionRequest, TestConnectionResponse
)

router = APIRouter()

# Server Tag endpoints
@router.get("/tags", response_model=List[ServerTagResponse])
async def get_server_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all server tags"""
    result = await db.execute(select(ServerTag))
    tags = result.scalars().all()
    return tags

@router.post("/tags", response_model=ServerTagResponse, status_code=status.HTTP_201_CREATED)
async def create_server_tag(
    tag: ServerTagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new server tag"""
    # Check if tag with same name already exists
    result = await db.execute(select(ServerTag).where(ServerTag.name == tag.name))
    existing_tag = result.scalars().first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag.name}' already exists"
        )
    
    # Create new tag
    db_tag = ServerTag(**tag.dict())
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag

@router.get("/tags/{tag_id}", response_model=ServerTagResponse)
async def get_server_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a server tag by ID"""
    result = await db.execute(select(ServerTag).where(ServerTag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    return tag

@router.put("/tags/{tag_id}", response_model=ServerTagResponse)
async def update_server_tag(
    tag_id: int,
    tag_update: ServerTagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a server tag"""
    # Get existing tag
    result = await db.execute(select(ServerTag).where(ServerTag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    
    # Check if name is being updated and if it already exists
    if tag_update.name and tag_update.name != tag.name:
        result = await db.execute(select(ServerTag).where(ServerTag.name == tag_update.name))
        existing_tag = result.scalars().first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_update.name}' already exists"
            )
    
    # Update tag
    update_data = tag_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)
    
    await db.commit()
    await db.refresh(tag)
    return tag

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a server tag"""
    # Get existing tag
    result = await db.execute(select(ServerTag).where(ServerTag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    
    # Delete tag
    await db.delete(tag)
    await db.commit()
    return None

# Server endpoints
@router.get("", response_model=List[ServerListResponse])
async def get_servers(
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all servers with optional filtering by tag"""
    query = select(Server)
    
    # Filter by tag if provided
    if tag:
        query = query.join(server_tag_association).join(ServerTag).where(ServerTag.name == tag)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    servers = result.scalars().all()
    
    # Convert tags to list of names for response
    server_list = []
    for server in servers:
        server_data = ServerListResponse.from_orm(server)
        server_data.tags = [tag.name for tag in server.tags]
        server_list.append(server_data)
    
    return server_list

@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server: ServerCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new server"""
    # Check if server with same IP already exists
    result = await db.execute(select(Server).where(Server.ip_address == server.ip_address))
    existing_server = result.scalars().first()
    if existing_server:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Server with IP address '{server.ip_address}' already exists"
        )
    
    # Extract credentials and tags from request
    credentials_data = server.credentials.dict()
    tags = server.tags or []
    
    # Create server without credentials and tags
    server_data = server.dict(exclude={"credentials", "tags"})
    db_server = Server(**server_data)
    
    # Create credentials
    db_credentials = ServerCredential(**credentials_data)
    
    # Handle password hashing if auth_type is password
    if db_credentials.auth_type == "password" and db_credentials.password:
        db_credentials.set_password(db_credentials.password)
    
    # Associate credentials with server
    db_server.credentials = db_credentials
    
    # Create initial status
    db_status = ServerStatus(
        is_online=False,
        last_check=None,
        error_message=None
    )
    db_server.status = db_status
    
    # Add server to database
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)
    
    # Add tags
    if tags:
        for tag_name in tags:
            # Get or create tag
            result = await db.execute(select(ServerTag).where(ServerTag.name == tag_name))
            tag = result.scalars().first()
            if not tag:
                tag = ServerTag(name=tag_name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            
            # Add tag to server
            db_server.tags.append(tag)
        
        await db.commit()
        await db.refresh(db_server)
    
    # Test connection in background
    background_tasks.add_task(SSHService.update_server_status, db_server)
    
    return db_server

@router.get("/{server_id}", response_model=ServerDetailResponse)
async def get_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a server by ID with detailed information"""
    # Get server
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalars().first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server with ID {server_id} not found"
        )
    
    # Get system info if server is online
    system_info = None
    if server.status and server.status.is_online:
        monitor_service = ServerMonitorService(db)
        server_info = await monitor_service.get_server_info(server_id)
        if server_info:
            system_info = server_info.get("system_info")
    
    # Create response
    response = ServerDetailResponse.from_orm(server)
    response.tags = [ServerTagResponse.from_orm(tag) for tag in server.tags]
    response.system_info = system_info
    
    return response

@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: int,
    server_update: ServerUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a server"""
    # Get existing server
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalars().first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server with ID {server_id} not found"
        )
    
    # Check if IP is being updated and if it already exists
    if server_update.ip_address and server_update.ip_address != server.ip_address:
        result = await db.execute(
            select(Server).where(
                Server.ip_address == server_update.ip_address,
                Server.id != server_id
            )
        )
        existing_server = result.scalars().first()
        if existing_server:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Server with IP address '{server_update.ip_address}' already exists"
            )
    
    # Update server fields
    server_data = server_update.dict(exclude={"credentials", "tags"}, exclude_unset=True)
    for key, value in server_data.items():
        setattr(server, key, value)
    
    # Update credentials if provided
    if server_update.credentials:
        credentials_data = server_update.credentials.dict(exclude_unset=True)
        
        # Handle password update if provided
        if "password" in credentials_data and credentials_data["password"]:
            server.credentials.set_password(credentials_data["password"])
            del credentials_data["password"]
        
        # Update other credential fields
        for key, value in credentials_data.items():
            if key != "password":  # Skip password as it's handled separately
                setattr(server.credentials, key, value)
    
    # Update tags if provided
    if server_update.tags is not None:
        # Clear existing tags
        server.tags = []
        
        # Add new tags
        for tag_name in server_update.tags:
            # Get or create tag
            result = await db.execute(select(ServerTag).where(ServerTag.name == tag_name))
            tag = result.scalars().first()
            if not tag:
                tag = ServerTag(name=tag_name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            
            # Add tag to server
            server.tags.append(tag)
    
    # Commit changes
    await db.commit()
    await db.refresh(server)
    
    # Test connection in background if connection details changed
    connection_changed = (
        server_update.ip_address is not None or
        server_update.ssh_port is not None or
        (server_update.credentials is not None and (
            server_update.credentials.username is not None or
            server_update.credentials.auth_type is not None or
            server_update.credentials.password is not None or
            server_update.credentials.private_key is not None
        ))
    )
    
    if connection_changed:
        background_tasks.add_task(SSHService.update_server_status, server)
    
    return server

@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a server"""
    # Get existing server
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalars().first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server with ID {server_id} not found"
        )
    
    # Delete server (will cascade to credentials and status)
    await db.delete(server)
    await db.commit()
    return None

@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_connection(
    connection_data: TestConnectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Test SSH connection to a server without creating it"""
    # Create temporary server and credential objects
    server = Server(
        id=0,  # Temporary ID
        name="Test Connection",
        ip_address=connection_data.ip_address,
        ssh_port=connection_data.ssh_port,
        is_active=True
    )
    
    credentials = ServerCredential(
        server_id=0,  # Temporary ID
        username=connection_data.username,
        auth_type=connection_data.auth_type
    )
    
    # Handle password or private key
    if connection_data.auth_type == "password" and connection_data.password:
        credentials.password = connection_data.password  # Not hashed for testing
    elif connection_data.auth_type == "key" and connection_data.private_key:
        credentials.private_key = connection_data.private_key
    
    # Associate credentials with server
    server.credentials = credentials
    
    # Test connection
    is_success, error_message = await SSHService.test_connection(server)
    
    # Return result
    return TestConnectionResponse(
        success=is_success,
        message="Connection successful" if is_success else error_message or "Connection failed"
    )

@router.post("/{server_id}/check", response_model=ServerDetailResponse)
async def check_server_status(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check server status and get detailed information"""
    # Get server
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalars().first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server with ID {server_id} not found"
        )
    
    # Update server status
    await SSHService.update_server_status(server)
    await db.commit()
    await db.refresh(server)
    
    # Get system info if server is online
    system_info = None
    if server.status and server.status.is_online:
        monitor_service = ServerMonitorService(db)
        server_info = await monitor_service.get_server_info(server_id)
        if server_info:
            system_info = server_info.get("system_info")
    
    # Create response
    response = ServerDetailResponse.from_orm(server)
    response.tags = [ServerTagResponse.from_orm(tag) for tag in server.tags]
    response.system_info = system_info
    
    return response