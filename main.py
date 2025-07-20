# main.py
from fastapi import FastAPI, status, Query
from db import product_collection, order_collection
from bson import ObjectId
from schema import ProductModel, OrderModel
from fastapi import HTTPException
from schema import OrderRequestModel

app = FastAPI()


@app.get("/")
async def health_check():
    return {"message": "Ecommerce backend is up and running 🚀"}


@app.get("/test-mongo")
async def test_mongo():
    product = {"name": "Test Product", "price": 100.0}
    result = await product_collection.insert_one(product)
    return {"inserted_id": str(result.inserted_id)}


@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel):
    product_dict = product.dict()
    result = await product_collection.insert_one(product_dict)
    return {"id": str(result.inserted_id)}


@app.get("/products")
async def list_products(
    name: str = Query(None),
    size: str = Query(None),
    limit: int = Query(10),
    offset: int = Query(0)
):
    filter_query = {}

    if name:
        filter_query["name"] = {"$regex": name, "$options": "i"}

    if size:
        filter_query["sizes.size"] = size

    cursor = product_collection.find(filter_query, {"sizes": 0}).skip(offset).limit(limit)
    products_raw = await cursor.to_list(length=limit)

    products = [
        {
            "id": str(product["_id"]),
            "name": product.get("name"),
            "price": product.get("price")
        }
        for product in products_raw
    ]

    return {
        "data": products,
        "page": {
            "next": offset + limit,
            "limit": limit,
            "previous": max(offset - limit, 0)
        }
    }

# @app.post("/orders", status_code=status.HTTP_201_CREATED)
# async def create_order(order: OrderModel):
#     order_dict = order.dict()
#     result = await order_collection.insert_one(order_dict)
#     return {"order_id": str(result.inserted_id)}




@app.get("/orders/{user_id}")
async def get_orders(user_id: str):
    user_id = user_id.strip()  # 👈 Removes accidental '\n', ' ', etc.

    cursor = order_collection.find({"user_id": user_id}).sort("_id", -1)
    orders = []
    async for order in cursor:
        orders.append({
            "order_id": str(order["_id"]),
            "products": order["products"]
        })

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user.")

    return {"orders": orders}



@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order_request: OrderRequestModel):
    order_data = {
        "user_id": order_request.user_id,
        "products": [],
    }

    for item in order_request.items:
        # Validate ObjectId
        try:
            product_id = ObjectId(item.product_id)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid product ID: {item.product_id}")

        # Fetch product
        product = await product_collection.find_one({"_id": product_id})

        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found.")

        if "stock" not in product or product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product['name']}.")

        # Update stock
        await product_collection.update_one(
            {"_id": product_id},
            {"$inc": {"stock": -item.quantity}}
        )

        # Append product to order
        order_data["products"].append({
            "product_id": item.product_id,
            "name": product["name"],
            "quantity": item.quantity,
            "price": product["price"]
        })

    # Save order
    result = await order_collection.insert_one(order_data)

    return {"order_id": str(result.inserted_id)}
