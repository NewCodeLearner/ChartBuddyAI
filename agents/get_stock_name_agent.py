from dotenv import load_dotenv
load_dotenv()
import os
from llama_index.core import VectorStoreIndex,Settings
from llama_index.core.tools import QueryEngineTool
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.json import JSONReader
from llama_index.llms.groq import Groq
from llama_index.core.agent.react.base import ReActAgent
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


#set up LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

Settings.llm = Groq(model = "llama-3.3-70b-versatile" , api_key = GROQ_API_KEY)

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Set up RAG for stock names
stock_document =JSONReader().load_data(
    input_file='scripcodes.json'
)



splitter = SentenceSplitter()
stock_nodes = splitter.get_nodes_from_documents(stock_document)
stock_index = VectorStoreIndex(stock_nodes,show_progress=True)

stockname_query_engine = stock_index.as_query_engine()


stockname_tool = QueryEngineTool.from_defaults(
    query_engine=stockname_query_engine,
    description=(
        "Provides NSE Stock Code based on company name"
    )
)



context = """
You are a stock assistant. When a user asks about a company like 'show me the chart for icici bank' or 'give me the chart of Reliance',
you need to:
- Identify the action (e.g., 'show chart') from the query.
- Extract the company name or stock code.
Your response should return the action and the company NSE CODE clearly.

Example input: 'show me the chart for Reliance'
Example output: {'action': 'show chart', 'company': 'RELIANCE'}
Example input: 'show me the chart for Powergrid'
Example output: {'action': 'show chart', 'company': 'POWERGRID'}
Use only the tools provided to answer questions and NOT your own memory.
"""

stockname_tools =[stockname_tool]
stock_name_agent = ReActAgent.from_tools(
    tools = stockname_tools,
    llm = Settings.llm,
    verbose = True,
    context = context
)


#print("generate response!")
#response=stock_name_agent.chat("show me the chart of adani green")
#print("*******\n Response : ",response.response)
