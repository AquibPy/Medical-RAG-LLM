import os
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
import settings

embeddings = SentenceTransformerEmbeddings(model_name=settings.EMBEDDINGS)

print(embeddings)

loader = DirectoryLoader(settings.DATA_DIR, glob="**/*.pdf", show_progress=True, loader_cls=UnstructuredFileLoader)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=70)

texts = text_splitter.split_documents(documents)

print(texts[1])

qdrant = Qdrant.from_documents(
    texts,
    embeddings,
    url=settings.VECTOR_DB_URL,
    prefer_grpc=False,
    collection_name=settings.VECTOR_DB_NAME
)

print("Vector DB Successfully Created!")