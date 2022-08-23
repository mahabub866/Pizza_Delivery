from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from models import User

from schemas import SignUpModel,LoginModel
from sqlalchemy.orm.session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder


auth_router = APIRouter(
    prefix="/auth",
    tags=['Auth']
)


@auth_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invaild Token")

    return {'message': 'hello world'}


@auth_router.post('/signup',response_model=SignUpModel,status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel, db: Session = Depends(get_db)):
    db_email = db.query(User).filter(User.email == user.email).first()

    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with email Already Exists")

    db_username = db.query(User).filter(User.username == user.username).first()

    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with username Already Exists")

    new_user = User(username=user.username, email=user.email, password=generate_password_hash(
        user.password), is_active=user.is_active, is_staff=user.is_staff)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# login routes
@auth_router.post('/login',status_code=status.HTTP_200_OK)
async def login(user:LoginModel,db: Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    db_user=db.query(User).filter(User.username==user.username).first()

    if db_user and check_password_hash(db_user.password,user.password):
        access_token=Authorize.create_access_token(subject=user.username)
        refresh_token=Authorize.create_refresh_token(subject=user.username)

        response={
            "access":access_token,
            "refresh":refresh_token
        }

        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Username or Password")


# refreshing tokens routes
@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_refresh_token_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please provide a valid refresh token"
        ) 

    current_user=Authorize.get_jwt_subject()

    
    access_token=Authorize.create_access_token(subject=current_user)

    return jsonable_encoder({"access":access_token})   

