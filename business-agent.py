# ================================
# Business Analytics Chat System - Fixed Version
# ================================

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Validate that API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY not found in environment variables!")
    print("Please create a .env file with your OpenAI API key:")
    print("OPENAI_API_KEY=your_openai_api_key_here")
    exit(1)

from typing import Annotated, List, Dict, Any, Union
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import json
from datetime import datetime, timedelta
import random

# Initialize the chat model
try:
    llm = init_chat_model("openai:gpt-4o-mini")
    print("✅ LLM initialized successfully")
except Exception as e:
    print(f"❌ Error initializing LLM: {e}")
    print("Please check your OpenAI API key and internet connection")
    exit(1)

# Sample business data (simulating a database)
BUSINESS_DATA = {
    "2024-01-01": {"revenue": 8000, "cost": 5000, "customers": 80},
    "2024-01-02": {"revenue": 10000, "cost": 6000, "customers": 100},
    "2024-01-03": {"revenue": 7500, "cost": 4800, "customers": 75},
    "2024-01-04": {"revenue": 11000, "cost": 7000, "customers": 110},
    "2024-01-05": {"revenue": 9500, "cost": 6200, "customers": 95},
    "2024-01-06": {"revenue": 5000, "cost": 7000, "customers": 50},
    "2024-01-07": {"revenue": 12000, "cost": 7500, "customers": 120},
    "2024-01-08": {"revenue": 9000, "cost": 5800, "customers": 90},
    "2024-01-09": {"revenue": 8500, "cost": 5500, "customers": 85},
    "2024-01-10": {"revenue": 10500, "cost": 6500, "customers": 105},
}

# Define the state structure
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str
    stage: str  # "greeting", "date_selection", "confirm_analysis", "analysis", "complete"
    selected_date: str
    analysis_result: Dict[str, Any]

# Display the data table
def get_data_table():
    response = """📊 **Available Business Data:**
```
Date        | Revenue ($) | Cost ($) | Customers
------------|------------|----------|----------"""
    
    for date, data in sorted(BUSINESS_DATA.items()):
        response += f"\n{date} | ${data['revenue']:,}      | ${data['cost']:,}    | {data['customers']}"
    
    response += "\n```"
    return response

# Process user input and determine next action
def process_input(state: State) -> Dict:
    """
    Process user input and determine what to do next
    """
    user_input = state.get("user_input", "").strip()
    stage = state.get("stage", "greeting")
    
    if stage == "greeting":
        response = f"""Hello! I'm your Business Analytics Assistant. 🤖
        
To analyze your sales and cost data, please select a date from the available data.

{get_data_table()}

💡 Please enter the date you'd like to analyze in YYYY-MM-DD format (e.g., 2024-01-05)"""
        
        return {
            "messages": [AIMessage(content=response)],
            "stage": "date_selection"
        }
    
    elif stage == "date_selection":
        if user_input in BUSINESS_DATA:
            # Check if previous day exists
            date_obj = datetime.strptime(user_input, "%Y-%m-%d")
            prev_date = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d")
            
            if prev_date not in BUSINESS_DATA:
                return {
                    "messages": [AIMessage(content="⚠️ Sorry, no data available for the previous day. Please select a date that has previous day data for comparison.")],
                    "stage": "date_selection"
                }
            
            return {
                "messages": [AIMessage(content=f"✅ Date {user_input} selected.\n\nDo you want me to analyze the business data for this date? (yes/no)")],
                "selected_date": user_input,
                "stage": "confirm_analysis"
            }
        else:
            return {
                "messages": [AIMessage(content="❌ The entered date is not in the available data. Please select one of the dates from the table.")],
                "stage": "date_selection"
            }
    
    elif stage == "confirm_analysis":
        if user_input.lower() in ["yes", "y", "yeah", "sure"]:
            return {
                "messages": [AIMessage(content="🔍 Starting business data analysis...")],
                "stage": "analysis"
            }
        elif user_input.lower() in ["no", "n", "nope"]:
            response = f"""{get_data_table()}

💡 Please enter a new date you'd like to analyze:"""
            return {
                "messages": [AIMessage(content=response)],
                "stage": "date_selection",
                "selected_date": ""
            }
        else:
            return {
                "messages": [AIMessage(content="Please answer with 'yes' or 'no'. Do you want me to analyze the business data?")],
                "stage": "confirm_analysis"
            }
    
    elif stage == "complete":
        if user_input.lower() in ["yes", "y", "yeah", "sure"]:
            response = f"""{get_data_table()}

💡 Please enter the new date you'd like to analyze:"""
            return {
                "messages": [AIMessage(content=response)],
                "stage": "date_selection",
                "selected_date": ""
            }
        elif user_input.lower() in ["no", "n", "nope"]:
            return {
                "messages": [AIMessage(content="Thank you for using Business Analytics Chat! 👋")],
                "stage": "end"
            }
        else:
            return {
                "messages": [AIMessage(content="Please answer with 'yes' or 'no'. Would you like to analyze another date?")],
                "stage": "complete"
            }
    
    return state

# Perform business analysis using LLM
def analyze_business(state: State) -> Dict:
    """
    Perform the business analysis using LLM
    """
    if state.get("stage") != "analysis":
        return state
    
    selected_date = state["selected_date"]
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    prev_date = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d")
    
    current = BUSINESS_DATA[selected_date]
    previous = BUSINESS_DATA[prev_date]
    
    # Prepare data for LLM analysis
    analysis_prompt = f"""
    You are a business analyst. Analyze the following business data and provide insights:

    Selected Date: {selected_date}
    Current Day Data:
    - Revenue: ${current['revenue']:,}
    - Cost: ${current['cost']:,}
    - Customers: {current['customers']}

    Previous Day Data ({prev_date}):
    - Revenue: ${previous['revenue']:,}
    - Cost: ${previous['cost']:,}
    - Customers: {previous['customers']}

    Please provide:
    1. A comprehensive business analysis comparing the two days
    2. Calculate key metrics (profit/loss, changes in percentages, customer acquisition cost)
    3. Identify any alerts or warnings based on the data
    4. Provide actionable recommendations
    5. Give an overall assessment of business performance

    Format your response with clear sections and use emojis for better readability.
    Also, at the end, provide a JSON summary with key metrics and recommendations.
    """
    
    try:
        print("🤖 Generating analysis with AI...")
        # Generate analysis using LLM
        analysis_response = llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Generate JSON output using LLM
        json_prompt = f"""
        Based on the business data analysis for {selected_date}, create a structured JSON output with the following format:
        
        Current Day: Revenue ${current['revenue']:,}, Cost ${current['cost']:,}, Customers {current['customers']}
        Previous Day: Revenue ${previous['revenue']:,}, Cost ${previous['cost']:,}, Customers {previous['customers']}
        
        Create a JSON with these keys:
        - profit_loss_status: "positive" or "negative"
        - current_profit: calculated profit value
        - alerts: array of alert messages
        - recommendations: array of actionable recommendations
        - key_metrics: object with percentage changes and important metrics
        
        Return only valid JSON without any explanation.
        """
        
        json_response = llm.invoke([HumanMessage(content=json_prompt)])
        
        # Parse JSON response
        try:
            json_output = json.loads(json_response.content)
        except json.JSONDecodeError:
            print("⚠️ Warning: Could not parse LLM JSON response, using fallback")
            # Fallback JSON if parsing fails
            current_profit = current["revenue"] - current["cost"]
            json_output = {
                "profit_loss_status": "positive" if current_profit > 0 else "negative",
                "current_profit": current_profit,
                "alerts": ["Unable to parse LLM JSON response"],
                "recommendations": ["Review analysis manually"],
                "key_metrics": {"error": "JSON parsing failed"}
            }
        
    except Exception as e:
        print(f"⚠️ Warning: LLM error ({e}), using fallback analysis")
        
        # Fallback analysis if LLM fails
        current_profit = current["revenue"] - current["cost"]
        revenue_change = ((current["revenue"] - previous["revenue"]) / previous["revenue"]) * 100
        cost_change = ((current["cost"] - previous["cost"]) / previous["cost"]) * 100
        
        analysis_response = type('obj', (object,), {
            'content': f"""📊 **Business Analysis for {selected_date}** (Fallback Mode)
            
💰 **Financial Summary:**
- Current Profit: ${current_profit:,}
- Revenue Change: {revenue_change:.1f}%
- Cost Change: {cost_change:.1f}%

📈 **Key Insights:**
- {"Profitable day" if current_profit > 0 else "Loss incurred"}
- Revenue {"increased" if revenue_change > 0 else "decreased"} compared to previous day
- Cost efficiency needs attention if costs grew faster than revenue

⚠️ **Note:** This is a basic analysis due to LLM connectivity issues."""
        })()
        
        json_output = {
            "profit_loss_status": "positive" if current_profit > 0 else "negative",
            "current_profit": current_profit,
            "alerts": ["LLM unavailable - basic analysis provided"],
            "recommendations": ["Review detailed financials", "Check operational efficiency"],
            "key_metrics": {
                "revenue_change": f"{revenue_change:.1f}%",
                "cost_change": f"{cost_change:.1f}%",
                "profit": current_profit
            }
        }
    
    # Combine LLM analysis with JSON output
    final_response = f"{analysis_response.content}\n\n📋 **JSON Output:**\n```json\n{json.dumps(json_output, indent=2)}\n```\n\nWould you like to analyze another date? (yes/no)"
    
    return {
        "messages": [AIMessage(content=final_response)],
        "stage": "complete",
        "analysis_result": json_output
    }

# Generate greeting using LLM
def generate_greeting(state: State) -> Dict:
    """
    Generate a dynamic greeting using LLM
    """
    greeting_prompt = f"""
    You are a friendly business analytics assistant. Generate a welcoming greeting message that:
    1. Introduces yourself as a business analytics assistant
    2. Explains that you can analyze business data
    3. Shows the available data table
    4. Asks the user to select a date for analysis
    
    Available data dates: {list(BUSINESS_DATA.keys())}
    
    Make it engaging and professional with appropriate emojis.
    Include this data table in your response:
    {get_data_table()}
    
    End with asking the user to enter a date in YYYY-MM-DD format.
    """
    
    try:
        greeting_response = llm.invoke([HumanMessage(content=greeting_prompt)])
        return {
            "messages": [AIMessage(content=greeting_response.content)],
            "stage": "date_selection"
        }
    except Exception as e:
        print(f"⚠️ Warning: LLM error for greeting ({e}), using fallback")
        # Fallback greeting
        fallback_greeting = f"""Hello! I'm your Business Analytics Assistant. 🤖
        
To analyze your sales and cost data, please select a date from the available data.

{get_data_table()}

💡 Please enter the date you'd like to analyze in YYYY-MM-DD format (e.g., 2024-01-05)"""
        
        return {
            "messages": [AIMessage(content=fallback_greeting)],
            "stage": "date_selection"
        }

# Enhanced process_input function
def process_input_enhanced(state: State) -> Dict:
    """
    Enhanced process input that uses LLM for dynamic responses
    """
    user_input = state.get("user_input", "").strip()
    stage = state.get("stage", "greeting")
    
    if stage == "greeting":
        return generate_greeting(state)
    
    elif stage == "date_selection":
        if user_input in BUSINESS_DATA:
            # Check if previous day exists
            date_obj = datetime.strptime(user_input, "%Y-%m-%d")
            prev_date = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d")
            
            if prev_date not in BUSINESS_DATA:
                try:
                    # Use LLM to generate error message
                    error_prompt = f"""
                    User selected date {user_input} but there's no data for the previous day ({prev_date}).
                    Generate a helpful error message asking them to select a date that has previous day data.
                    Be friendly and guide them to make a better selection.
                    """
                    error_response = llm.invoke([HumanMessage(content=error_prompt)])
                    
                    return {
                        "messages": [AIMessage(content=error_response.content)],
                        "stage": "date_selection"
                    }
                except Exception:
                    # Fallback error message
                    return {
                        "messages": [AIMessage(content="⚠️ Sorry, no data available for the previous day. Please select a date that has previous day data for comparison.")],
                        "stage": "date_selection"
                    }
            
            try:
                # Use LLM to generate confirmation message
                confirm_prompt = f"""
                User selected date {user_input} for analysis. 
                Generate a confirmation message that:
                1. Confirms the date selection
                2. Asks if they want to proceed with the analysis
                3. Be encouraging and professional
                """
                confirm_response = llm.invoke([HumanMessage(content=confirm_prompt)])
                
                return {
                    "messages": [AIMessage(content=confirm_response.content)],
                    "selected_date": user_input,
                    "stage": "confirm_analysis"
                }
            except Exception:
                # Fallback confirmation
                return {
                    "messages": [AIMessage(content=f"✅ Date {user_input} selected.\n\nDo you want me to analyze the business data for this date? (yes/no)")],
                    "selected_date": user_input,
                    "stage": "confirm_analysis"
                }
        else:
            try:
                # Use LLM to generate invalid date message
                invalid_prompt = f"""
                User entered invalid date: {user_input}
                Available dates: {list(BUSINESS_DATA.keys())}
                Generate a helpful error message asking them to select a valid date from the table.
                """
                invalid_response = llm.invoke([HumanMessage(content=invalid_prompt)])
                
                return {
                    "messages": [AIMessage(content=invalid_response.content)],
                    "stage": "date_selection"
                }
            except Exception:
                # Fallback invalid date message
                return {
                    "messages": [AIMessage(content="❌ The entered date is not in the available data. Please select one of the dates from the table.")],
                    "stage": "date_selection"
                }
    
    elif stage == "confirm_analysis":
        if user_input.lower() in ["yes", "y", "yeah", "sure"]:
            try:
                # Use LLM to generate analysis start message
                start_prompt = "Generate an engaging message that indicates the business analysis is starting. Use emojis and be encouraging."
                start_response = llm.invoke([HumanMessage(content=start_prompt)])
                
                return {
                    "messages": [AIMessage(content=start_response.content)],
                    "stage": "analysis"
                }
            except Exception:
                # Fallback start message
                return {
                    "messages": [AIMessage(content="🔍 Starting business data analysis...")],
                    "stage": "analysis"
                }
        elif user_input.lower() in ["no", "n", "nope"]:
            try:
                # Use LLM to generate back to selection message
                back_prompt = f"""
                User declined analysis. Generate a message that:
                1. Acknowledges their choice
                2. Shows the data table again
                3. Asks them to select a new date
                
                Include this table: {get_data_table()}
                """
                back_response = llm.invoke([HumanMessage(content=back_prompt)])
                
                return {
                    "messages": [AIMessage(content=back_response.content)],
                    "stage": "date_selection",
                    "selected_date": ""
                }
            except Exception:
                # Fallback back message
                response = f"""{get_data_table()}

💡 Please enter a new date you'd like to analyze:"""
                return {
                    "messages": [AIMessage(content=response)],
                    "stage": "date_selection",
                    "selected_date": ""
                }
        else:
            try:
                # Use LLM to generate clarification message
                clarify_prompt = f"""
                User gave unclear response: {user_input}
                Generate a polite message asking them to clarify with yes or no.
                """
                clarify_response = llm.invoke([HumanMessage(content=clarify_prompt)])
                
                return {
                    "messages": [AIMessage(content=clarify_response.content)],
                    "stage": "confirm_analysis"
                }
            except Exception:
                # Fallback clarification
                return {
                    "messages": [AIMessage(content="Please answer with 'yes' or 'no'. Do you want me to analyze the business data?")],
                    "stage": "confirm_analysis"
                }
    
    elif stage == "complete":
        if user_input.lower() in ["yes", "y", "yeah", "sure"]:
            try:
                # Use LLM to generate new analysis prompt
                new_prompt = f"""
                User wants to analyze another date. Generate a message that:
                1. Shows enthusiasm for another analysis
                2. Displays the data table
                3. Asks for new date selection
                
                Include this table: {get_data_table()}
                """
                new_response = llm.invoke([HumanMessage(content=new_prompt)])
                
                return {
                    "messages": [AIMessage(content=new_response.content)],
                    "stage": "date_selection",
                    "selected_date": ""
                }
            except Exception:
                # Fallback new analysis message
                response = f"""{get_data_table()}

💡 Please enter the new date you'd like to analyze:"""
                return {
                    "messages": [AIMessage(content=response)],
                    "stage": "date_selection",
                    "selected_date": ""
                }
        elif user_input.lower() in ["no", "n", "nope"]:
            try:
                # Use LLM to generate goodbye message
                goodbye_prompt = "Generate a warm, professional goodbye message for a business analytics session."
                goodbye_response = llm.invoke([HumanMessage(content=goodbye_prompt)])
                
                return {
                    "messages": [AIMessage(content=goodbye_response.content)],
                    "stage": "end"
                }
            except Exception:
                # Fallback goodbye
                return {
                    "messages": [AIMessage(content="Thank you for using Business Analytics Chat! 👋")],
                    "stage": "end"
                }
        else:
            try:
                # Use LLM to generate clarification message
                clarify_prompt = f"""
                User gave unclear response: {user_input}
                Generate a polite message asking them to clarify with yes or no for continuing with another analysis.
                """
                clarify_response = llm.invoke([HumanMessage(content=clarify_prompt)])
                
                return {
                    "messages": [AIMessage(content=clarify_response.content)],
                    "stage": "complete"
                }
            except Exception:
                # Fallback clarification
                return {
                    "messages": [AIMessage(content="Please answer with 'yes' or 'no'. Would you like to analyze another date?")],
                    "stage": "complete"
                }
    
    return state

# Create the graph
def create_business_chat_graph():
    """
    Create the business analytics chat graph
    """
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("process_input", process_input_enhanced)
    graph_builder.add_node("analyze", analyze_business)
    
    # Define routing
    def route_next(state: State):
        stage = state.get("stage", "")
        if stage == "analysis":
            return "analyze"
        elif stage == "end":
            return END
        else:
            return END
    
    # Add edges
    graph_builder.add_edge(START, "process_input")
    graph_builder.add_conditional_edges("process_input", route_next, {
        "analyze": "analyze",
        END: END
    })
    graph_builder.add_edge("analyze", END)
    
    return graph_builder.compile()

# Function to get analysis result as JSON
def get_analysis_json(state: State) -> Dict[str, Any]:
    """
    Get the analysis result as a JSON object
    """
    return state.get("analysis_result", {})

# Function to save analysis result to file
def save_analysis_to_file(state: State, filename: str = "analysis_result.json"):
    """
    Save the analysis result to a JSON file
    """
    result = get_analysis_json(state)
    if result:
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Analysis saved to {filename}")
    else:
        print("\n❌ No analysis result to save")

# Test function
def test_dynamic_flow():
    """
    Test function to demonstrate the dynamic LLM flow
    """
    print("=== Testing Dynamic LLM Business Analytics Flow ===\n")
    
    # Create graph
    graph = create_business_chat_graph()
    
    # Test steps
    test_steps = [
        {"input": "", "stage": "greeting", "description": "Dynamic greeting"},
        {"input": "2024-01-08", "stage": "date_selection", "description": "Select date"},
        {"input": "yes", "stage": "confirm_analysis", "description": "Confirm analysis"},
    ]
    
    state = State(
        messages=[],
        user_input="",
        stage="greeting",
        selected_date="",
        analysis_result={}
    )
    
    for step in test_steps:
        print(f"\n--- {step['description']} ---")
        state["user_input"] = step["input"]
        state["stage"] = step["stage"]
        
        result = graph.invoke(state)
        if result.get("messages") and len(result["messages"]) > len(state["messages"]):
            print(f"Assistant: {result['messages'][-1].content}")
        
        state.update(result)
        
        # If we reach analysis stage, run the analysis
        if state.get("stage") == "analysis":
            result = graph.invoke(state)
            if result.get("messages") and len(result["messages"]) > len(state["messages"]):
                print(f"Assistant: {result['messages'][-1].content}")
            state.update(result)
    
    return state

if __name__ == "__main__":
    import sys
    
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_dynamic_flow()
        sys.exit(0)
    
    print("🤖 Dynamic LLM Business Analytics Chat System")
    print("=" * 55)
    
    # Create the graph
    graph = create_business_chat_graph()
    
    # Initialize state
    state = State(
        messages=[],
        user_input="",
        stage="greeting",
        selected_date="",
        analysis_result={}
    )
    
    # Run initial greeting
    result = graph.invoke(state)
    if result["messages"]:
        print(f"\n{result['messages'][-1].content}")
    state.update(result)
    
    # Main interaction loop
    while state.get("stage") != "end":
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break
            
            # Check if user wants to save the last analysis
            if user_input.lower() == "save" and state.get("analysis_result"):
                save_analysis_to_file(state)
                continue
            
            # Update state with user input
            state["user_input"] = user_input
            
            # Run the graph
            result = graph.invoke(state)
            if result.get("messages") and len(result["messages"]) > len(state["messages"]):
                print(f"\n{result['messages'][-1].content}")
            
            # Update state
            state.update(result)
            
            # Check if we reached the end stage
            if state.get("stage") == "end":
                break
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()