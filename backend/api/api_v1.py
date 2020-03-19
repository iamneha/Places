"""Booking property api v1."""
import requests
from flask import Blueprint, request, current_app
from flask_restx import Resource, Api, fields
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from backend.config import API_KEY, BASE_URL
from backend.exceptions import HTTPError
from backend.models.booking import (
    Booking,
    BookingSchema,
    Property,
    PropertySchema,
)
from backend.app import db

API_V1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

api = Api(
    API_V1, default="api/v1", default_label="Booking Operations [show/hide]"
)
booking_schema = BookingSchema()
property_schema = PropertySchema()


SUCCESS_CODES = (200, 202)

booking_req_model = api.model(
    "Booking",
    {
        "username": fields.String(required=True, description="User name"),
        "email": fields.String(
            required=True, description="Email address of user"
        ),
        "property_name": fields.String(
            required=True, description="Name of the property"
        ),
        "property_latitude": fields.Float(
            required=True, description="Latitude or property"
        ),
        "property_longitude": fields.Float(
            required=True, description="Longitude or property"
        ),
    },
)
property_booking_model = api.model(
    "PropertyBookingResponse",
    {
        "username": fields.String,
        "emai": fields.String,
        "property_id": fields.Integer,
        "id": fields.Integer,
    },
)
property_req_model = api.model(
    "Property",
    {
        "property_name": fields.String(required=True),
        "property_latitude": fields.Float(required=True),
        "property_longitude": fields.Float(required=True),
    },
)
error_model = api.model(
    "ErrorResponse", {"error": fields.String(desription="message")}
)


@api.route("/properties")
class Properties(Resource):
    """Implementation of /properties REST API endpoint."""

    @api.doc(params={"at": "LAT,LONG"}, description="nonthing")
    @api.response(200, "Success")
    @api.response(400, "Validation Error", model=error_model)
    def get(self):
        """Handle the GET REST API endpoint.

        Returns (list): List of location of properties available around the given
            latitude and longitude.
        """
        at = request.args.get("at")
        current_app.logger.info("[/properties] request args %s", at)
        if at is None or len(at.split(",")) != 2:
            raise HTTPError(
                status_code=400,
                description=(
                    "Please provide LAT and LONG in "
                    "valid format at=<LAT>,<LONG>"
                ),
            )
        LAT, LONG = at.split(",")
        try:
            LAT = float(LAT)
            LONG = float(LONG)
            if not (-90 <= LAT <= 90) or not (-180 <= LONG <= 180):
                raise ValueError(
                    "The latitude must be a number between "
                    "-90 and 90 and the longitude between -180 and 180"
                )
        except ValueError as _exc:
            raise HTTPError(400, description=str(_exc))

        params = {"at": f"{LAT},{LONG}", "apiKey": API_KEY, "q": "hotel"}
        response = requests.get(BASE_URL, params=params)
        if response.status_code not in SUCCESS_CODES:
            raise HTTPError(
                status_code=response.status_code, description=response.text
            )
        responses = response.json()
        hotels = []
        for res in responses["results"]:
            if res.get("position"):
                hotels.append(res)
        return hotels

    @api.expect(property_req_model)
    @api.response(
        200,
        "Property succefully created.",
        model=api.model("PropertyResponse", {"property_id": fields.Integer}),
    )
    @api.response(400, "Validation Error", model=error_model)
    def post(self):
        """Handle the POST REST API call.

        Create the property for given property name, latitude, longitude if
            not exists.
        Returns (dict): property id
        """
        input_json = request.get_json()
        if not input_json:
            raise HTTPError(400, "please provide valid input")
        try:
            property_name = input_json["property_name"]
            property_latitude = input_json["property_latitude"]
            property_longitude = input_json["property_longitude"]

            if not (-90 <= property_latitude <= 90) or not (
                -180 <= property_longitude <= 180
            ):
                raise ValueError(
                    "The latitude must be a number between "
                    "-90 and 90 and the longitude between -180 and 180"
                )

            # ASSUMPTION: property name,longitude,latitude are unique fields
            property_exist = (
                db.session.query(Property)
                .filter_by(
                    property_name=property_name,
                    property_latitude=property_latitude,
                    property_longitude=property_longitude,
                )
                .first()
            )
            if property_exist:
                current_app.logger.info(
                    "property %s already exists", property_name
                )
                property_id = property_schema.dump(property_exist)["id"]
            else:
                # create property
                property_obj = property_schema.load(
                    dict(
                        property_name=property_name,
                        property_latitude=property_latitude,
                        property_longitude=property_longitude,
                    )
                )
                db.session.add(property_obj)
                db.session.commit()
                property_id = property_obj.id
            return {"property_id": property_id}
        except ValueError as _exc:
            raise HTTPError(400, description=str(_exc))
        except KeyError as _exc:
            raise HTTPError(400, f"Missing field {str(_exc)}")
        except ValidationError as _exc:
            raise HTTPError(400, str(_exc.messages))
        except SQLAlchemyError as _exc:
            db.session.rollback()
            current_app.logger.exception(str(_exc))
            raise HTTPError(
                500, "Database Error: Could not process the request"
            )


@api.route("/bookings", methods=["POST"])
class Bookings(Resource):
    """Implementation of /bookings REST API endpoint."""

    @api.expect(booking_req_model)
    @api.response(
        200,
        "Booking succefully created.",
        model=api.model("BookingResponse", {"booking_id": fields.Integer}),
    )
    @api.response(400, "Validation Error", model=error_model)
    def post(self):
        """Handle the POST REST API endpoint.

        Create the booking for given property location and also creates the
            property entry if property does not exist in the database.

        Returns (dict): booking id

        """
        input_json = request.get_json()
        if not input_json:
            raise HTTPError(400, "please provide valid input")
        try:
            properties_obj = Properties()
            property_response = properties_obj.post()
            property_id = property_response["property_id"]

            booking_obj = booking_schema.load(
                dict(
                    username=input_json["username"],
                    email=input_json["email"],
                    property_id=property_id,
                )
            )
            db.session.add(booking_obj)
            db.session.commit()
            return {"booking_id": booking_obj.id}
        except KeyError as _exc:
            raise HTTPError(400, f"Missing field {str(_exc)}")
        except ValidationError as _exc:
            raise HTTPError(400, str(_exc.messages))
        except SQLAlchemyError as _exc:
            db.session.rollback()
            current_app.logger.exception(str(_exc))
            raise HTTPError(
                500, "Database Error: Could not process the request"
            )


@api.route("/properties/<int:property_id>/bookings", methods=["GET"])
class PropertyBookings(Resource):
    """Implementation of /properties/<id>/bookings REST API endpoint."""

    @api.response(
        200,
        "Success",
        model=api.model(
            "PropertyBoookingResponse",
            {"results": fields.List(fields.Nested(property_booking_model))},
        ),
    )
    @api.response(400, "Validation Error", model=error_model)
    def get(self, property_id):
        """Handle the GET REST API endpoint.

        Arguments:
            property_id (int): property id
        Returns (list): list of bookings for a given property id

        """
        try:
            result_obj = (
                db.session.query(Booking)
                .filter_by(property_id=int(property_id))
                .all()
            )
            return booking_schema.dump(result_obj, many=True)
        except ValueError as _exc:
            raise HTTPError(400, str(_exc))
        except SQLAlchemyError as _exc:
            db.session.rollback()
            current_app.logger.exception(str(_exc))
            raise HTTPError(
                500, "Database Error: Could not process the request"
            )
