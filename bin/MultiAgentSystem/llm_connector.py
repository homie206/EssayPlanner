from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
import os
load_dotenv()

os.environ.get("OPENAI_API_KEY")

def chat(system_prompt: str, user_input: str):

    # Initialize the LLM model
    model = ChatOpenAI(
     model="gpt-4.1-mini",
     temperature=0.1,
     max_tokens=1000,
     timeout=30
    # ... (other params)
   )
   
   # Create the agent
    agent = create_agent(model, system_prompt=system_prompt)
   
   # Print the system prompt
   #uncomment this if you want to see the system prompt
   #print("Agent created with system prompt:", system_prompt)
   
   # Stream the response
    for chunk in agent.stream({
     "messages": [{"role": "user", "content": user_input}]
 }, stream_mode="values"):
     # Each chunk contains the full state at that point
     latest_message = chunk["messages"][-1]
     #uncomment this if you want to print the agent's last response or tool calls
     #if latest_message.content:
     #    print(f"Agent: {latest_message.content}")
     #elif latest_message.tool_calls:
     #    print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
#
    return latest_message.content