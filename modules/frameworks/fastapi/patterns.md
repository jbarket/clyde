# FastAPI Patterns and Best Practices

## API Design Patterns

### RESTful Endpoint Design
```python
# src/myapp/api/api_v1/endpoints/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.user import User, UserCreate, UserUpdate
from ...crud.user import user_crud
from ..deps import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users with pagination."""
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    # Check if user already exists
    existing_user = user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = user_crud.create(db, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user by ID."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user by ID."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_crud.remove(db, id=user_id)
    return {"message": "User deleted successfully"}
```

### Response Models and Status Codes
```python
from pydantic import BaseModel
from typing import Optional, Any

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

@router.post("/users/", 
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        409: {"model": ErrorResponse, "description": "Conflict"},
    }
)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Implementation
    pass
```

## Authentication and Authorization

### JWT Token Handling
```python
# src/myapp/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm="HS256"
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None
```

### Role-Based Access Control
```python
from enum import Enum
from typing import List
from fastapi import HTTPException, status

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

def require_roles(allowed_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Usage in endpoints
@router.delete("/admin/users/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    # Only admins can access this endpoint
    pass
```

## Request Validation and Error Handling

### Advanced Pydantic Validation
```python
from pydantic import BaseModel, validator, root_validator
from typing import Optional
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    age: Optional[int] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 18 or v > 120):
            raise ValueError('Age must be between 18 and 120')
        return v

    @root_validator
    def validate_passwords_match(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        if password != confirm_password:
            raise ValueError('Passwords do not match')
        return values
```

### Custom Exception Handling
```python
# src/myapp/core/exceptions.py
from fastapi import HTTPException, status

class BusinessLogicError(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class UserNotFoundError(BusinessLogicError):
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with ID {user_id} not found",
            error_code="USER_NOT_FOUND"
        )

class InsufficientPermissionsError(BusinessLogicError):
    def __init__(self):
        super().__init__(
            message="Not enough permissions to perform this action",
            error_code="INSUFFICIENT_PERMISSIONS"
        )

# Exception handlers in main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(BusinessLogicError)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
            "error_code": exc.error_code
        }
    )
```

## Background Tasks and Async Patterns

### Background Task Implementation
```python
from fastapi import BackgroundTasks
from ..services.email_service import send_welcome_email

@router.post("/users/", response_model=User)
def create_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = user_crud.create(db, obj_in=user_in)
    
    # Send welcome email in background
    background_tasks.add_task(
        send_welcome_email,
        email=user.email,
        name=user.name
    )
    
    return user
```

### Async Database Operations
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

async_engine = create_async_engine(settings.ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/users/", response_model=List[User])
async def get_users_async(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users
```

## Testing Patterns

### Test Client Setup
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from myapp.main import app
from myapp.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def authenticated_client(client):
    # Create test user and get token
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

### API Testing Examples
```python
# tests/api/test_users.py
def test_create_user(client):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

def test_get_users_requires_authentication(client):
    response = client.get("/api/v1/users/")
    assert response.status_code == 401

def test_get_users_with_authentication(authenticated_client):
    response = authenticated_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```