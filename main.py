from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from langchain.agents import create_tool_calling_agent, AgentExecutor

# tools import
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

# generate llm (open ai)
#llm2 = ChatOpenAI(model="gpt-4-0613", temperature=0.9)

'''
test API
response = llm.invoke("What is the meaning of life?")
print(response)
'''

# class for specific type of content we want our llm to generate
# give prompt, answer user q, as part of reply, generate using this schema..
# this is format

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# generate llm
llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0.9)

# parser
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# create prompt with prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant. You will be given a research topic, and you will provide a summary of the topic, along with sources and tools used, that will help generate a research paper.
            Answer the user query and use necessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# tools use 
tools = [search_tool, wiki_tool, save_tool]

# create simple agent
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    #output_parser=parser,
)

# agent executor for response generation
# verbose for thought process
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# get from user
query = input("What do you want to research? ")

# PRE TOOL response (basic test of invoke without tools)
#raw_response = agent_executor.invoke({"query": "What does the word yearn mean?"})
#print(raw_response)

# use tool 

# sample query used:  "Singapore population, save to text"
raw_response = agent_executor.invoke({"query": query})


# parse into python obj
try:
    output = raw_response.get("output")
    if isinstance(output, list):
        output = output[0]["text"]
    structured_response = parser.parse(output)
    print(structured_response)
except Exception as e:
    print("Error parsing response:", e, "Raw Response - ", raw_response)

# call tools so llm/agent can use them next.
