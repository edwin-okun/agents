from app.core.settings import settings

TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url
    },
    "apps": {
        "models": {
            "models": ["app.models.payment"],
            "default_connection": "default",
        }
    }
}