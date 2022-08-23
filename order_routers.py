from fastapi import APIRouter,Depends,HTTPException,status
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from database import get_db
from models import User,Order
from schemas import LoginModel, OrderModel, OrderStatusModel
from sqlalchemy.orm.session import Session

order_router=APIRouter(
    prefix="/order",
    tags=['Order']
)

@order_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invaild Token")

    return {'message':'hello world'}

@order_router.post('/order',status_code=status.HTTP_201_CREATED)
async def place_An_order(order:OrderModel,Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invaild Token")
    
    current_user=Authorize.get_jwt_subject()

    user=db.query(User).filter(User.username==current_user).first()

    new_order=Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,
        
    )
    new_order.user=user
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    response={
        "pizza_size":new_order.pizza_size,
        "quantity":new_order.quantity,
        "id":new_order.id,
        "order_status":new_order.order_status

    }
    return jsonable_encoder(response)


    # normal way kora jai
    # return new_order

@order_router.get('/orders')
async def list_all_orders(Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invaild Token")

    current_user=Authorize.get_jwt_subject()

    user=db.query(User).filter(User.username==current_user).first()
    if user.is_staff:
        orders=db.query(Order).all()

        return jsonable_encoder(orders)

    raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not a superuser"
        )

    
@order_router.get('/orders/{id}')
async def get_order_by_id(id:int,Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):


    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user=Authorize.get_jwt_subject()

    current_user=db.query(User).filter(User.username==user).first()

    if current_user.is_staff:
        order=db.query(Order).filter(Order.id==id).first()

        return jsonable_encoder(order)

    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not alowed to carry out request"
        )


@order_router.get('/user/orders')
async def get_user_orders(Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):
 

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user=Authorize.get_jwt_subject()


    current_user=db.query(User).filter(User.username==user).first()

    return jsonable_encoder(current_user.orders)

@order_router.get('/user/order/{id}/')
async def get_specific_order(id:int,Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):


    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    subject=Authorize.get_jwt_subject()

    current_user=db.query(User).filter(User.username==subject).first()

    orders=current_user.orders

    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="No order with such id"
    )

@order_router.put('/order/update/{id}/')
async def update_order(id:int,order:OrderModel,Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):
   

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

    order_to_update=db.query(Order).filter(Order.id==id).first()

    order_to_update.quantity=order.quantity
    order_to_update.pizza_size=order.pizza_size

    db.commit()


    response={
                "id":order_to_update.id,
                "quantity":order_to_update.quantity,
                "pizza_size":order_to_update.pizza_size,
                "order_status":order_to_update.order_status,
            }

    return jsonable_encoder(response)


@order_router.patch('/order/update/{id}/')
async def update_order_status(id:int,
        order:OrderStatusModel,
        Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):


    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

    username=Authorize.get_jwt_subject()

    current_user=db.query(User).filter(User.username==username).first()

    if current_user.is_staff:
        order_to_update=db.query(Order).filter(Order.id==id).first()

        order_to_update.order_status=order.order_status
       

        db.commit()

        response={
                "id":order_to_update.id,
                "quantity":order_to_update.quantity,
                "pizza_size":order_to_update.pizza_size,
                "order_status":order_to_update.order_status,
            }

        return jsonable_encoder(response)


@order_router.delete('/order/delete/{id}/',status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id:int,Authorize:AuthJWT=Depends(),db: Session = Depends(get_db)):

    
    
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")


    order_to_delete=db.query(Order).filter(Order.id==id).first()
    if not order_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'post  with id {id} not Found')

    db.delete(order_to_delete)

    db.commit()

    return 'Deleted Sucessufly'

