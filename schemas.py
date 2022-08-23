from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_active:Optional[bool]
    is_staff:Optional[bool]
    
    class Config():
        orm_mode=True
        schema_extra={
            'example':{
                "username":"mahabub",
                "email":"mak@gmail.com",
                "password":'password',
                "is_staff":True,
                "is_active":False,

            }
        }


# login jwt part
class Settings(BaseModel):
    AUTHJWT_SECRET_KEY:str='2332b5d0ea305b1b472fc85371ea45d7'
    authjwt_access_token_expires: timedelta = timedelta(hours=15)
    authjwt_refresh_token_expires: timedelta = timedelta(days=30)
    

class LoginModel(BaseModel):
    username:str
    password:str

class OrderModel(BaseModel):
    id:Optional[int]
    quantity:int
    order_status:Optional[str]="PENDING"
    pizza_size:Optional[str]="SMALL"
    user_id:Optional[int]

    class Config():
        orm_mode=True
        schema_extra={
            'example':{
                "quantity":2,
                "pizza_size":'SMALL',


            }
        }
    
class OrderStatusModel(BaseModel):
    order_status:Optional[str]="PENDING"
    

    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "order_status":"PENDING",
                 
            }
        }