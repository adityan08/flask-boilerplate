from flasgger import swag_from

from app.api import bp

@swag_from({
    "tags": ["Health"],
    "summary": "Health check endpoint",
    "description": "Returns 200 OK if the service is running",
    "responses": {
        200: {
            "description": "Service is healthy",
            "content": {
                "text/plain": {
                    "example": "200 OK"
                }
            }
        }
    }
})
@bp.route("/health", methods=["GET"])
def health():
    return "200 OK"