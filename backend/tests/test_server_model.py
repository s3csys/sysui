import pytest
from sqlalchemy.orm import Session
from app.models.server import Server, ServerCredential, ServerStatus, ServerTag, server_tag_association
from app.core.security.password import verify_password


def test_server_model_creation(db: Session):
    """Test that a server can be created and retrieved from the database."""
    # Create a server
    server = Server(
        name="Test Server",
        hostname="192.168.1.100",
        port=22,
        description="Test server for unit tests",
        active=True
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    
    # Retrieve the server
    retrieved_server = db.query(Server).filter(Server.id == server.id).first()
    
    # Check that the server was created correctly
    assert retrieved_server is not None
    assert retrieved_server.name == "Test Server"
    assert retrieved_server.hostname == "192.168.1.100"
    assert retrieved_server.port == 22
    assert retrieved_server.description == "Test server for unit tests"
    assert retrieved_server.active is True
    assert retrieved_server.created_at is not None
    assert retrieved_server.updated_at is not None


def test_server_credential_creation(db: Session):
    """Test that server credentials can be created and retrieved from the database."""
    # Create a server
    server = Server(
        name="Credential Test Server",
        hostname="192.168.1.101",
        port=22,
        description="Test server for credential tests",
        active=True
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    
    # Create credentials for the server
    credential = ServerCredential(
        server_id=server.id,
        username="testuser",
        auth_type="password",
        password="securepassword",
        private_key=None
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)
    
    # Retrieve the credentials
    retrieved_credential = db.query(ServerCredential).filter(ServerCredential.server_id == server.id).first()
    
    # Check that the credentials were created correctly
    assert retrieved_credential is not None
    assert retrieved_credential.username == "testuser"
    assert retrieved_credential.auth_type == "password"
    assert retrieved_credential.private_key is None
    
    # Check that the password was hashed
    assert retrieved_credential.password != "securepassword"
    assert verify_password("securepassword", retrieved_credential.password)


def test_server_status_creation(db: Session):
    """Test that server status can be created and retrieved from the database."""
    # Create a server
    server = Server(
        name="Status Test Server",
        hostname="192.168.1.102",
        port=22,
        description="Test server for status tests",
        active=True
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    
    # Create status for the server
    status = ServerStatus(
        server_id=server.id,
        status="online",
        cpu_usage=25.5,
        memory_usage=40.2,
        disk_usage=30.0,
        last_checked_at=None  # This will be set automatically
    )
    db.add(status)
    db.commit()
    db.refresh(status)
    
    # Retrieve the status
    retrieved_status = db.query(ServerStatus).filter(ServerStatus.server_id == server.id).first()
    
    # Check that the status was created correctly
    assert retrieved_status is not None
    assert retrieved_status.status == "online"
    assert retrieved_status.cpu_usage == 25.5
    assert retrieved_status.memory_usage == 40.2
    assert retrieved_status.disk_usage == 30.0
    assert retrieved_status.last_checked_at is not None


def test_server_tag_creation(db: Session):
    """Test that server tags can be created and retrieved from the database."""
    # Create a tag
    tag = ServerTag(
        name="Production",
        description="Production servers",
        color="#FF0000"
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    # Retrieve the tag
    retrieved_tag = db.query(ServerTag).filter(ServerTag.id == tag.id).first()
    
    # Check that the tag was created correctly
    assert retrieved_tag is not None
    assert retrieved_tag.name == "Production"
    assert retrieved_tag.description == "Production servers"
    assert retrieved_tag.color == "#FF0000"


def test_server_tag_association(db: Session):
    """Test that servers can be associated with tags."""
    # Create a server
    server = Server(
        name="Tag Test Server",
        hostname="192.168.1.103",
        port=22,
        description="Test server for tag association tests",
        active=True
    )
    db.add(server)
    
    # Create tags
    tag1 = ServerTag(name="Production", description="Production servers", color="#FF0000")
    tag2 = ServerTag(name="Database", description="Database servers", color="#00FF00")
    db.add_all([tag1, tag2])
    db.commit()
    db.refresh(server)
    db.refresh(tag1)
    db.refresh(tag2)
    
    # Associate server with tags
    server.tags.append(tag1)
    server.tags.append(tag2)
    db.commit()
    
    # Retrieve the server with tags
    retrieved_server = db.query(Server).filter(Server.id == server.id).first()
    
    # Check that the tags were associated correctly
    assert retrieved_server is not None
    assert len(retrieved_server.tags) == 2
    assert any(tag.name == "Production" for tag in retrieved_server.tags)
    assert any(tag.name == "Database" for tag in retrieved_server.tags)
    
    # Check that the tags have the server associated
    retrieved_tag1 = db.query(ServerTag).filter(ServerTag.id == tag1.id).first()
    assert len(retrieved_tag1.servers) == 1
    assert retrieved_tag1.servers[0].id == server.id