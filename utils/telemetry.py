import os
import logging
from dotenv import load_dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger(__name__)

def setup_simple_telemetry():
    try:
        load_dotenv(override=True)

        connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

        if not connection_string:
            logger.warning("Application Insights connection string not found")
            return False

        configure_azure_monitor(
            connection_string=connection_string,
            enable_live_metrics=True,
            enable_standard_metrics=True
        )

        logger.info("Application Insights configured successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to configure Application Insights: {str(e)}")
        return False

def instrument_fastapi_app(app):
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented for telemetry")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {str(e)}")
