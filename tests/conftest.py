import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from database import (
    create_table,
    create_product
)


@pytest.fixture
def setup_products(tmp_path):
    """
    Creates test products in a temporary database.
    """

    db_file = tmp_path / "test.db"

    db_name = str(db_file)

    create_table(db_name)

    create_product("Rice", 12.0, db_name)
    create_product("Beans", 8.0, db_name)
    create_product("Pasta", 5.0, db_name)

    return db_name