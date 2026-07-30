"""Start the BuildSense AI Flask development server."""

from app import create_app
from config.settings import get_settings

settings = get_settings()
app = create_app()

if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
