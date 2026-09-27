from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TripRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    start_date: date
    end_date: date
    budget: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    travelers: int = Field(default=1, ge=1, le=20)
    preferences: str = Field(default="", max_length=1000)
    passport_country: str = Field(default="India", min_length=2)

    @model_validator(mode="after")
    def validate_trip_dates(self) -> "TripRequest":
        if self.end_date <= self.start_date:
            raise ValueError("End date must be later than start date.")
        if self.start_date < date.today():
            raise ValueError("Start date cannot be in the past.")
        self.currency = self.currency.upper()
        return self


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1500)
    destination: str | None = None
    passport_country: str = "India"
    start_date: date | None = None
    end_date: date | None = None
