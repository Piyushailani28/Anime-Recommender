from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

## Vector Store Builder Class
class VectorStoreBuilder:
    def __init__(self, csv_path:str, persist_dir : str="chroma_db"):
        self.csv_path = csv_path
        self.persist_dir = persist_dir
        self.embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  ## initialize the embedding model

    ## Build and Save the Vector Store
    def build_and_save_vectorstore(self):
        ## Load the data from the CSV file
        loader = CSVLoader(
            file_path=self.csv_path, 
            encoding="utf-8",
            metadata_columns=[]     
            )

        ## Load the data 
        data = loader.load()

        ## split the data
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)  ## initialize the splitter
        texts = splitter.split_documents(data) ## apply the splitter to the data and store the result in texts

        ## convert these texts into embedding 
        db = Chroma.from_documents(texts, self.embedding, persist_directory=self.persist_dir)
        db.persist() ## persist the data to the vector store

    ## Load the Vector Store
    def load_vector_store(self):
        return Chroma(persist_directory=self.persist_dir, embedding_function=self.embedding)