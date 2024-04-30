import argparse
import os
import shutil
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain.vectorstores.chroma import Chroma
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders.csv_loader import UnstructuredCSVLoader# from urls import urls
CHROMA_PATH = "chroma"
DATA_PATH = "data"

urls=['https://tailwindcomponents.com/component/social-ntwrk', 'https://tailwindcomponents.com/component/tailwind-css-cards-social', 'https://windstatic.com/errors', 'https://tw-elements.com/docs/standard/methods/ripple/', 'https://tailwindcomponents.com/component/airbnb-clone', 'https://tailwindcomponents.com/component/user-avatar-with-presence-indicator', 'https://fancytailwind.com/app/fancy-laboratory/atoms/avatars/avatar7', 'https://fancytailwind.com/app/fancy-laboratory/molecules/promosections/promoSection13', 'https://github.com/brendan-c/Tailwindcss-Counter', 'https://tailwindcomponents.com/component/simple-button-animation-scale', 'https://tailwindcomponents.com/component/grid-responsive-tailwind-css', 'https://github.com/iozcelik/SarissaPersonalBlog', 'https://tailwindcomponents.com/component/list-group', 'https://mambaui.com/components/footer', 'https://tailwindui.com/components/preview#component-fd7b8bd425f42f6504b22e1ecc6b43c9', 'https://postsrc.com/components/buttons/pill-buttons', 'https://tailwindcomponents.com/component/error-404-1', 'https://fancytailwind.com/app/fancy-laboratory/organisms/teams/team1', 'https://sailboatui.com/docs/components/dropdown/#default', 'https://github.com/ttntm/11ty-landing-page']




def populate_database(reset=False):
    # Check if the database should be cleared (using the --clear flag).
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--reset", action="store_true", help="Reset the database.")
    # args = parser.parse_args()
    if reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def load_documents():   
    # document_loader = UnstructuredMarkdownLoader(DATA_PATH)
    # document_loader = PyPDFDirectoryLoader(DATA_PATH)
    document_loader = UnstructuredCSVLoader(
    file_path="data/uiforge.csv"
    )
    return document_loader.load()
    # docs = [WebBaseLoader(url).load() for url in urls]
    # docs_list = [item for sublist in docs for item in sublist]
    # return docs_list


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    populate_database()
