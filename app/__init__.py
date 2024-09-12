from app.lib.get_config import get_config
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


def create_app(config_class):
    config = get_config(config_class)

    app = FastAPI(
        title="The National Archives opening times",
        log_level=config.get("LOG_LEVEL"),
    )
    app.state.config = {
        "BASE_URI": config.get("BASE_URI"),
        "GOOGLE_MAPS_API_KEY": config.get("GOOGLE_MAPS_API_KEY"),
        "GOOGLE_MAPS_PLACE_ID": config.get("GOOGLE_MAPS_PLACE_ID"),
    }
    if config.get("FORCE_HTTPS"):
        app.add_middleware(HTTPSRedirectMiddleware)

    from .healthcheck import routes as healthcheck_routes
    from .main import routes as main_routes

    app.include_router(healthcheck_routes.router, prefix="/healthcheck")
    app.include_router(
        main_routes.router,
        prefix=config.get("BASE_URI"),
    )

    return app
