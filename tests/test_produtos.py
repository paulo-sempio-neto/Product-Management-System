import sys
import os

# Adiciona a pasta raiz ao caminho para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from funcoes_produtos import (   # ← "functions" com "s"
    generate_next_id,
    find_product_by_id,
    find_product_by_name,
    filter_products_by_partial_name
)

# ============================================
# DADOS DE TESTE
# ============================================

produtos = [
    {"id": 1, "name": "Arroz", "price": 12.0},
    {"id": 2, "name": "Feijão", "price": 8.0},
    {"id": 3, "name": "Macarrão", "price": 5.0},
]

# ============================================
# TESTES
# ============================================

def test_generate_next_id():
    assert generate_next_id(produtos) == 4
    assert generate_next_id([]) == 1


def test_find_product_by_id():
    produto = find_product_by_id(produtos, 1)
    assert produto is not None
    assert produto["name"] == "Arroz"
    assert produto["price"] == 12.0

    produto = find_product_by_id(produtos, 999)
    assert produto is None


def test_find_product_by_name():
    produto = find_product_by_name(produtos, "Arroz")
    assert produto is not None
    assert produto["id"] == 1
    assert produto["price"] == 12.0

    produto = find_product_by_name(produtos, "Inexistente")
    assert produto is None


def test_filter_products_by_partial_name():
    encontrados = filter_products_by_partial_name(produtos, "ar")
    assert len(encontrados) == 2
    assert encontrados[0]["name"] == "Arroz"
    assert encontrados[1]["name"] == "Macarrão"

    encontrados = filter_products_by_partial_name(produtos, "feijao")
    assert len(encontrados) == 1
    assert encontrados[0]["name"] == "Feijão"

    encontrados = filter_products_by_partial_name(produtos, "xyz")
    assert len(encontrados) == 0