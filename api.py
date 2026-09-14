from fastapi import FastAPI, HTTPException
from database import (
    create_product as save_product_to_database,
    update_product as update_product_database,
    delete_product as delete_product_database,
    find_product_by_id,
    find_product_by_name,
    load_products,
    filter_products_by_partial_name,
    create_table
)
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
import os 


DB_NAME = os.getenv("DB_NAME", "produtos.db")

create_table(DB_NAME)


# ============================================
# INICIALIZAÇÃO DA API
# ============================================

app = FastAPI(
    title="Sistema de Produtos API",
    description="API para gerenciamento de produtos",
    version="1.0.0"
)


# ============================================
# ENDPOINTS (rotas da API)
# ============================================

@app.get("/")
def root():
    return {"message": "Bem-vindo à API de Produtos!"}


@app.get("/products", response_model=list[ProductResponse])
def list_all_products():
    """Retorna todos os produtos"""
    return load_products(DB_NAME)


@app.get(
    "/products/search/",
    response_model=list[ProductResponse],
)
def search_products(name: str):
    """Busca produtos por parte do nome"""
    result = filter_products_by_partial_name(name, DB_NAME)
    if not result:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado")
    return result


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    """Retorna um produto pelo ID"""
    product = find_product_by_id(product_id, DB_NAME)
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate):
    """Cria um novo produto"""
    # Verifica se já existe com o mesmo nome
    existing = find_product_by_name(product.name, DB_NAME)
    if existing:
        raise HTTPException(status_code=400, detail="Produto já cadastrado")
    
    product_id = save_product_to_database(product.name, product.price, DB_NAME)

    return {
        "id": product_id,
        "name": product.name,
        "price": product.price
    }


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):

    existing = find_product_by_id(product_id, DB_NAME)

    if existing is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    product_with_same_name = find_product_by_name(product.name, DB_NAME)

    if product_with_same_name and product_with_same_name["id"] != product_id:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro produto com esse nome"
        )

    update_product_database(
        product_id,
        product.name,
        product.price,
        DB_NAME
    )

    return {
        "id": product_id,
        "name": product.name,
        "price": product.price
    }


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):

    existing = find_product_by_id(product_id, DB_NAME)

    if existing is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    delete_product_database(product_id, DB_NAME)

    return
