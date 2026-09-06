from database import (
    find_product_by_id,
    find_product_by_name,
    filter_products_by_partial_name
)


def test_find_product_by_id(setup_products):

    product = find_product_by_id(1, setup_products)

    assert product is not None
    assert product["name"] == "Rice"
    assert product["price"] == 12.0


def test_find_product_by_id_when_product_does_not_exist(setup_products):

    product = find_product_by_id(999, setup_products)

    assert product is None


def test_find_product_by_name(setup_products):

    product = find_product_by_name("Rice", setup_products)

    assert product is not None
    assert product["id"] == 1
    assert product["price"] == 12.0


def test_find_product_by_name_when_product_does_not_exist(setup_products):

    product = find_product_by_name("Nonexistent", setup_products)

    assert product is None


def test_filter_products_by_partial_name(setup_products):

    products = filter_products_by_partial_name("ri", setup_products)

    assert len(products) == 1
    assert products[0]["name"] == "Rice"


def test_filter_products_by_partial_name_with_multiple_results(setup_products):

    products = filter_products_by_partial_name("a", setup_products)

    assert len(products) == 2