from unittest.mock import create_autospec

import pytest

import product_service
from persistence import DatabaseDuplicateError, DatabaseError, ProductRepository


@pytest.fixture
def injected_repository(monkeypatch):
    def forbid_default_storage(_path):
        pytest.fail("Injected service must not open default SQLite storage")

    monkeypatch.setattr(product_service, "get_repository", forbid_default_storage)
    return create_autospec(ProductRepository, instance=True, spec_set=True)


def test_service_can_use_an_independent_repository(injected_repository):
    storage = injected_repository
    storage.find_by_name.return_value = None
    storage.create.return_value = 7
    product = product_service.create_product("  Café  ", 1.2345, repository=storage)
    assert product == {"id": 7, "name": "Café", "price": 1.2345}
    storage.create.assert_called_once_with("Café", 1.2345)
    storage.get.return_value = product
    assert product_service.get_product(7, repository=storage) == product
    storage.list_products.return_value = [product]
    assert product_service.list_products(repository=storage) == [product]
    assert product_service.search_products("CAFE", repository=storage) == [product]
    storage.update.return_value = True
    updated = product_service.update_product(7, " New ", 2, repository=storage)
    assert updated == {"id": 7, "name": "New", "price": 2.0}
    storage.update.assert_called_once_with(7, "New", 2.0)
    storage.delete.return_value = True
    assert product_service.delete_product(7, repository=storage) == product
    storage.delete.assert_called_once_with(7)
    product_service.initialize_products(repository=storage)
    product_service.check_product_storage(repository=storage)
    storage.initialize.assert_called_once_with()
    storage.check_health.assert_called_once_with()


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (DatabaseError, product_service.ProductPersistenceError),
        (DatabaseDuplicateError, product_service.DuplicateProductError),
    ],
)
def test_driver_neutral_failures_translate(injected_repository, error, expected):
    injected_repository.find_by_name.return_value = None
    injected_repository.create.side_effect = error
    with pytest.raises(expected):
        product_service.create_product("New", 1, repository=injected_repository)


def test_invalid_input_is_rejected_before_repository_write(injected_repository):
    with pytest.raises(product_service.ProductValidationError):
        product_service.create_product("  ", 1, repository=injected_repository)
    with pytest.raises(product_service.ProductValidationError):
        product_service.create_product(
            "Valid", float("inf"), repository=injected_repository
        )
    injected_repository.create.assert_not_called()


def test_conflicting_storage_arguments_are_rejected(injected_repository):
    with pytest.raises(ValueError, match="either"):
        product_service.list_products("explicit.db", repository=injected_repository)


def test_adapter_obeys_repository_contract(product_repository):
    storage: ProductRepository = product_repository
    storage.initialize()
    storage.check_health()
    assert storage.list_products() == []
    first = storage.create("First", 1.1234)
    second = storage.create("first", 2)
    assert [p["id"] for p in storage.list_products()] == [first, second]
    assert storage.find_by_name("First") == storage.get(first)
    assert storage.find_by_name("FIRST") is None
    with pytest.raises(DatabaseDuplicateError):
        storage.create("First", 3)
    assert storage.update(first, "Updated", 3)
    assert storage.get(first) == {"id": first, "name": "Updated", "price": 3.0}
    assert storage.delete(first)
    assert storage.get(first) is None
    assert not storage.update(first, "Gone", 1)
    assert not storage.delete(first)
    assert storage.get(2**100) is None
