import os
import sys
import asyncio
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai


# ------------------------------------------------------------------
# WINDOWS EVENT-LOOP PATCH (avoids RuntimeError)
# ------------------------------------------------------------------
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ------------------------------------------------------------------
# API KEY & GEMINI SETUP
# ------------------------------------------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found in your .env or env vars")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# ------------------------------------------------------------------
# PDF HELPERS
# ------------------------------------------------------------------
def read_pdfs(files) -> str:
    """Extract raw text from a list of uploaded PDFs."""
    text = ""
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def split_text(text: str, size: int = 10_000, overlap: int = 1_000):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=overlap
    )
    return splitter.split_text(text)


def build_vector_store(chunks, path="faiss_index"):
    embeds = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectordb = FAISS.from_texts(chunks, embedding=embeds)
    vectordb.save_local(path)


# ------------------------------------------------------------------
# QA CHAIN (sync client only)
# ------------------------------------------------------------------
def qa_chain():
    prompt = PromptTemplate(
        template=(
            "Answer the question as precisely as possible using ONLY the context "
            "below. If the answer is not present, reply with "
            "'answer is not available in the context.'\n\n"
            "Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
        ),
        input_variables=["context", "question"],
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        streaming=False,
        _enable_async_client=False,  # keep everything synchronous
    )
    return load_qa_chain(llm, chain_type="stuff", prompt=prompt)


def ask_question(question: str, path="faiss_index") -> str:
    embeds = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectordb = FAISS.load_local(
        path, embeds, allow_dangerous_deserialization=True
    )
    docs = vectordb.similarity_search(question, k=4)
    chain = qa_chain()
    result = chain(
        {"input_documents": docs, "question": question},
        return_only_outputs=True,
    )
    return result["output_text"]


# ------------------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Chat with PDFs 🦜🔗📄")
    st.header("Chatbot Using the Pdf", divider="rainbow")

    # ---------- question box ----------
    user_q = st.text_input("Ask a question about your PDFs")
    if user_q:
        with st.spinner("Analyzing…"):
            reply = ask_question(user_q)
        st.markdown("**Reply:** " + reply)

    # ---------- sidebar ----------
    with st.sidebar:
        st.title("Upload your PDFs")
        pdf_files = st.file_uploader(
            "Select one or more PDF files", type=["pdf"], accept_multiple_files=True
        )

        process_clicked = st.button("PDFs Uploading")  # ← only ONE button

        if process_clicked:
            if not pdf_files:
                st.warning("Please upload at least one PDF first.")
            else:
                with st.spinner("Reading and indexing…"):
                    raw = read_pdfs(pdf_files)
                    chunks = split_text(raw)
                    build_vector_store(chunks)
                st.success("Done! You can now ask questions now")

if __name__ == "__main__":
    main()
