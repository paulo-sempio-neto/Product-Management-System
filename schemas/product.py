from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer, field_validator

PRICE_QUANTUM = Decimal("0.01")
MAX_PRICE_CENTS = 2**63 - 1


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: Decimal = Field(..., gt=0, allow_inf_nan=False)

    @field_validator("price", mode="before")
    @classmethod
    def price_not_boolean(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("Preco deve ser um numero")
        return value

    @field_validator("price")
    @classmethod
    def price_is_valid_money(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("Preco deve ser finito")
        cents = value * 100
        if cents != cents.to_integral_value():
            raise ValueError("Preco deve ter no maximo duas casas decimais")
        if int(cents) > MAX_PRICE_CENTS:
            raise ValueError("Preco muito alto")
        return value.quantize(PRICE_QUANTUM)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Nome nao pode ser vazio")

        return value


class ProductUpdate(ProductCreate):
    pass


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal

    @field_serializer("price", when_used="json")
    def serialize_price(self, value: Decimal) -> float:
        return float(value)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    limit: int
    total: int
