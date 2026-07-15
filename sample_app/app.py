"""Sample application that WatchDog AI monitors.
This simulates a real production API with intentional edge-case gaps."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Sample E-Commerce API", version="1.0.0")

users_db = {}
orders_db = {}
products_db = {
    "1": {"id": "1", "name": "Laptop", "price": 999.99, "stock": 50},
    "2": {"id": "2", "name": "Phone", "price": 699.99, "stock": 100},
    "3": {"id": "3", "name": "Headphones", "price": 149.99, "stock": 200},
}


class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None


class OrderCreate(BaseModel):
    user_id: str
    product_id: str
    quantity: int
    discount_code: Optional[str] = None


@app.post("/api/users")
async def create_user(user: UserCreate):
    if not user.name:
        raise HTTPException(status_code=400, detail="Name is required")
    if user.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(status_code=409, detail="Email already exists")

    # BUG: No validation for special characters in name
    # BUG: No length limit on name field
    user_id = str(len(users_db) + 1)
    users_db[user_id] = {"id": user_id, "name": user.name, "email": user.email, "phone": user.phone}
    return users_db[user_id]


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]


@app.post("/api/orders")
async def create_order(order: OrderCreate):
    # BUG: No validation for negative quantity
    # BUG: No validation for discount_code format
    if order.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products_db[order.product_id]

    # BUG: Doesn't check stock availability
    total = product["price"] * order.quantity

    # BUG: discount_code=None causes crash if processed
    if order.discount_code:
        if order.discount_code == "SAVE20":
            total *= 0.8
        # BUG: Unknown discount codes silently ignored

    order_id = str(len(orders_db) + 1)
    orders_db[order_id] = {
        "id": order_id,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total": total,
        "status": "created",
    }
    return orders_db[order_id]


@app.get("/api/products")
async def list_products():
    return list(products_db.values())


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]


@app.put("/api/users/{user_id}")
async def update_user(user_id: str, user: UserCreate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    # BUG: No validation on update either
    users_db[user_id].update({"name": user.name, "email": user.email, "phone": user.phone})
    return users_db[user_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
