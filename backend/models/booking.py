"""Database models."""

from sqlalchemy import Integer, String, Float, ForeignKey, UniqueConstraint
from marshmallow import post_load, fields, Schema
from backend.app import db


class Property(db.Model):
    """Property database model."""

    __tablename__ = "property"
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    property_name = db.Column(String(250), nullable=False)
    property_latitude = db.Column(Float, nullable=False)
    property_longitude = db.Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "property_latitude", "property_longitude", "property_name"
        ),
    )


class PropertySchema(Schema):
    """Schema for the Property Model."""

    id = fields.Integer(dump_only=True)
    property_name = fields.String()
    property_latitude = fields.Float()
    property_longitude = fields.Float()

    @post_load
    def create_property(self, data, **kwargs):
        """Create a Property Object."""
        return Property(**data)


class Booking(db.Model):
    """Booking database model."""

    __tablename__ = "booking"
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    username = db.Column(String(250), nullable=False)
    email = db.Column(String(250), nullable=False)
    property_id = db.Column(Integer, ForeignKey(Property.id), nullable=False)


class BookingSchema(Schema):
    """Schema for the Booking Model."""

    id = fields.Integer(dump_only=True)
    username = fields.String()
    email = fields.Email()
    property_id = fields.Integer()

    @post_load
    def create_booking(self, data, **kwargs):
        """Create a Booking Object."""
        return Booking(**data)
