"""
Automated Data Fetcher for Crime Logs and Safety Data

Fetches fresh data from MUPD, CPD, and other sources on a scheduled basis.
Designed to run via cron job or Windows Task Scheduler.
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
CRIME_LOGS_DIR = DATA_DIR / "crime_logs"
CRIME_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'data_fetcher_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Data Source Configuration
DATA_SOURCES = {
    "MUPD_CRIME_LOG": {
        "url": os.getenv("MUPD_CRIME_LOG_URL", "https://police.missouri.edu/daily-crime-log/"),
        "update_frequency": "daily",  # daily, weekly, hourly
        "enabled": True,
        "fetch_method": "scrape"  # scrape, api, download
    },
    "CPD_CRIME_DATA": {
        "url": os.getenv("CPD_CRIME_DATA_URL", "https://www.como.gov/CMS/gis/crimedata.php"),
        "update_frequency": "weekly",
        "enabled": True,
        "fetch_method": "api"  # ArcGIS REST API
    },
    "MUPD_INCIDENT_LOG": {
        "url": os.getenv("MUPD_INCIDENT_LOG_URL", "https://police.missouri.edu/daily-incident-log/"),
        "update_frequency": "daily",
        "enabled": True,
        "fetch_method": "scrape"
    }
}


class DataFetcher:
    """Base class for data fetching operations"""
    
    def __init__(self, source_name, config):
        self.source_name = source_name
        self.config = config
        self.logger = logging.getLogger(f"DataFetcher.{source_name}")
    
    def should_update(self):
        """Check if data should be updated based on last fetch time"""
        last_file = self.get_latest_file()
        if not last_file:
            return True
        
        file_date = self.extract_date_from_filename(last_file)
        if not file_date:
            return True
        
        frequency = self.config.get("update_frequency", "daily")
        now = datetime.now()
        
        if frequency == "hourly":
            return (now - file_date).total_seconds() > 3600
        elif frequency == "daily":
            return (now - file_date).days >= 1
        elif frequency == "weekly":
            return (now - file_date).days >= 7
        
        return True
    
    def get_latest_file(self):
        """Get the most recent data file for this source"""
        files = list(CRIME_LOGS_DIR.glob(f"{self.source_name.lower()}*.csv"))
        if not files:
            return None
        return max(files, key=lambda f: f.stat().st_mtime)
    
    def extract_date_from_filename(self, filepath):
        """Extract date from filename (format: source_YYYYMMDD.csv)"""
        try:
            filename = filepath.stem
            date_str = filename.split('_')[-1]
            return datetime.strptime(date_str, "%Y%m%d")
        except:
            return None
    
    def fetch(self):
        """Fetch data from source - to be implemented by subclasses"""
        raise NotImplementedError
    
    def save(self, data, suffix=""):
        """Save fetched data to CSV"""
        datestamp = datetime.now().strftime("%Y%m%d%H%M") if suffix else datetime.now().strftime("%Y%m%d")
        filename = f"{self.source_name.lower()}_{datestamp}.csv"
        filepath = CRIME_LOGS_DIR / filename
        
        data.to_csv(filepath, index=False)
        self.logger.info(f"Saved {len(data)} records to {filename}")
        return filepath


class MUPDCrimeLogFetcher(DataFetcher):
    """Fetcher for MUPD Daily Crime Log"""
    
    def fetch(self):
        """
        Fetch MUPD crime log data
        
        Note: This is a placeholder. Actual implementation depends on:
        - If MUPD provides an API: use requests.get()
        - If data is on a webpage: use BeautifulSoup to scrape
        - If data is a downloadable CSV: use pandas.read_csv()
        """
        self.logger.info(f"Fetching MUPD crime log from {self.config['url']}")
        
        try:
            # Example: If MUPD provides CSV download
            # df = pd.read_csv(self.config['url'])
            
            # Example: If using web scraping
            # from bs4 import BeautifulSoup
            # response = requests.get(self.config['url'])
            # soup = BeautifulSoup(response.content, 'html.parser')
            # # Parse table data...
            
            # Placeholder: Return empty DataFrame with expected schema
            self.logger.warning("MUPD fetcher not implemented - using placeholder")
            df = pd.DataFrame(columns=[
                'Case Number', 
                'Date/Time Reported', 
                'Location of Occurence', 
                'Incident Type', 
                'Disposition'
            ])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching MUPD data: {e}")
            return None


class CPDCrimeDataFetcher(DataFetcher):
    """Fetcher for Columbia PD Crime Data (ArcGIS)"""
    
    def fetch(self):
        """
        Fetch CPD crime data from ArcGIS REST API
        
        Columbia PD likely uses ArcGIS Server for crime data.
        This fetcher queries the REST API endpoint.
        """
        self.logger.info(f"Fetching CPD crime data from ArcGIS API")
        
        try:
            # Example ArcGIS REST API query
            # Adjust based on actual CPD endpoint
            api_url = self.config.get('url')
            
            # Query parameters for recent data (last 30 days)
            days_back = int(os.getenv("CPD_FETCH_DAYS", "30"))
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            params = {
                "where": f"report_date >= '{date_filter}'",
                "outFields": "*",
                "f": "json",
                "resultRecordCount": 10000  # Fetch up to 10k records
            }
            
            # Placeholder: Actual API call would be:
            # response = requests.get(f"{api_url}/query", params=params)
            # data = response.json()
            # df = pd.DataFrame(data['features'])
            
            self.logger.warning("CPD ArcGIS fetcher not implemented - using placeholder")
            df = pd.DataFrame(columns=[
                'offense_id',
                'report_date', 
                'nibrs_description',
                'full_address',
                'x',
                'y'
            ])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching CPD data: {e}")
            return None


class MUPDIncidentLogFetcher(DataFetcher):
    """Fetcher for MUPD Daily Incident Log"""
    
    def fetch(self):
        """Fetch MUPD incident log (similar to crime log but different format)"""
        self.logger.info(f"Fetching MUPD incident log from {self.config['url']}")
        
        try:
            # Placeholder implementation
            self.logger.warning("MUPD incident log fetcher not implemented - using placeholder")
            df = pd.DataFrame(columns=[
                'Incident Number',
                'Date/Time',
                'Location',
                'Nature',
                'Disposition'
            ])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching MUPD incident log: {e}")
            return None


def run_data_update():
    """Main function to run all data fetchers"""
    logger.info("=" * 60)
    logger.info("Starting automated data update")
    logger.info(f"Current time: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Fetcher mapping
    fetchers = {
        "MUPD_CRIME_LOG": MUPDCrimeLogFetcher,
        "CPD_CRIME_DATA": CPDCrimeDataFetcher,
        "MUPD_INCIDENT_LOG": MUPDIncidentLogFetcher
    }
    
    results = []
    
    for source_name, config in DATA_SOURCES.items():
        if not config.get("enabled", False):
            logger.info(f"Skipping {source_name} (disabled)")
            continue
        
        logger.info(f"\n--- Processing {source_name} ---")
        
        fetcher_class = fetchers.get(source_name)
        if not fetcher_class:
            logger.warning(f"No fetcher implementation for {source_name}")
            continue
        
        fetcher = fetcher_class(source_name, config)
        
        # Check if update is needed
        if not fetcher.should_update():
            logger.info(f"Skipping {source_name} - data is up to date")
            continue
        
        # Fetch data
        data = fetcher.fetch()
        
        if data is not None and len(data) > 0:
            # Save data
            filepath = fetcher.save(data)
            results.append({
                "source": source_name,
                "status": "success",
                "records": len(data),
                "file": str(filepath)
            })
            logger.info(f"✓ {source_name}: Fetched {len(data)} records")
        else:
            results.append({
                "source": source_name,
                "status": "failed",
                "records": 0
            })
            logger.warning(f"✗ {source_name}: No data fetched")
    
    logger.info("\n" + "=" * 60)
    logger.info("Data update complete")
    logger.info(f"Successfully updated: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")
    logger.info("=" * 60)
    
    return results


def trigger_etl():
    """Trigger the ETL pipeline to load newly fetched data into database"""
    logger.info("Triggering ETL pipeline to load new data...")
    
    try:
        # Import and run the existing load_data script
        from etl.load_data import (
            get_engine, 
            load_mupd_crime_logs, 
            load_cpd_crime_data
        )
        
        engine = get_engine()
        load_mupd_crime_logs(engine)
        load_cpd_crime_data(engine)
        
        logger.info("✓ ETL pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"✗ ETL pipeline failed: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch and update crime data")
    parser.add_argument(
        "--run-etl", 
        action="store_true",
        help="Run ETL pipeline after fetching data"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if data is recent"
    )
    
    args = parser.parse_args()
    
    # Override should_update if force flag is set
    if args.force:
        logger.info("Force update enabled - ignoring update frequency checks")
        for config in DATA_SOURCES.values():
            config['force_update'] = True
    
    # Run data fetchers
    results = run_data_update()
    
    # Optionally run ETL
    if args.run_etl and any(r['status'] == 'success' for r in results):
        trigger_etl()
