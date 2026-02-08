import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from browser_use import Agent
import asyncio

app = FastAPI()

# Input schema
class TaskRequest(BaseModel):
    instruction: str

# Fix: Custom class to add the missing 'provider' attribute
class CustomChatAnthropic(ChatAnthropic):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def provider(self):
        return "anthropic"

@app.get("/")
def home():
    return {"status": "Power BI Agent is Awake"}

@app.post("/run")
async def run_agent(request: TaskRequest):
    """
    Sends the AI agent to the Power BI dashboard to execute the instruction.
    """
    try:
        # 1. Setup the Brain (Claude 3.5 Sonnet is BEST for computer use)
        # It will automatically look for 'ANTHROPIC_API_KEY' in env variables
        llm = CustomChatAnthropic(
            model_name="claude-3-5-sonnet-20240620", 
            temperature=0.0
        )

        # 2. Define the exact Power BI URL
        # We hardcode this so you don't have to pass it every time, 
        # but you can make it dynamic if you want.
        power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiNGI5OWM4NzctMDExNS00ZTBhLWIxMmYtNzIyMTJmYTM4MzNjIiwidCI6IjMwN2E1MzQyLWU1ZjgtNDZiNS1hMTBlLTBmYzVhMGIzZTRjYSIsImMiOjl9"
        
        # 3. Create the Agent
        # We prepend the navigation command to your instruction
        final_task = f"Go to {power_bi_url}. Wait for the dashboard to fully load (wait 5 seconds). {request.instruction}"
        
        agent = Agent(
            task=final_task,
            llm=llm,
        )

        # 4. Execute
        # The agent will open a headless browser, click/read, and return the result
        result = await agent.run()
        
        return {
            "status": "success",
            "agent_result": result
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
