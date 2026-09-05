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
from pydantic import BaseModel, Field, validator

# Cria a tabela ao iniciar
create_table()

# ============================================
# MODELO DE DADOS (validação)
# ============================================

class Product(BaseModel):
    name: str = Field(..., min_length=1, description="Nome do produto")
    price: float = Field(..., gt=0, description="Preço do produto (deve ser maior que zero)")

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Nome não pode ser vazio')
        return v.strip()

    @validator('price')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

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
    return load_products()


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    """Retorna um produto pelo ID"""
    product = find_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: Product):
    """Cria um novo produto"""
    # Verifica se já existe com o mesmo nome
    existing = find_product_by_name(product.name)
    if existing:
        raise HTTPException(status_code=400, detail="Produto já cadastrado")
    
    product_id = save_product_to_database(product.name, product.price)

    return {
        "id": product_id,
        "name": product.name,
        "price": product.price
    }


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: Product):

    existing = find_product_by_id(product_id)

    if existing is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_product_database(
        product_id,
        product.name,
        product.price
    )

    return {
        "id": product_id,
        "name": product.name,
        "price": product.price
    }


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):

    existing = find_product_by_id(product_id)

    if existing is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    delete_product_database(product_id)

    return

@app.get("/products/search/")
def search_products(name: str):
    """Busca produtos por parte do nome"""
    result = filter_products_by_partial_name(name)
    if not result:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado")
    return result