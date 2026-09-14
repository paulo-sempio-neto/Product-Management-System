from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Nome não pode ser vazio")

        return value


class ProductUpdate(ProductCreate):
    pass


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float