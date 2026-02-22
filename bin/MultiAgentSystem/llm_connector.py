from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent as _create_agent
from langgraph.checkpoint.memory import InMemorySaver  
import os
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

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
    final_text = ""

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="values",
    ):
        messages = chunk.get("messages", [])
        if not messages:
            continue

        last = messages[-1]

        # ---- AI MESSAGE
        if isinstance(last, AIMessage):

            # Tool call detection
            if last.tool_calls:
                print("\n[Agent decided to call a tool]")
                for call in last.tool_calls:
                    print(f"Tool name: {call['name']}")
                    print(f"Arguments: {call['args']}")
            else:
                # normal assistant response
                if last.content:
                   # print("\n[Assistant]")
                   # print(last.content)
                    final_text = last.content

        # ---- TOOL RESPONSE
        #elif isinstance(last, ToolMessage):
        #    print("\n[Tool returned result]")
        #    print(last.content)

    return final_text

