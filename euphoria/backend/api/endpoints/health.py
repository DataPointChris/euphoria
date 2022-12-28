import os
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter
from euphoria import __version__
from euphoria.backend.common import schemas

router = APIRouter(prefix='/health', tags=['health'])


# TODO: It would be cool to have a test that ran after upgrading an api
# that hit this endpoint to make sure that the versions match so it got updated.
@router.get("/", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    return {
        'name': 'Euphoria API',
        'version': __version__,
        'environment': os.getenv('ENVIRONMENT', 'NOT SET'),
        'api_url': os.getenv('API_URL', 'NOT SET'),
        'log_level': os.getenv('LOG_LEVEL', 'NOT SET'),
        'server_time': datetime.now().isoformat(),
        'local_time': datetime.now(tz=ZoneInfo('America/Chicago')).isoformat()
    }
