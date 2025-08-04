from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.security.password import get_password_hash, verify_password

# Association table for server tags
server_tag_association = Table(
    'server_tag_association',
    Base.metadata,
    Column('server_id', Integer, ForeignKey('server.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('server_tag.id', ondelete='CASCADE'), primary_key=True)
)


class ServerTag(Base):
    """Model for server tags/groups"""
    __tablename__ = 'server_tag'
    
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(200), nullable=True)
    
    # Relationship with servers
    servers = relationship(
        "Server",
        secondary=server_tag_association,
        back_populates="tags"
    )
    
    def __repr__(self):
        return f"<ServerTag {self.name}>"


class Server(Base):
    """Model for server details"""
    __tablename__ = 'server'
    
    name = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 can be up to 45 chars
    ssh_port = Column(Integer, nullable=False, default=22)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    credentials = relationship("ServerCredential", back_populates="server", uselist=False, cascade="all, delete-orphan")
    status = relationship("ServerStatus", back_populates="server", uselist=False, cascade="all, delete-orphan")
    tags = relationship(
        "ServerTag",
        secondary=server_tag_association,
        back_populates="servers"
    )
    
    def __repr__(self):
        return f"<Server {self.name} ({self.ip_address})>"


class ServerCredential(Base):
    """Model for server authentication credentials"""
    __tablename__ = 'server_credential'
    
    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, unique=True)
    username = Column(String(50), nullable=False)
    auth_type = Column(String(10), nullable=False)  # 'password' or 'key'
    password = Column(String(100), nullable=True)  # Hashed password if auth_type is 'password'
    private_key = Column(Text, nullable=True)  # SSH private key if auth_type is 'key'
    
    # Relationship with server
    server = relationship("Server", back_populates="credentials")
    
    def __repr__(self):
        return f"<ServerCredential for server_id={self.server_id}>"
    
    def set_password(self, password: str) -> None:
        """Hash and store the password"""
        self.password = get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify the password"""
        if not self.password:
            return False
        return verify_password(password, self.password)


class ServerStatus(Base):
    """Model for tracking server connection status"""
    __tablename__ = 'server_status'
    
    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, unique=True)
    is_online = Column(Boolean, nullable=False, default=False)
    last_check = Column(String(50), nullable=True)  # ISO format timestamp
    error_message = Column(String(200), nullable=True)
    
    # Relationship with server
    server = relationship("Server", back_populates="status")
    
    def __repr__(self):
        status = "Online" if self.is_online else "Offline"
        return f"<ServerStatus {status} for server_id={self.server_id}>"