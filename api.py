from fastapi import FastAPI, HTTPException
from funcoes_produtos import (
    load_products,
    save_products,
    generate_next_id,
    find_product_by_id,
    find_product_by_name,
    filter_products_by_partial_name
)
from pydantic import BaseModel

# ============================================
# MODELO DE DADOS (validação)
# ============================================

class Product(BaseModel):
    name: str
    price: float

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

# Carrega os produtos ao iniciar
products = load_products()

# ============================================
# ENDPOINTS (rotas da API)
# ============================================

@app.get("/")
def root():
    return {"message": "Bem-vindo à API de Produtos!"}


@app.get("/products", response_model=list[ProductResponse])
def list_all_products():
    """Retorna todos os produtos"""
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    """Retorna um produto pelo ID"""
    product = find_product_by_id(products, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: Product):
    """Cria um novo produto"""
    # Verifica se já existe com o mesmo nome
    existing = find_product_by_name(products, product.name)
    if existing:
        raise HTTPException(status_code=400, detail="Produto já cadastrado")
    
    # Gera ID e cria o produto
    new_id = generate_next_id(products)
    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price
    }
    
    products.append(new_product)
    save_products(products)
    
    return new_product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: Product):
    """Atualiza o preço de um produto"""
    existing = find_product_by_id(products, product_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    existing["name"] = product.name
    existing["price"] = product.price
    save_products(products)
    
    return existing


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    """Remove um produto"""
    existing = find_product_by_id(products, product_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    products.remove(existing)
    save_products(products)
    
    return None


@app.get("/products/search/")
def search_products(name: str):
    """Busca produtos por parte do nome"""
    result = filter_products_by_partial_name(products, name)
    if not result:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado")
    return result