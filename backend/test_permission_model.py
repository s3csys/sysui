from app.models.permission import Permission, PermissionEnum
from app.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create an in-memory SQLite database for testing
engine = create_engine('sqlite:///:memory:')

# Create all tables
Base.metadata.create_all(bind=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Test creating a permission
try:
    # Create a permission
    permission = Permission(name=PermissionEnum.VIEW_USERS.value)
    db.add(permission)
    db.commit()
    print("Successfully created permission with name as primary key")
    
    # Verify the permission was created
    db_permission = db.query(Permission).filter(Permission.name == PermissionEnum.VIEW_USERS.value).first()
    if db_permission:
        print(f"Retrieved permission: {db_permission.name}")
    else:
        print("Failed to retrieve permission")
        
except Exception as e:
    print(f"Error: {str(e)}")
    db.rollback()
finally:
    db.close()