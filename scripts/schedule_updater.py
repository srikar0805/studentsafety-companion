"""
Scheduler for Automated Data Updates

Runs data_fetcher.py on a configurable schedule.
Supports both continuous scheduling (for server deployment) and one-time runs (for cron/Task Scheduler).
"""

import schedule
import time
import logging
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import the data fetcher
from data_fetcher import run_data_update, trigger_etl

load_dotenv()

# Logging setup
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'scheduler_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Schedule Configuration (from environment or defaults)
CONFIG = {
    "MUPD_CRIME_LOG_SCHEDULE": os.getenv("MUPD_CRIME_LOG_SCHEDULE", "daily_03:00"),
    "CPD_CRIME_DATA_SCHEDULE": os.getenv("CPD_CRIME_DATA_SCHEDULE", "weekly_sunday_02:00"),
    "MUPD_INCIDENT_LOG_SCHEDULE": os.getenv("MUPD_INCIDENT_LOG_SCHEDULE", "daily_03:30"),
    "AUTO_RUN_ETL": os.getenv("AUTO_RUN_ETL", "true").lower() == "true",
    "CONTINUOUS_MODE": os.getenv("CONTINUOUS_MODE", "false").lower() == "true"
}


def parse_schedule(schedule_str):
    """
    Parse schedule string into schedule configuration
    
    Formats supported:
    - "hourly" or "hourly_:30" (every hour at :30)
    - "daily_HH:MM" (every day at HH:MM)
    - "weekly_DAY_HH:MM" (every DAY at HH:MM)
    
    Examples:
    - "hourly" → every hour
    - "daily_03:00" → every day at 3:00 AM
    - "weekly_sunday_02:00" → every Sunday at 2:00 AM
    """
    parts = schedule_str.lower().split('_')
    
    if parts[0] == "hourly":
        minute = parts[1] if len(parts) > 1 else ":00"
        return {"type": "hourly", "minute": minute.lstrip(':')}
    
    elif parts[0] == "daily":
        time = parts[1] if len(parts) > 1 else "03:00"
        return {"type": "daily", "time": time}
    
    elif parts[0] == "weekly":
        day = parts[1] if len(parts) > 1 else "sunday"
        time = parts[2] if len(parts) > 2 else "02:00"
        return {"type": "weekly", "day": day, "time": time}
    
    else:
        logger.warning(f"Unknown schedule format: {schedule_str}, defaulting to daily 03:00")
        return {"type": "daily", "time": "03:00"}


def job_with_etl():
    """Job that runs data fetcher and optionally triggers ETL"""
    logger.info("Scheduled job started")
    results = run_data_update()
    
    if CONFIG["AUTO_RUN_ETL"] and any(r.get('status') == 'success' for r in results):
        logger.info("New data fetched - triggering ETL pipeline")
        trigger_etl()
    
    logger.info("Scheduled job completed")


def setup_schedules():
    """Setup all scheduled jobs based on configuration"""
    logger.info("Setting up data update schedules...")
    logger.info(f"Configuration: {CONFIG}")
    
    # For now, we'll use a single unified schedule
    # In production, you could set up individual schedules per source
    
    # Default: Daily at 3:00 AM
    default_schedule = parse_schedule(CONFIG["MUPD_CRIME_LOG_SCHEDULE"])
    
    if default_schedule["type"] == "hourly":
        minute = default_schedule.get("minute", "00")
        schedule.every().hour.at(f":{minute}").do(job_with_etl)
        logger.info(f"Scheduled: Hourly at :{minute}")
    
    elif default_schedule["type"] == "daily":
        time_str = default_schedule["time"]
        schedule.every().day.at(time_str).do(job_with_etl)
        logger.info(f"Scheduled: Daily at {time_str}")
    
    elif default_schedule["type"] == "weekly":
        day = default_schedule["day"]
        time_str = default_schedule["time"]
        
        day_map = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday
        }
        
        scheduler = day_map.get(day, schedule.every().sunday)
        scheduler.at(time_str).do(job_with_etl)
        logger.info(f"Scheduled: Weekly on {day.capitalize()} at {time_str}")
    
    logger.info("Schedule setup complete")


def run_continuous():
    """Run scheduler in continuous mode (for server deployment)"""
    logger.info("Starting scheduler in CONTINUOUS mode")
    logger.info("Press Ctrl+C to stop")
    
    setup_schedules()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


def run_once():
    """Run data update once (for cron/Task Scheduler)"""
    logger.info("Running data update (one-time execution)")
    job_with_etl()
    logger.info("One-time execution complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Schedule automated data updates")
    parser.add_argument(
        "--mode",
        choices=["continuous", "once"],
        default="once",
        help="Run mode: continuous (server) or once (cron)"
    )
    
    args = parser.parse_args()
    
    # Override with environment variable if set
    if CONFIG["CONTINUOUS_MODE"]:
        args.mode = "continuous"
    
    if args.mode == "continuous":
        run_continuous()
    else:
        run_once()
