from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from src.prompt_template import get_anime_prompt

class AnimeRecommender:
    def __init__(self, retriever, api_key:str, model_name:str):
        self.llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.0)
        self.prompt = get_anime_prompt()

        docs_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.qa_chain = create_retrieval_chain(retriever, docs_chain)

    def get_recommendations(self, query:str):
        result = self.qa_chain.invoke({"input": query})
        return result["answer"]