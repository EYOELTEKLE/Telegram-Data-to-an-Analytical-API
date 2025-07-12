from dagster import Definitions
from .jobs import telegram_data_pipeline, telegram_data_schedule

defs = Definitions(
    jobs=[telegram_data_pipeline],
    schedules=[telegram_data_schedule]
)
