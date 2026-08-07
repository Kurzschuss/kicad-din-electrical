"""Explizite JSON-Codecs und SQLite-Repository-Fabriken für MCB und RCCB."""

from __future__ import annotations

from collections.abc import Mapping
import sqlite3

from .identifiers import BusinessId, ObjectId
from .mcb import BreakingCapacity, MCB, NominalCurrent, PoleCount, RatedVoltage, TripCharacteristic
from .rccb import RCCB, RCCBPoleCount, RCCBRatedVoltage, RCCBType, RatedCurrent, ResidualCurrent
from .sqlite import SQLiteJsonRepository, SQLiteRepositoryConfig


def encode_mcb(mcb: MCB) -> Mapping[str, object]:
    return {
        "object_id": str(mcb.object_id),
        "business_id": str(mcb.business_id),
        "manufacturer": mcb.manufacturer,
        "product_name": mcb.product_name,
        "nominal_current_a": mcb.nominal_current.amperes,
        "rated_voltage_v": mcb.rated_voltage.volts,
        "breaking_capacity_a": mcb.breaking_capacity.amperes,
        "pole_count": mcb.pole_count.value,
        "trip_characteristic": mcb.trip_characteristic.value,
    }


def decode_mcb(data: Mapping[str, object]) -> MCB:
    return MCB(
        object_id=ObjectId.parse(str(data["object_id"])),
        business_id=BusinessId.parse(str(data["business_id"])),
        manufacturer=str(data["manufacturer"]),
        product_name=str(data["product_name"]),
        nominal_current=NominalCurrent(int(data["nominal_current_a"])),
        rated_voltage=RatedVoltage(int(data["rated_voltage_v"])),
        breaking_capacity=BreakingCapacity(int(data["breaking_capacity_a"])),
        pole_count=PoleCount(int(data["pole_count"])),
        trip_characteristic=TripCharacteristic(str(data["trip_characteristic"])),
    )


def encode_rccb(rccb: RCCB) -> Mapping[str, object]:
    return {
        "object_id": str(rccb.object_id),
        "business_id": str(rccb.business_id),
        "manufacturer": rccb.manufacturer,
        "product_name": rccb.product_name,
        "rated_current_a": rccb.rated_current.amperes,
        "residual_current_ma": rccb.residual_current.milliamperes,
        "rated_voltage_v": rccb.rated_voltage.volts,
        "pole_count": rccb.pole_count.value,
        "rccb_type": rccb.rccb_type.value,
    }


def decode_rccb(data: Mapping[str, object]) -> RCCB:
    return RCCB(
        object_id=ObjectId.parse(str(data["object_id"])),
        business_id=BusinessId.parse(str(data["business_id"])),
        manufacturer=str(data["manufacturer"]),
        product_name=str(data["product_name"]),
        rated_current=RatedCurrent(int(data["rated_current_a"])),
        residual_current=ResidualCurrent(int(data["residual_current_ma"])),
        rated_voltage=RCCBRatedVoltage(int(data["rated_voltage_v"])),
        pole_count=RCCBPoleCount(int(data["pole_count"])),
        rccb_type=RCCBType(str(data["rccb_type"])),
    )


def create_mcb_sqlite_repository(connection: sqlite3.Connection) -> SQLiteJsonRepository[MCB]:
    return SQLiteJsonRepository(
        connection,
        config=SQLiteRepositoryConfig("mcb"),
        encode=encode_mcb,
        decode=decode_mcb,
    )


def create_rccb_sqlite_repository(connection: sqlite3.Connection) -> SQLiteJsonRepository[RCCB]:
    return SQLiteJsonRepository(
        connection,
        config=SQLiteRepositoryConfig("rccb"),
        encode=encode_rccb,
        decode=decode_rccb,
    )
