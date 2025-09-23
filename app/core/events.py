from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

# Startup event: called when app starts
def create_start_app_handler(app: FastAPI, settings):
    async def start_app():
        # Initialize DB connections
        if hasattr(app.state, "db"):
            await app.state.db.connect()
        # Initialize cache / external APIs if needed
        logger.info("Song Library API starting up...")
    return start_app

# Shutdown event: called when app stops
def create_stop_app_handler(app: FastAPI):
    async def stop_app():
        # Close DB connections
        if hasattr(app.state, "db"):
            await app.state.db.disconnect()
        # Close cache / other resources
        logger.info("Song Library API shutting down...")
    return stop_app
