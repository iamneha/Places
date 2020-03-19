"""Representation of HTTP error."""
from werkzeug.exceptions import HTTPException


class HTTPError(HTTPException):
    """Representation of HTTP error."""

    def __init__(self, status_code, description):
        """Call the superclass constructor and set status code and \
        error attributes."""
        super().__init__(self)
        self.code = status_code
        self.description = description
        self.data = {"error": self.description}
