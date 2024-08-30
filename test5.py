from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from dotenv import load_dotenv
import base64
import os
load_dotenv()
import logging

from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_gigachat_functions_agent

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def add(a: int, b: int) -> int:
    """Складывает числа a и b."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Умножает a на b."""
    return a * b

tools = [add, multiply]

client_id = os.environ['client_id']
secret = os.environ['client_secret']

credentials = f"{client_id}:{secret}"
auth= base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

giga = GigaChat(credentials=auth,
                model='GigaChat:latest',
                verify_ssl_certs=False
                )

agent = create_gigachat_functions_agent(giga, tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

query = "Сколько будет 3 * 12? А еще сколько будет 47 плюс 20"
#query = "Привет!"
# result=agent_executor.invoke(        {
#             "input": query,
#         })
# print(result)
llm_with_tools = giga.bind_tools(tools)
result=llm_with_tools.invoke(query)
print(result)

