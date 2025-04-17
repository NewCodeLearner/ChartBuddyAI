from dotenv import load_dotenv
load_dotenv()
import os
from llama_index.core import VectorStoreIndex,Settings,Document
from llama_index.core.tools import QueryEngineTool
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.json import JSONReader
from llama_index.llms.groq import Groq
from llama_index.core.agent.react.base import ReActAgent
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import pandas as pd


#set up LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

Settings.llm = Groq(model = "llama-3.3-70b-versatile" , api_key = GROQ_API_KEY)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

#read nse500 stocklist 
filename = 'ind_nifty500list.csv'
data_frame = pd.read_csv(filename)
data_dict = data_frame.to_dict(orient='records')

#Convert data_dict to a list of Document objects
documents = [
    Document(
        text=f"Company Name: {item['Company Name']}, Industry: {item['Industry']}, Symbol: {item['Symbol']}"
    )
    for item in data_dict
]

splitter = SentenceSplitter()
stock_nodes = splitter.get_nodes_from_documents(documents)
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
Example output: {'action': 'show chart', 'symbol': 'RELIANCE'}
Example input: 'show me the chart for Powergrid'
Example output: {'action': 'show chart', 'symbol': 'POWERGRID'}
Use only the tools provided to answer questions and NOT your own memory.
"""

stockname_tools =[stockname_tool]

#Agent Creation:
def create_stock_name_agent():
    """
    Function to create and return the stock name agent.
    """
    return ReActAgent.from_tools(
        tools = stockname_tools,
        llm = Settings.llm,
        verbose = True,
        context = context
    )

# The global agent instance (you can initialize it here)
stock_name_agent = create_stock_name_agent()

# Query handling interface
def get_stock_name(user_query):
    """
    Pass a query to the agent and return the response.
    """
    response = stock_name_agent.query(user_query)  # Use the query method
    return response.response



#response=stock_name_agent.chat("show me the chart of Central Bank of India")
#print("*******\n Response : ",response.response)

#> Running step b8c8e5d4-818d-42bd-99b1-d0b979849927. Step input: show me the chart of Central Bank of India
#  Thought: The current language of the user is: English. I need to use a tool to help me answer the question.
#  Action: query_engine_tool
#  Action Input: {'input': 'Central Bank of India'}
#  Observation: Central Bank of India is in the Financial Services industry and has the symbol CENTRALBK.
# > Running step c69b5a13-2b88-49d6-aeb2-8c0e9db3b5da. Step input: None
#  Thought: I can extract the action from the user's query and the company symbol from the tool's response.
#  Answer: {'action': 'show chart', 'symbol': 'CENTRALBK'}
#  *******
#   Response :  {'action': 'show chart', 'symbol': 'CENTRALBK'}

response=stock_name_agent.chat("show me the chart of Cholamandalam Investment")
print("*******\n Response : ",response.response)
