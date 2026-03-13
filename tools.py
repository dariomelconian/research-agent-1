from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime

# SEARCH TOOL
search = DuckDuckGoSearchRun()
search_tool = Tool( 
    name="search",
    func=search.run,
    description="Search the web for information",  # knows when to use
)


# WIKI TOOL
# api wrapper
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
# create tool, pass the tool directly to langchain
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)


# CUSTOM TOOL to save to file
def save_to_file(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ({timestamp}) ---\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as file:
        file.write(formatted_text)

    return f"Data saved to {filename} at {timestamp}"

# wrap function as tool
save_tool = Tool(
    name="save_text_to_file",
    func=save_to_file,
    description="Save text data to a file with a timestamp",
)

