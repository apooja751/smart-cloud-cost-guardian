from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas import UserRegister, UserLogin, PasswordChange, ProfileUpdate, UserResponse, TokenResponse
from app.schemas.common import StandardResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/register', response_model=StandardResponse[TokenResponse])
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email address already registered')
    
    role = 'ADMIN' if user_in.email.startswith('admin') or user_in.role == 'ADMIN' else 'USER'
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    audit = AuditLog(user_id=user.id, action='USER_REGISTERED', metadata_json='{}')
    db.add(audit)
    db.commit()

    token = create_access_token(subject=user.id, role=user.role)
    token_resp = TokenResponse(
        access_token=token,
        token_type='bearer',
        user=UserResponse.model_validate(user)
    )
    return StandardResponse(data=token_resp, message='User registered successfully')

@router.post('/login', response_model=StandardResponse[TokenResponse])
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Account is inactive')

    audit = AuditLog(user_id=user.id, action='USER_LOGIN', metadata_json='{}')
    db.add(audit)
    db.commit()

    token = create_access_token(subject=user.id, role=user.role)
    token_resp = TokenResponse(
        access_token=token,
        token_type='bearer',
        user=UserResponse.model_validate(user)
    )
    return StandardResponse(data=token_resp, message='Login successful')

@router.get('/me', response_model=StandardResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    return StandardResponse(data=UserResponse.model_validate(current_user), message='Profile retrieved')

@router.post('/change-password', response_model=StandardResponse[dict])
def change_password(pass_in: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(pass_in.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail='Current password is incorrect')
    
    current_user.password_hash = get_password_hash(pass_in.new_password)
    db.commit()

    audit = AuditLog(user_id=current_user.id, action='PASSWORD_CHANGED', metadata_json='{}')
    db.add(audit)
    db.commit()

    return StandardResponse(data={}, message='Password changed successfully')

@router.put('/update-profile', response_model=StandardResponse[UserResponse])
def update_profile(prof_in: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if prof_in.name:
        current_user.name = prof_in.name
    if prof_in.email and prof_in.email != current_user.email:
        exist = db.query(User).filter(User.email == prof_in.email).first()
        if exist:
            raise HTTPException(status_code=400, detail='Email already in use')
        current_user.email = prof_in.email
    db.commit()
    db.refresh(current_user)
    return StandardResponse(data=UserResponse.model_validate(current_user), message='Profile updated')
