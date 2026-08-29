import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    generate_next_id,
    find_product_by_id,
    find_product_by_name,
    filter_products_by_partial_name,
    save_products,
    create_table
)

# ============================================
# CONFIGURAÇÃO PARA TESTES
# ============================================

def setup_products():
    """Cria dados de teste no banco"""
    create_table()
    produtos = [
        {"id": 1, "name": "Arroz", "price": 12.0},
        {"id": 2, "name": "Feijão", "price": 8.0},
        {"id": 3, "name": "Macarrão", "price": 5.0},
    ]
    save_products(produtos)
    return produtos

# ============================================
# TESTES
# ============================================

def test_generate_next_id():
    setup_products()
    assert generate_next_id() == 4


def test_find_product_by_id():
    setup_products()
    produto = find_product_by_id(1)
    assert produto is not None
    assert produto["name"] == "Arroz"
    assert produto["price"] == 12.0

    produto = find_product_by_id(999)
    assert produto is None


def test_find_product_by_name():
    setup_products()
    produto = find_product_by_name("Arroz")
    assert produto is not None
    assert produto["id"] == 1
    assert produto["price"] == 12.0

    produto = find_product_by_name("Inexistente")
    assert produto is None


def test_filter_products_by_partial_name():
    setup_products()
    encontrados = filter_products_by_partial_name("ar")
    assert len(encontrados) == 2
    assert encontrados[0]["name"] == "Arroz"
    assert encontrados[1]["name"] == "Macarrão"

    encontrados = filter_products_by_partial_name("feijao")
    assert len(encontrados) == 1
    assert encontrados[0]["name"] == "Feijão"

    encontrados = filter_products_by_partial_name("xyz")
    assert len(encontrados) == 0