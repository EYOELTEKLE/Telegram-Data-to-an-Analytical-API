from dagster import job, op, ScheduleDefinition
import subprocess

@op
def scrape_telegram_data():
    subprocess.run(["python", "scripts/scrape_telegram.py"], check=True)

@op
def load_raw_to_postgres():
    subprocess.run(["python", "scripts/load_telegram_to_postgres.py"], check=True)

@op
def run_dbt_transformations():
    subprocess.run(["dbt", "run"], cwd="my_project", check=True)

@op
def run_yolo_enrichment():
    subprocess.run(["python", "scripts/detect_and_store_images.py"], check=True)

@job
def telegram_data_pipeline():
    scrape_telegram_data()
    load_raw_to_postgres()
    run_dbt_transformations()
    run_yolo_enrichment()

# Optional: schedule to run daily at midnight
telegram_data_schedule = ScheduleDefinition(
    job=telegram_data_pipeline,
    cron_schedule="0 0 * * *"
)
