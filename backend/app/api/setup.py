import os
import subprocess
import sys
import shutil
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, EmailStr
from pathlib import Path

router = APIRouter()

class DBConfig(BaseModel):
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

class AdminUser(BaseModel):
    admin_user: str
    admin_email: EmailStr
    admin_password: str

class SetupPayload(DBConfig, AdminUser):
    pass

def run_command(command, cwd):
    try:
        subprocess.run(command, check=True, cwd=cwd, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(e.stderr)
        raise


def create_systemd_services(backend_dir, frontend_dir):
    """
    Create systemd service files for backend and frontend
    
    Args:
        backend_dir: Path to backend directory
        frontend_dir: Path to frontend directory
    """
    # Get absolute paths
    backend_abs_path = os.path.abspath(backend_dir)
    frontend_abs_path = os.path.abspath(frontend_dir)
    
    # Create backend service file
    backend_service = f"""[Unit]
    Description=SysUI Backend Service
    After=network.target mysql.service
    
    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory={backend_abs_path}
    ExecStart={sys.executable} {os.path.join(backend_abs_path, 'run.py')}
    Restart=always
    RestartSec=10
    Environment=PYTHONUNBUFFERED=1
    
    [Install]
    WantedBy=multi-user.target
    """
    
    # Create frontend service file
    frontend_service = f"""[Unit]
    Description=SysUI Frontend Service
    After=network.target sysui-backend.service
    Requires=sysui-backend.service
    
    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory={frontend_abs_path}
    ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0
    Restart=always
    RestartSec=10
    Environment=NODE_ENV=production
    
    [Install]
    WantedBy=multi-user.target
    """
    
    # Write service files
    try:
        # Create directory for service files if it doesn't exist
        services_dir = os.path.join(backend_abs_path, 'services')
        os.makedirs(services_dir, exist_ok=True)
        
        # Write backend service file
        with open(os.path.join(services_dir, 'sysui-backend.service'), 'w') as f:
            f.write(backend_service)
        
        # Write frontend service file
        with open(os.path.join(services_dir, 'sysui-frontend.service'), 'w') as f:
            f.write(frontend_service)
        
        print(f"Service files created in {services_dir}")
        print("To install the services, run:")
        print(f"sudo cp {os.path.join(services_dir, '*.service')} /etc/systemd/system/")
        print("sudo systemctl daemon-reload")
        print("sudo systemctl enable sysui-backend.service sysui-frontend.service")
        print("sudo systemctl start sysui-backend.service sysui-frontend.service")
    except Exception as e:
        print(f"Error creating service files: {str(e)}")
        raise

@router.post("/setup")
def setup_application(payload: SetupPayload):
    try:
        # 1. Copy env.example to .env and replace values
        backend_dir = '.'
        env_example_path = os.path.join(backend_dir, 'env.example')
        backend_env_path = os.path.join(backend_dir, '.env')
        
        # Check if env.example exists
        if not os.path.exists(env_example_path):
            raise HTTPException(status_code=500, detail="env.example file not found")
            
        # Copy env.example to .env
        shutil.copy2(env_example_path, backend_env_path)
        
        # Read the .env file
        with open(backend_env_path, 'r') as f:
            env_content = f.read()
        
        # Replace database connection string
        db_url = f"mysql+mysqlconnector://{payload.db_user}:{payload.db_password}@{payload.db_host}:{payload.db_port}/{payload.db_name}"
        env_content = env_content.replace("mysql+mysqlconnector://user:password@localhost/sysui", db_url)
        
        # Add admin user details
        env_content += f"\n# Admin User\nADMIN_USERNAME={payload.admin_user}\nADMIN_EMAIL={payload.admin_email}\nADMIN_PASSWORD={payload.admin_password}\n"
        
        # Write updated content back to .env file
        with open(backend_env_path, 'w') as f:
            f.write(env_content)
            
        print("Backend .env file created.")

        # 2. Install backend dependencies
        print("Installing backend dependencies...")
        run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=backend_dir)
        print("Backend dependencies installed.")

        # 3. Install frontend dependencies
        print("Installing frontend dependencies...")
        frontend_dir = os.path.join('..', 'frontend')
        run_command(["npm", "install"], cwd=frontend_dir)
        print("Frontend dependencies installed.")

        # 4. Initialize the database by creating all tables
        print("Initializing database...")
        # Import here to avoid circular imports
        from app.models.base import Base
        from app.db.session import engine
        from app.models.permission import Permission, PermissionEnum
        from app.models.user import User, UserRole
        from app.services.auth.auth_service import AuthService
        from app.db.session import get_db
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created.")
        
        # Initialize permissions
        db = next(get_db())
        try:
            # Check if permissions already exist
            existing_permissions = db.query(Permission).count()
            if existing_permissions == 0:
                # Create all permissions from the PermissionEnum
                for permission in PermissionEnum:
                    db.add(Permission(name=permission.value))
                
                db.commit()
                print(f"Initialized {len(PermissionEnum)} permissions.")
            else:
                print(f"Permissions already initialized ({existing_permissions} found).")
                
            # Create admin user
            admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
            if not admin:
                # Create admin user
                admin_username = payload.admin_user
                admin_email = payload.admin_email
                admin_password = payload.admin_password
                
                try:
                    # Create user
                    user = AuthService.create_user(
                        db=db,
                        username=admin_username,
                        email=admin_email,
                        password=admin_password,
                        full_name="System Administrator"
                    )
                    
                    # Set admin role
                    if user:
                        user.role = UserRole.ADMIN
                        db.commit()
                        
                        # Verify the admin user automatically
                        if user.verification_token:
                            # Ensure verification works
                            verification_result = AuthService.verify_email(db=db, token=user.verification_token)
                            if verification_result:
                                print(f"Admin user created and verified: {admin_username}")
                            else:
                                # Force verification if the normal method fails
                                user.is_verified = True
                                user.verification_token = None
                                db.commit()
                                print(f"Admin user created and force-verified: {admin_username}")
                        else:
                            # If no verification token, ensure user is verified
                            user.is_verified = True
                            db.commit()
                            print(f"Admin user created and verified: {admin_username}")
                    else:
                        print("Failed to create admin user.")
                except Exception as e:
                    db.rollback()
                    print(f"Error creating admin user: {e}")
            else:
                print("Admin user already exists.")
        finally:
            db.close()

        # 5. Create systemd service files
        print("Creating systemd service files...")
        create_systemd_services(backend_dir, frontend_dir)
        print("Systemd service files created.")

        return {"message": "Installation completed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))