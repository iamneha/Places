import re

from backend.models.database import db
import backend.models as models

from pyexpect import expect
import responses


def test_api_docs(client):
    response = client.get("/spec")
    assert response.status_code == 302
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.data


@responses.activate
def test_properties_get_invalid_params(client):
    response = client.get("/api/v1/properties?at=")
    assert response.status_code == 400
    expected = {
        "error": "Please provide LAT and LONG in valid format at=<LAT>,<LONG>"
    }
    expect(response.json).equal(expected)


def test_properties_get_invalid_lat_long_range(client):
    response = client.get("/api/v1/properties?at=2032,-123")
    assert response.status_code == 400
    expected = {
        "error": (
            "The latitude must be a number between -90 and "
            "90 and the longitude between -180 and 180"
        )
    }
    expect(response.json).equal(expected)


@responses.activate
def test_properties_get_valid_params(client):
    json_response = {
        "results": [{"position": {"latitude": 32.32, "longitude": 56.1}}]
    }
    responses.add(
        responses.GET,
        url=re.compile(r"https://.+"),
        json=json_response,
        status=200,
    )
    response = client.get("/api/v1/properties?at=20,32")
    assert response.status_code == 200
    expect(response.json).equal(json_response["results"])


def test_create_property_post_invalid(client):
    payload = dict(
        property_name="test", property_latitude=3232, property_longitude=-32321
    )
    response = client.post("/api/v1/properties", json=payload)
    assert response.status_code == 400
    expected = {
        "error": (
            "The latitude must be a number between -90 and "
            "90 and the longitude between -180 and 180"
        )
    }
    expect(response.json).equal(expected)


def test_create_property_post_valid(client):
    payload = dict(
        property_name="test", property_latitude=2, property_longitude=-3
    )
    response = client.post("/api/v1/properties", json=payload)
    assert response.status_code == 200
    property_obj = (
        db.session.query(models.booking.Property).filter_by(**payload).first()
    )
    property_id = models.booking.PropertySchema().dump(
        property_obj, many=False
    )["id"]
    assert response.json["property_id"] == property_id


def test_booking_post_invalid_input(client):
    payload = {
        "username": "neha",
        "email": "test",
        "property_name": "some property",
        "property_latitude": 32.02,
        "property_longitude": 38.02,
    }
    response = client.post("/api/v1/bookings", json=payload)
    expected = {"error": "{'email': ['Not a valid email address.']}"}
    expect(response.json).equal(expected)


def test_booking_post_valid_input(client):
    payload = {
        "username": "neha",
        "email": "test@test.com",
        "property_name": "some property",
        "property_latitude": 32.02,
        "property_longitude": 38.02,
    }

    response = client.post("/api/v1/bookings", json=payload)

    booking_result_obj = (
        db.session.query(models.booking.Booking)
        .filter_by(email="test@test.com")
        .first()
    )
    result = models.booking.BookingSchema().dump(
        booking_result_obj, many=False
    )

    assert response.json["booking_id"] == result["id"]
    assert payload["username"] == result["username"]
    assert payload["email"] == result["email"]


def test_property_bookings_get_invalid_id(client):
    response = client.get("/api/v1/properties/dxff/bookings")
    assert response.status_code == 404


def test_property_bookings_get_valid_id(client):
    payload = dict(
        property_name="test", property_latitude=30.0, property_longitude=-3
    )
    response = client.post("/api/v1/properties", json=payload)
    property_id = response.json["property_id"]
    response = client.get(f"/api/v1/properties/{property_id}/bookings")
    assert response.status_code == 200
