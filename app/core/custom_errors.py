from flask import jsonify

from app.api import bp


class CustomError(Exception):
    def __init__(self, message=None, status=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status
        self.payload = payload

    def __str__(self):
        return f'{self.message} {self.status_code}'

    def to_dict(self):
        rv = dict(self.payload or ())
        rv.update({"message": self.message, "status_code": self.status_code})
        return rv


class NoContent(CustomError):
    def __init__(self, message="Success"):
        CustomError.__init__(self, message, 204)


class BadRequest(CustomError):
    def __init__(self, message):
        CustomError.__init__(self, message, 400)


class Unauthorized(CustomError):
    def __init__(self, message="Please login and try again."):
        CustomError.__init__(self, message, 401)


class Forbidden(CustomError):
    def __init__(self, message="You do not have the privilege to do this."):
        CustomError.__init__(self, message, 403)


class InternalError(CustomError):
    def __init__(self, message="Please try again later."):
        CustomError.__init__(self, message, 500)


class UnProcessable(CustomError):
    def __init__(self, message="The input format is wrong"):
        CustomError.__init__(self, message, 422)


class Conflict(CustomError):
    def __init__(self, message="Duplicate Entry"):
        CustomError.__init__(self, message, 409)


class ManyRequests(CustomError):
    def __init__(self, message="Too Many Requests has been received."):
        CustomError.__init__(self, message, 409)


class NotFound(CustomError):
    def __init__(self, message="Sorry No data found"):
        CustomError.__init__(self, message, 404)


@bp.errorhandler(CustomError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = 200
    return response
