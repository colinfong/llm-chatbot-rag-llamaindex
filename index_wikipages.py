import llama_index # LLMs for applications
from llama_index.readers.wikipedia import WikipediaReader # read and retrieve Wiki data
from llama_index.core.indices.vector_store import VectorStoreIndex # in memory vector store
from llama_index.core.node_parser import SentenceSplitter # split text during preprocessing
from llama_index.program.openai import OpenAIPydanticProgram #  
from llama_index.llms.openai import OpenAI
from utils import get_apikey
from pydantic import BaseModel
from typing import List
import openai
import wikipedia

"""
A vector store is a database of documents split into chunks and embedded
embedded means the data is converted into vectors or numbers which represent
semantic data points. This allows a model to search for relevant data by
semantic similarity

Vector databases store documents in chunks which are embedded into vectors
which allows a model to search for data via semantic similarity.
"""


# define the data model in pydantic
class WikiPageList(BaseModel):
    "Data model for WikiPageList"
    pages: List[str]


def wikipage_list(query):
    openai.api_key = get_apikey()

    prompt_template_str = """
    Given the input {query},
    extract the Wikipedia pages mentioned after
    "please index:" and return them as a list.
    If only one page is mentioned, return a single
    element list.
    """
    program = OpenAIPydanticProgram.from_defaults(
        output_cls=WikiPageList,
        prompt_template_str=prompt_template_str,
        llm=OpenAI(model="gpt-4o-mini"), # default gpt-3.5-turbo is deprecated
        verbose=True,
    )

    wikipage_requests = program(query=query)

    return wikipage_requests


def create_wikidocs(wikipage_requests):
    # Wikipedia rate limits the library's shared default user agent
    wikipedia.set_user_agent("LLMChatbotRAG/0.1 (personal learning project)")

    reader = WikipediaReader()
    # auto_suggest off, otherwise "paris" gets "corrected" to "parks"
    documents = reader.load_data(pages=wikipage_requests, auto_suggest=False)

    return documents


def create_index(query):
    global index
    wikipage_requests = wikipage_list(query)
    documents = create_wikidocs(wikipage_requests.pages)

    text_splits = SentenceSplitter(chunk_size=150, chunk_overlap=45)
    nodes = text_splits.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes)

    return index


if __name__ == "__main__":
    query = "/get wikipages: paris, lagos, laos"
    index = create_index(query)
    print("INDEX CREATED", index)
