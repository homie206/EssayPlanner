#functions that can be used by agents as tools
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper

load_dotenv()

class Tools:
    """Container for all LangChain tools used by agents in the planning module."""

    # Google Search Tool
    search_wrapper = GoogleSearchAPIWrapper(k=5)

    google_search = Tool(
        name="google_search",
        description="Search Google for recent results.",
        func=search_wrapper.run,
    )
