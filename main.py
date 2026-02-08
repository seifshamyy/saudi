import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from browser_use import Agent
# Use the official browser-use wrapper for Anthropic
from browser_use import ChatAnthropic
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class TaskRequest(BaseModel):
    instruction: str

@app.get("/")
def home():
    return {"status": "Power BI Agent is Awake"}

@app.post("/run")
async def run_agent(request: TaskRequest):
    try:
        # Initialize the model using the browser-use wrapper
        # Using the current Sonnet 4.5 model
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.0
        )

        power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiNGI5OWM4NzctMDExNS00ZTBhLWIxMmYtNzIyMTJmYTM4MzNjIiwidCI6IjMwN2E1MzQyLWU1ZjgtNDZiNS1hMTBlLTBmYzVhMGIzZTRjYSIsImMiOjl9"
        
        final_task = (
            f"Go to {power_bi_url}. Wait for the dashboard to fully load (wait 5 seconds). "
            f"{request.instruction} "
            "IMPORTANT: Once you have the answer, you must use the 'finish' tool to output it clearly."
        )
        
        agent = Agent(
            task=final_task,
            llm=llm,
        )

        history = await agent.run()
        
        # Robust result extraction with fallback
        result = history.final_result()
        if not result:
             if history.is_done():
                result = "Agent finished but returned no specific result. Check logs."
             elif history.has_errors():
                result = f"Agent encountered errors: {history.errors()}"
             elif history.steps:
                last_step = history.steps[-1]
                if last_step.model_output:
                    result = str(last_step.model_output)
                else:
                    result = "No result produced."
             else:
                result = "No result produced."
        
        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
