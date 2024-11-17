from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
from numpy._typing import ArrayLike
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import database


# To get sunrise + sunset times:
# https://pypi.org/project/suntime/


class Base(DeclarativeBase):
    pass


class LightingSample(database.Base):
    __tablename__ = "model_input"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    sunrise_time: Mapped[int]
    """
    Seconds since the start of the day that the sun would rise.
    """

    sunset_time: Mapped[int]
    """
    Seconds since the start of the day that the sun would set.
    """

    current_time: Mapped[int]
    """
    Seconds sinec the start of the day.
    """

    outside_brightness: Mapped[int]
    """
    Integer value between 0 and 255.
    Corresponds to luminosity readings from a light sensor.
    """

    outside_color_temperature: Mapped[int]
    """
    Mired color temperature (https://en.wikipedia.org/wiki/Mired)
    of the light coming from outside.
    """

    inside_brightness: Mapped[int]
    """
    Integer value between 0 and 255.
    Corresponds to the brightness value in the Philips Hue API.
    """

    inside_color_temperature: Mapped[int]
    """
    Mired color temperature.
    Not sure what the range is of this.
    Philips docs say lights from 2012 can go between 153 and 500,
    so probably in that range.
    """


@dataclass
class ModelInput:
    sunrise_time: int
    sunset_time: int
    current_time: int
    outside_brightness: int
    outside_color_temperature: int

    def to_array(self) -> ArrayLike:
        return np.array(
            [
                self.sunrise_time,
                self.sunset_time,
                self.current_time,
                self.outside_brightness,
                self.outside_color_temperature,
            ]
        )


@dataclass
class ModelOutput:
    inside_brightness: int
    inside_color_temperature: int


class LightModel(ABC):
    @abstractmethod
    def fit(self, samples: list[LightingSample]) -> None:
        pass

    @abstractmethod
    def predict(self, input: ModelInput) -> ModelOutput:
        pass


class LinearRegressionLightModel(LightModel):
    def __init__(self) -> None:
        self._brightness_model = LinearRegression()
        self._color_temperature_model = LinearRegression()

    def fit(self, samples: list[LightingSample]) -> None:
        inputs = [
            [
                sample.sunrise_time,
                sample.sunset_time,
                sample.current_time,
                sample.outside_brightness,
                sample.outside_color_temperature,
            ]
            for sample in samples
        ]
        brightnesses = [sample.inside_brightness for sample in samples]
        color_temperatures = [sample.inside_color_temperature for sample in samples]
        self._brightness_model.fit(inputs, brightnesses)
        self._color_temperature_model.fit(inputs, color_temperatures)

    def predict(self, input: ModelInput) -> ModelOutput:
        return ModelOutput(
            inside_brightness=self._brightness_model.predict(input.to_array()),
            inside_color_temperature=self._brightness_model.predict(input.to_array()),
        )
