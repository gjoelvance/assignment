from pydantic import BaseModel, ConfigDict, Field, field_validator

class AddressBase(BaseModel):
    street: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)

    @field_validator("street", "city", "state", "postal_code", "country")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")
        return value

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class NearbyAddress(AddressResponse):
    distance_km: float
