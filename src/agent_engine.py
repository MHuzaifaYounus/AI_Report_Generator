import os
import asyncio
import json
from openai import AsyncOpenAI  # <--- Correct import source
from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure the Gemini-compatible Client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Configure the Model Adapter
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash-lite",
    openai_client=external_client,
)

run_config = RunConfig(
    model=model,
)

# 2. DEFINE DYNAMIC INSTRUCTIONS
# FIX: The 'context' argument is a RunContextWrapper. 
# We must access 'context.context' to get the dictionary we passed in Runner.run().

def trends_instructions(context, trend_agent):
    # <--- ACCESS THE INNER DICTIONARY HERE
    stats = context.context.get("stats", "No data provided")
    
    return f"""
    You are a Data Trend Analyst.
    
    Here is the Statistical Summary of the dataset:
    {stats}
    
    YOUR MISSION:
    1. Identify the overall direction (Growth/Decline/Stable).
    2. Note the velocity of change (based on Min/Max delta).
    3. IGNORE individual outliers (focus on the aggregate).
    
    CONSTRAINTS:
    - Keep output under 50 words.
    - Use a professional, executive tone.
    - Do not use markdown headers (##), just plain text.
    """

def anomalies_instructions(context, anomaly_agent):
    # <--- ACCESS THE INNER DICTIONARY HERE
    stats = context.context.get("stats", "No data provided")
    
    return f"""
    You are a Forensic Security Auditor.
    
    Here is the Statistical Summary of the dataset:
    {stats}
    
    YOUR MISSION:
    1. Focus ONLY on the 'anomaly_detection' fields (Z-scores, Outliers).
    2. Explain WHY these specific points are unusual.
    3. IGNORE the general trend.
    
    CONSTRAINTS:
    - Keep output under 50 words.
    - Use an urgent, warning tone.
    """

def actions_instructions(context, action_agent):
    # <--- ACCESS THE INNER DICTIONARY HERE
    stats = context.context.get("stats", "No data provided")
    
    return f"""
    You are a C-Level Strategy Consultant.
    
    Here is the Statistical Summary of the dataset:
    {stats}
    
    YOUR MISSION:
    1. Suggest 3 concrete, realistic business actions based on these stats.
    2. Prioritize actions that address the lowest performing areas or highest risks.
    
    CONSTRAINTS:
    - Use a concise bullet-point format.
    - Be direct and authoritative.
    """

# 3. INSTANTIATE AGENTS
trend_agent = Agent(
    name="Trend Analyst",
    instructions=trends_instructions
)

anomaly_agent = Agent(
    name="Anomaly Hunter",
    instructions=anomalies_instructions
)

action_agent = Agent(
    name="Strategist",
    instructions=actions_instructions
)

# 4. ASYNC EXECUTION WRAPPER
async def run_agent_process(agent, context_data):
    """
    Handles the async nature of the Agents SDK Runner.
    """
    # We pass 'context_data' here. 
    # It becomes 'context.context' inside the instruction functions.
    result = await Runner.run(
        starting_agent=agent,
        input="Analyze the provided statistics and generate the report.",
        context=context_data,
        run_config=run_config
    )
    
    return result.final_output

# 5. MAIN ENTRY POINT (Called by App.py)
# Replace your existing get_ai_insight function with this Optimized Version

def get_ai_insight(stats_dict: dict, insight_type: str) -> str:
    """
    Synchronous wrapper that routes the request and runs the async agent.
    """
    
    # --- OPTIMIZATION: PRUNE DATA (The Diet) ---
    # We create a lightweight copy to send to the LLM.
    # We remove 'data_types_distribution' which is useless text that costs tokens.
    clean_stats = stats_dict.copy()
    if "overall_summary" in clean_stats:
        # Remove verbose metadata that the AI doesn't strictly need
        clean_stats["overall_summary"].pop("data_types_distribution", None)
    
    # For 'Trends', we don't need the detailed outlier examples (save tokens)
    if insight_type == "Trends" and "numeric_columns" in clean_stats:
        for col in clean_stats["numeric_columns"]:
            clean_stats["numeric_columns"][col].pop("anomaly_detection_zscore_outliers_examples", None)

    # 1. Route to the correct Agent
    if insight_type == "Trends":
        selected_agent = trend_agent
    elif insight_type == "Anomalies":
        selected_agent = anomaly_agent
    elif insight_type == "Actions":
        selected_agent = action_agent
    else:
        return "Error: Invalid Insight Type Requested"

    # 2. Prepare Context 
    # Now we dump the 'clean_stats' instead of the full dict
    context_data = {"stats": json.dumps(clean_stats, indent=2)}
    
    # 3. Run Async Loop
    try:
        return asyncio.run(run_agent_process(selected_agent, context_data))
    except Exception as e:
        return f"Agent Engine Error: {str(e)}"