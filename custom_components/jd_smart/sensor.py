"""Sensor platform for JD Smart."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import JdSmartConfigEntry
from .entity import JdSmartEntity


@dataclass(frozen=True, kw_only=True)
class JdSmartSensorDescription(SensorEntityDescription):
    """JD Smart sensor description."""

    stream_id: str


SENSORS: tuple[JdSmartSensorDescription, ...] = (
    # 当前温度
    JdSmartSensorDescription(
        key="current_temperature",
        stream_id="CurrentTemperature",
        translation_key="current_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # 新增：户外温度
    JdSmartSensorDescription(
        key="outdoor_temperature",
        stream_id="OutdoorTemperature",
        translation_key="outdoor_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    JdSmartSensorDescription(
        key="ptcheat",
        stream_id="ptcheat",
        translation_key="protection_state",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JdSmartConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up JD Smart sensors."""
    async_add_entities(
        JdSmartSensor(coordinator, description)
        for coordinator in entry.runtime_data.coordinators.values()
        for description in SENSORS
    )


class JdSmartSensor(JdSmartEntity, SensorEntity):
    """JD Smart stream sensor."""

    entity_description: JdSmartSensorDescription

    def __init__(
        self,
        coordinator,
        description: JdSmartSensorDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_translation_key = description.translation_key

    @property
    def native_value(self) -> str | float | None:
        """Return sensor value."""
        value = self.streams.get(self.entity_description.stream_id)
        if value == "":
            return None
        if self.entity_description.state_class is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        return value
