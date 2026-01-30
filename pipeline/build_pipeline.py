from src.data_loader import AnimeDataloader
from src.vector_store import VectorStoreBuilder
from dotenv import load_dotenv
from utils.logger import get_logger
from utils.custom_exception import CustomException
import sys
import os
from pathlib import Path

load_dotenv()

logger = get_logger(__name__)

# Get the project root directory (parent of pipeline directory)
PROJECT_ROOT = Path(__file__).parent.parent

def main():
    try:
        logger.info("Starting the Build Pipeline")
        # Use absolute paths relative to project root
        original_csv = PROJECT_ROOT / "Data" / "anime_with_synopsis.csv"
        processed_csv = PROJECT_ROOT / "Data" / "anime_processed.csv"
        loader = AnimeDataloader(original_csv=str(original_csv), processed_csv=str(processed_csv))
        processed = loader.load_and_process()
        logger.info(f"Processed data saved to {processed}")

        vector_builder = VectorStoreBuilder(csv_path = processed)
        vector_builder.build_and_save_vectorstore()
        logger.info("Vector store built and saved successfully")
        logger.info("Build Pipeline completed successfully")

    except Exception as e:
        logger.error(f"Error building pipeline: {e}")
        raise CustomException(e, sys.exc_info())

if __name__ == "__main__":
    main()