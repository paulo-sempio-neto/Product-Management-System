import sqlite3
from typing import List, Dict, Optional
import unicodedata

DB_NAME = "produtos.db"


def get_connection():
    """Retorna uma conexão com o banco de dados"""
    return sqlite3.connect(DB_NAME)


def create_table():
    """Cria a tabela de produtos se não existir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def load_products() -> List[Dict]:
    """Carrega todos os produtos do banco"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, price FROM products")
    rows = cursor.fetchall()
    
    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2]
        })
    
    conn.close()
    return products


def save_products(products: List[Dict]) -> None:
    """Salva a lista de produtos no banco (substitui tudo)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Limpa a tabela
    cursor.execute("DELETE FROM products")
    
    # Insere todos os produtos
    for product in products:
        cursor.execute(
            "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
            (product["id"], product["name"], product["price"])
        )
    
    conn.commit()
    conn.close()


def find_product_by_id(product_id: int) -> Optional[Dict]:
    """Busca um produto pelo ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        "id": row[0],
        "name": row[1],
        "price": row[2]
    }


def find_product_by_name(name: str) -> Optional[Dict]:
    """Busca um produto pelo nome (exato)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, price FROM products WHERE name = ?", (name,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        "id": row[0],
        "name": row[1],
        "price": row[2]
    }


def filter_products_by_partial_name(partial_name: str) -> List[Dict]:
    """Busca produtos por parte do nome (ignorando acentos)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    partial_name = unicodedata.normalize('NFKD', partial_name).encode('ascii', 'ignore').decode('ascii').lower()
    
    cursor.execute("SELECT id, name, price FROM products")
    rows = cursor.fetchall()
    
    products = []
    for row in rows:
        product_name = unicodedata.normalize('NFKD', row[1]).encode('ascii', 'ignore').decode('ascii').lower()
        if partial_name in product_name:
            products.append({
                "id": row[0],
                "name": row[1],
                "price": row[2]
            })
    
    conn.close()
    return products


def generate_next_id() -> int:
    """Gera o próximo ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM products")
    row = cursor.fetchone()
    
    conn.close()
    
    if row[0] is None:
        return 1
    return row[0] + 1