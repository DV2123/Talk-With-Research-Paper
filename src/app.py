import os
from dotenv import load_dotenv
import streamlit as st
from langchain_google_vertexai import VertexAIEmbeddings
from google.cloud import aiplatform
from src.rag import RAG

st.set_page_config(layout="wide")
load_dotenv()

aiplatform.init(
    #project=os.environ.get("PROJECT_ID"),
    project="ardent-case-429614-t1",
    #proejct="proddeploy-429412",
    location="us-central1",
)

@st.cache_resource
def get_embedding_model():
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@003")
    return embeddings


def load_rag(_chat_box):
    embeddings = get_embedding_model()
    rag = RAG(_chat_box, embeddings)
    return rag


def display_source_documents(source_documents):
    for document, score in source_documents:
        metadata = document.metadata
        document_content = document.page_content

        id_ = metadata["id"]
        arxiv_id = metadata["arxiv_id"]
        url_pdf = metadata["url_pdf"]
        title = metadata["title"]
        authors = metadata["authors"]
        published = metadata["published"]

        with st.container(border=True):
            st.markdown(f"* **📰 Title** : {title} (score = {score})")
            st.markdown(f"* **🏷️ ARXIV ID** : **`{arxiv_id}`**")
            st.markdown(f"* **✍️ Authors** : {' ,'.join(authors)}")
            st.markdown(f"* **📅 Publication date** : {published}")
            st.markdown(f"URL 🔗: {url_pdf}")
            st.write(f"context: {document_content}")


input_question = st.text_input("Ask your question")
columns = st.columns(2)

with columns[0]:
    chat_box = st.empty()

rag = load_rag(chat_box)


if input_question.strip() != "":
    with st.spinner("Generating Answer"):
        prediction = rag.predict(input_question)

    answer = prediction["answer"]
    source_documents = prediction["source_documents"]

    with columns[1]:
        st.write("### Source documents")
        display_source_documents(source_documents)
