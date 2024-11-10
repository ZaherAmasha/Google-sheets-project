# This is a logger for the entire project
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detailed logs
)

logger = logging.getLogger()
# logger = logging.getLogger("product_recommendations_project")

log_level = os.getenv("LOG_LEVEL", "INFO")
logger.setLevel(log_level.upper())  # overrides the above level setting
