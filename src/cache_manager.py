from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache, SQLiteCache

def initialize_cache(cache_type: str):
    """Sets the LangChain caching method."""
    if cache_type == "SQLiteCache":
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))
    else:
        set_llm_cache(InMemoryCache())