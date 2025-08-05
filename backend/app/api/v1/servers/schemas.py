from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime

# Base schemas
class ServerTagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class ServerCredentialBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    auth_type: str = Field(..., pattern='^(password|key)$')
    
    @validator('auth_type')
    def validate_auth_type(cls, v):
        if v not in ['password', 'key']:
            raise ValueError('auth_type must be either "password" or "key"')
        return v

class ServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: str = Field(..., min_length=1, max_length=45)
    ssh_port: int = Field(22, ge=1, le=65535)
    description: Optional[str] = Field(None, max_length=200)
    is_active: bool = True

# Create schemas
class ServerCredentialCreate(ServerCredentialBase):
    password: Optional[str] = Field(None, min_length=1)
    private_key: Optional[str] = None
    
    @root_validator(skip_on_failure=True)
    def validate_auth_credentials(cls, values):
        auth_type = values.get('auth_type')
        password = values.get('password')
        private_key = values.get('private_key')
        
        if auth_type == 'password' and not password:
            raise ValueError('password is required when auth_type is "password"')
        elif auth_type == 'key' and not private_key:
            raise ValueError('private_key is required when auth_type is "key"')
            
        return values

class ServerTagCreate(ServerTagBase):
    pass

class ServerCreate(ServerBase):
    credentials: ServerCredentialCreate
    tags: Optional[List[str]] = None  # List of tag names

# Update schemas
class ServerCredentialUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    auth_type: Optional[str] = Field(None, pattern='^(password|key)$')
    password: Optional[str] = None
    private_key: Optional[str] = None
    
    @validator('auth_type')
    def validate_auth_type(cls, v):
        if v is not None and v not in ['password', 'key']:
            raise ValueError('auth_type must be either "password" or "key"')
        return v

class ServerTagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class ServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ip_address: Optional[str] = Field(None, min_length=1, max_length=45)
    ssh_port: Optional[int] = Field(None, ge=1, le=65535)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    credentials: Optional[ServerCredentialUpdate] = None
    tags: Optional[List[str]] = None  # List of tag names

# Response schemas
class ServerTagResponse(ServerTagBase):
    id: int
    
    class Config:
        from_attributes = True

class ServerStatusResponse(BaseModel):
    is_online: bool
    last_check: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class ServerCredentialResponse(BaseModel):
    username: str
    auth_type: str
    # Note: We don't include password or private_key in responses
    
    class Config:
        from_attributes = True

class ServerResponse(ServerBase):
    id: int
    credentials: ServerCredentialResponse
    status: Optional[ServerStatusResponse] = None
    tags: List[ServerTagResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ServerListResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    is_active: bool
    status: Optional[ServerStatusResponse] = None
    tags: List[str] = []  # Just tag names for list view
    
    class Config:
        from_attributes = True

class ServerDetailResponse(ServerResponse):
    system_info: Optional[Dict[str, Any]] = None

# Test connection schema
class TestConnectionRequest(BaseModel):
    ip_address: str = Field(..., min_length=1, max_length=45)
    ssh_port: int = Field(22, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=50)
    auth_type: str = Field(..., pattern='^(password|key)$')
    password: Optional[str] = None
    private_key: Optional[str] = None
    
    @root_validator(skip_on_failure=True)
    def validate_auth_credentials(cls, values):
        auth_type = values.get('auth_type')
        password = values.get('password')
        private_key = values.get('private_key')
        
        if auth_type == 'password' and not password:
            raise ValueError('password is required when auth_type is "password"')
        elif auth_type == 'key' and not private_key:
            raise ValueError('private_key is required when auth_type is "key"')
            
        return values

class TestConnectionResponse(BaseModel):
    success: bool
    message: str