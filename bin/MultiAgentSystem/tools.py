# bin/MultiAgentSystem/tools.py
import os
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
from serpapi import GoogleSearch
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools import tool
load_dotenv()

# ---- ENV VARS ----

SERP_API_KEY = os.getenv("SERP_API_KEY")
if not SERP_API_KEY:
    raise RuntimeError("SERP_API_KEY not set in .env")

USER_AGENT = os.getenv(
    "USER_AGENT",
    "AI4ED-TuringProject/0.1 (mailto:your.email@example.com)",
)

def retriever_relevant_docs(query: str):
    """Internal helper: Google Scholar (via SerpAPI) -> pages -> relevant docs."""
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": SERP_API_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", []) or []

    urls = [r.get("link") for r in organic_results[:60] if r.get("link")]

    docs = []
    for url in urls:
        # Optional: skip sites that often block bots
        if "researchgate.net" in url:
            continue
        try:
            loader = WebBaseLoader(
                web_paths=[url],
                header_template={"User-Agent": USER_AGENT},
            )
            docs.extend(loader.load())
        except Exception as e:
            print(f"Failed to load {url}: {e}")

    if not docs:
        return []

    # Flatten, split, embed, build retriever
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=100,
    )
    doc_splits = text_splitter.split_documents(docs)

    vectorstore = InMemoryVectorStore.from_documents(
        documents=doc_splits,
        embedding=OpenAIEmbeddings(),  # needs OPENAI_API_KEY in .env
    )
    retriever = vectorstore.as_retriever()

    # Get the top matches for the same query
    return retriever.invoke(query)


@tool("retrieve_knowledge")
def retrieve_knowledge(query: str) -> str:
    """Search and return concise information about a certain topic."""
    docs = retriever_relevant_docs(query)
    if not docs:
        return "I couldn't find any relevant documents for that topic."
    #print("Retreival DOne")
    # Return a few chunks concatenated
    return "\n\n".join(doc.page_content for doc in docs)


class Tools:
    """Container for all LangChain tools used by agents in the planning module."""

    # Google Search Tool
    search_wrapper = GoogleSearchAPIWrapper(k=5)

    google_search = Tool(
        name="google_search",
        description="Search Google for recent results.",
        func=search_wrapper.run,
    )

    # Subject knowledge tool
    knowledge_retreiver = retrieve_knowledge
