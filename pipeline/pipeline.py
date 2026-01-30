from src.vector_store import VectorStoreBuilder
from src.recommender import AnimeRecommender
from config.config import GROQ_API_KEY, MODEL_NAME
from utils.logger import get_logger
from utils.custom_exception import CustomException
import sys

logger = get_logger(__name__)

class AnimeRecommenderPipeline:
    def __init__(self, persist_dir = "chroma_db"):
        try:
            logger.info("Initializing Anime Recommender Pipeline")

            vector_builder = VectorStoreBuilder(csv_path = "", persist_dir = persist_dir)
            retriever = vector_builder.load_vector_store().as_retriever()
            self.recommender = AnimeRecommender(retriever = retriever, api_key = GROQ_API_KEY, model_name = MODEL_NAME)
            logger.info("Anime Recommender Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Anime Recommender Pipeline: {e}")
            raise CustomException(e, sys.exc_info())

    def recommend(self, query:str) -> str:
        try:
            logger.info(f"received a query {query}")
            recommendation = self.recommender.get_recommendations(query = query)
            logger.info(f"recommendation Generated: {recommendation}")
            return recommendation
        except Exception as e:
            logger.error(f"Error recommending anime: {e}")
            raise CustomException(e, sys.exc_info())