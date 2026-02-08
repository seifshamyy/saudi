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

from pydantic import ConfigDict, BaseModel

# Fix: Custom class to add the missing 'provider' attribute
class CustomChatAnthropic(ChatAnthropic):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def provider(self):
        return "anthropic"

    @property
    def model_name(self):
        return self.model

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
        # We also instruct it to be explicit with the final answer
        final_task = (
            f"Go to {power_bi_url}. Wait for the dashboard to fully load (wait 5 seconds). "
            f"{request.instruction} "
            "IMPORTANT: Once you have the answer, you must use the 'finish' tool to output it clearly."
        )
        
        agent = Agent(
            task=final_task,
            llm=llm,
        )

        # 4. Execute
        # The agent will open a headless browser, click/read, and return the result
        history = await agent.run()
        
        # 5. Extract the result
        # 'history' is a complex object, we want the final string
        result = history.final_result()
        
        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
