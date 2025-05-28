from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"


embeddings = OllamaEmbeddings( model="gemma:2b")


VECTOR_DIR = "./vectorstore"

# Create or load vectorstore from disk
def get_vectorstore():
    try:
        if os.path.exists(os.path.join(VECTOR_DIR, "index.faiss")) and os.path.exists(os.path.join(VECTOR_DIR, "index.pkl")):
            print("[VectorStore] ✅ Loading vectorstore from disk...")
            vs = FAISS.load_local(VECTOR_DIR, embeddings, allow_dangerous_deserialization=True)
            print("[VectorStore] ✅ Load successful.")
            return vs
        else:
            print("[VectorStore] ***No FAISS index files found.")
            return None
    except Exception as e:
        print(f"[VectorStore]  ***Failed to load vectorstore: {e}")
        return None

# adds new notes into the vectorstore
def add_notes_to_vectorstore(notes: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    splits = text_splitter.split_text(notes)

    vs = get_vectorstore()

    if vs is None:
        # No existing database, create fresh
        vs = FAISS.from_texts(splits, embedding=embeddings)
    else:
        # Existing database, add to it
        vs.add_texts(splits)

    # Save updated database
    vs.save_local(VECTOR_DIR)
    print("[VectorStore] *** Notes saved to vectorstore.")



