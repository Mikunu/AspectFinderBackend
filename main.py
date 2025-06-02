from fastapi import FastAPI, HTTPException, status, Depends, Query, APIRouter
from service.aspects_loader import AspectsLoader
from service.locale_loader import LocaleLoader
from dto.aspects_request_dto import AspectRequestDto
from utils.logger import Logger

logger = Logger().logger

app = FastAPI(
    title="Aspect Data API",
    description="API for managing aspect data",
    version="1.0.0",
    docs_url="/docs",
    contact={
        "name": "Developer",
        "email": "sairusdev@gmail.com"
    }
)

api_router = APIRouter(prefix="/api")
aspect_loader: AspectsLoader
locale_loader: LocaleLoader


@app.on_event("startup")
async def startup_event():
    """Application initialization"""
    global aspect_loader, locale_loader
    logger.info("Starting application...")
    try:
        aspect_loader = AspectsLoader()
        available_versions = aspect_loader.get_available_versions()
        if available_versions:
            logger.info(f"Loaded versions: {', '.join(available_versions)}")
        else:
            logger.warning("No aspect versions found")

        locale_loader = LocaleLoader()
        locales = locale_loader.get_available_locales()
        if locales:
            logger.info(f"Loaded locales: {', '.join([loc['locale'] for loc in locales])}")
        else:
            logger.warning("No locales loaded during startup")

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unavailable")


@api_router.on_event("shutdown")
async def shutdown_event():
    """Application shutdown cleanup"""
    logger.info("Shutting down application...")


@api_router.get("/versions", tags=["Aspect Data"])
async def get_available_versions():
    """Get list of available aspect versions"""
    return aspect_loader.get_available_versions()


@api_router.get("/aspects", tags=["Aspect Data"])
async def get_aspects(version: str = Query(..., description="Aspect version (e.g., 2.7.4)")):
    """
    Get aspect data for specific version (GET request with query parameter)
    Example: /aspects?version=2.7.4
    """
    try:
        data = aspect_loader.get_data(version)
        if not data:
            logger.warning(f"No data found for version {version}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No aspect data available for version {version}"
            )
        return data
    except HTTPException as e:
        logger.warning(f"Failed request for version {version}: {e.detail}")
        raise e


@api_router.get("/locales/{locale}", tags=["Localization"])
async def get_locale(
        locale: str,
        service: LocaleLoader = Depends(lambda: locale_loader)
) -> dict:
    """
    Get localized FAQ content
    - **locale**: Locale code (e.g., en-US, ru-RU)
    """
    data = service.get_locale(locale)
    if not data:
        available = service.get_available_locales()
        logger.warning(f"Locale {locale} not found. Available: {available}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Locale {locale} not found. Available: {available}"
        )
    return data


@api_router.get("/locales", tags=["Localization"])
async def get_available_locales(
        service: LocaleLoader = Depends(lambda: locale_loader)
) -> list:
    """Get list of available locales"""
    return service.get_available_locales()

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
