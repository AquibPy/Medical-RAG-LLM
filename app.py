from langchain import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain_community.embeddings import SentenceTransformerEmbeddings
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
import settings
import json


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

local_llm = settings.LLM_PATH

llm = LlamaCpp(
    model_path= local_llm,
    temperature=0.3,
    max_tokens=2048,
    top_p=1
)

print("LLM Initialized....")

embeddings = SentenceTransformerEmbeddings(model_name=settings.EMBEDDINGS)

client = QdrantClient(
    url=settings.VECTOR_DB_URL, prefer_grpc=False
)

db = Qdrant(client=client, embeddings=embeddings, collection_name=settings.VECTOR_DB_NAME)

prompt = PromptTemplate(template=settings.PROMPT_TEMPLATE, input_variables=['context', 'question'])

retriever = db.as_retriever(search_kwargs={"k":1})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get_response")
async def get_response(query: str = Form(...)):
    chain_type_kwargs = {"prompt": prompt}
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True, chain_type_kwargs=chain_type_kwargs, verbose=True)
    response = qa(query)
    print(response)
    answer = response['result']
    source_document = response['source_documents'][0].page_content
    doc = response['source_documents'][0].metadata['source']
    response_data = jsonable_encoder(json.dumps({"answer": answer, "source_document": source_document, "doc": doc}))
    res = Response(response_data)
    return res
