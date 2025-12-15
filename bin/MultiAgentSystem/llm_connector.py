from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent as _create_agent
from langgraph.checkpoint.memory import InMemorySaver  
import os
load_dotenv()

os.environ.get("OPENAI_API_KEY")


def create_agent(system_prompt: str, model_name = "gpt-4.1-mini", tools: list = None): 
    # Initialize the LLM model
    llm = ChatOpenAI(
     model=model_name,
     temperature=0.1,
     max_tokens=10000,
     timeout=300,
    # ... (other params)
   )

    # Create the agent
    agent = _create_agent(llm, tools=tools, system_prompt=system_prompt, checkpointer=InMemorySaver())
    return agent

def chat(agent: object, user_input: str, thread_id: str) -> str:
    latest_message = None

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": thread_id}},  
        stream_mode="values",
    ):
        #print("Received chunk:", chunk)

        # Each chunk contains the full state at that point
        latest_message = chunk["messages"][-1]

        # If you want to see only the model text instead of the whole chunk:
        # if latest_message.content:
        #     print("Assistant:", latest_message.content)

    # Safeguard in case something weird happens and there are no chunks
    return latest_message.content if latest_message is not None else ""
