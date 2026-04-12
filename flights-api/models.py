from datetime import date

from sqlalchemy import BigInteger, Date, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Flight(Base):
    __tablename__ = "flights"
    __table_args__ = {"schema": "airline"}    

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # lookup fields
    flight_date: Mapped[date] = mapped_column(Date, nullable=False)
    iata_code_marketing_airline: Mapped[str | None] = mapped_column(Text)
    flight_number_marketing_airline: Mapped[str | None] = mapped_column(Text)

    # traveler-facing fields
    origin: Mapped[str | None] = mapped_column(Text)
    origin_city_name: Mapped[str | None] = mapped_column(Text)
    dest: Mapped[str | None] = mapped_column(Text)
    dest_city_name: Mapped[str | None] = mapped_column(Text)

    crs_dep_time: Mapped[str | None] = mapped_column(Text)
    dep_time: Mapped[str | None] = mapped_column(Text)
    crs_arr_time: Mapped[str | None] = mapped_column(Text)
    arr_time: Mapped[str | None] = mapped_column(Text)

    dep_delay_minutes: Mapped[float | None] = mapped_column(Float)
    arr_delay_minutes: Mapped[float | None] = mapped_column(Float)

    cancelled: Mapped[float | None] = mapped_column(Float)
    diverted: Mapped[float | None] = mapped_column(Float)

    operating_airline: Mapped[str | None] = mapped_column(Text)
    iata_code_operating_airline: Mapped[str | None] = mapped_column(Text)
    tail_number: Mapped[str | None] = mapped_column(Text)