# ================================
# Business Analytics LangGraph - English Version
# ================================

import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"


from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import json

# Initialize LLM
try:
    llm = init_chat_model("openai:gpt-4o-mini")
except Exception:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini")

# State Definition
class BusinessState(TypedDict):
    # Inputs
    today_data: Dict[str, Any]
    yesterday_data: Dict[str, Any]
    
    # Calculations
    metrics: Dict[str, Any]
    
    # Final outputs
    profit_status: str
    alerts: List[str]
    recommendations: List[str]
    final_report: Dict[str, Any]

# Input Node
def input_node(state: BusinessState) -> BusinessState:
    """Receive and validate business data"""
    
    # Sample data - in practice this would come from API or database
    today_data = {
        "revenue": 12000,
        "cost": 8000,
        "customers": 150,
        "marketing_cost": 2000
    }
    
    yesterday_data = {
        "revenue": 10000,
        "cost": 7500,
        "customers": 120,
        "marketing_cost": 1800
    }
    
    return {
        **state,
        "today_data": today_data,
        "yesterday_data": yesterday_data
    }

# Processing Node
def processing_node(state: BusinessState) -> BusinessState:
    """Calculate key business metrics"""
    
    today = state["today_data"]
    yesterday = state["yesterday_data"]
    
    # Calculate metrics
    today_profit = today["revenue"] - today["cost"]
    yesterday_profit = yesterday["revenue"] - yesterday["cost"]
    
    # CAC (Customer Acquisition Cost)
    today_cac = today["marketing_cost"] / today["customers"] if today["customers"] > 0 else 0
    yesterday_cac = yesterday["marketing_cost"] / yesterday["customers"] if yesterday["customers"] > 0 else 0
    
    # Percentage changes
    revenue_change = ((today["revenue"] - yesterday["revenue"]) / yesterday["revenue"]) * 100
    cost_change = ((today["cost"] - yesterday["cost"]) / yesterday["cost"]) * 100
    profit_change = ((today_profit - yesterday_profit) / abs(yesterday_profit)) * 100 if yesterday_profit != 0 else 0
    cac_change = ((today_cac - yesterday_cac) / yesterday_cac) * 100 if yesterday_cac > 0 else 0
    customer_growth = ((today["customers"] - yesterday["customers"]) / yesterday["customers"]) * 100
    
    # ROI (Return on Investment)
    today_roi = (today_profit / today["cost"]) * 100 if today["cost"] > 0 else 0
    yesterday_roi = (yesterday_profit / yesterday["cost"]) * 100 if yesterday["cost"] > 0 else 0
    
    metrics = {
        "today_profit": today_profit,
        "yesterday_profit": yesterday_profit,
        "today_cac": round(today_cac, 2),
        "yesterday_cac": round(yesterday_cac, 2),
        "revenue_change": round(revenue_change, 2),
        "cost_change": round(cost_change, 2),
        "profit_change": round(profit_change, 2),
        "cac_change": round(cac_change, 2),
        "customer_growth": round(customer_growth, 2),
        "today_roi": round(today_roi, 2),
        "yesterday_roi": round(yesterday_roi, 2)
    }
    
    return {
        **state,
        "metrics": metrics,
        "profit_status": "positive" if today_profit > 0 else "negative"
    }

# Analysis Node
def analysis_node(state: BusinessState) -> BusinessState:
    """Generate alerts and intelligent analysis"""
    
    metrics = state["metrics"]
    alerts = []
    
    # Check profit status
    if metrics["today_profit"] <= 0:
        alerts.append("🚨 CRITICAL: You have losses today!")
    
    # Check CAC
    if metrics["cac_change"] > 20:
        alerts.append("⚠️ WARNING: Customer acquisition cost increased by more than 20%")
    elif metrics["today_cac"] > 50:
        alerts.append("⚠️ ALERT: Customer acquisition cost is higher than optimal")
    
    # Check cost changes
    if metrics["cost_change"] > metrics["revenue_change"] and metrics["revenue_change"] > 0:
        alerts.append("⚠️ CAUTION: Costs are growing faster than revenue")
    
    # Check negative revenue growth
    if metrics["revenue_change"] < -10:
        alerts.append("🚨 URGENT: Revenue decreased by more than 10%")
    
    # Check ROI
    if metrics["today_roi"] < 10:
        alerts.append("⚠️ LOW ROI: Return on investment is less than 10%")
    
    return {
        **state,
        "alerts": alerts
    }

# Recommendation Node
def recommendation_node(state: BusinessState) -> BusinessState:
    """Generate actionable recommendations using LLM"""
    
    metrics = state["metrics"]
    today = state["today_data"]
    yesterday = state["yesterday_data"]
    alerts = state["alerts"]
    
    # Create prompt for LLM
    analysis_prompt = f"""
    You are a business consultant. Based on the following data, provide actionable recommendations:

    📊 Today's Data:
    - Revenue: ${today['revenue']:,}
    - Cost: ${today['cost']:,}
    - Customers: {today['customers']}
    - Marketing Cost: ${today['marketing_cost']:,}
    - Profit: ${metrics['today_profit']:,}

    📊 Yesterday's Data:
    - Revenue: ${yesterday['revenue']:,}
    - Cost: ${yesterday['cost']:,}
    - Customers: {yesterday['customers']}
    - Profit: ${metrics['yesterday_profit']:,}

    📈 Changes:
    - Revenue Change: {metrics['revenue_change']}%
    - Cost Change: {metrics['cost_change']}%
    - Profit Change: {metrics['profit_change']}%
    - CAC Change: {metrics['cac_change']}%
    - Customer Growth: {metrics['customer_growth']}%

    🚨 Alerts: {alerts}

    Please provide 3-5 specific and actionable recommendations including:
    1. Immediate actions (if needed)
    2. Cost optimization
    3. Growth strategies
    4. Risk management

    Write the response as a clear and actionable list.
    """
    
    try:
        llm_response = llm.invoke([HumanMessage(content=analysis_prompt)])
        recommendations_text = llm_response.content
        
        # Convert LLM response to list
        recommendations = [
            line.strip() 
            for line in recommendations_text.split('\n') 
            if line.strip() and (line.strip().startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')) or '.' in line[:5])
        ]
        
        # If parsing failed, use the whole text as one item
        if len(recommendations) < 2:
            recommendations = [recommendations_text]
            
    except Exception as e:
        # Fallback recommendations in case of error
        recommendations = [
            "Error connecting to LLM - using baseline recommendations",
            "Review and control operational costs",
            "Analyze marketing channel performance",
            "Optimize product pricing strategy"
        ]
        
        # Add automatic recommendations based on metrics
        if metrics["today_profit"] <= 0:
            recommendations.append("🚨 URGENT: Reduce unnecessary expenses")
        
        if metrics["cac_change"] > 20:
            recommendations.append("📊 Review and optimize marketing campaigns")
        
        if metrics["revenue_change"] > 15:
            recommendations.append("📈 Increase marketing budget to leverage growth momentum")
    
    return {
        **state,
        "recommendations": recommendations
    }

# Output Node
def output_node(state: BusinessState) -> BusinessState:
    """Generate final JSON report"""
    
    final_report = {
        "business_summary": {
            "date": "today",
            "profit_loss_status": state["profit_status"],
            "total_profit": state["metrics"]["today_profit"],
            "revenue": state["today_data"]["revenue"],
            "cost": state["today_data"]["cost"],
            "customers": state["today_data"]["customers"]
        },
        "key_metrics": {
            "cac_today": state["metrics"]["today_cac"],
            "roi_today": state["metrics"]["today_roi"],
            "revenue_change": f"{state['metrics']['revenue_change']}%",
            "cost_change": f"{state['metrics']['cost_change']}%",
            "profit_change": f"{state['metrics']['profit_change']}%",
            "customer_growth": f"{state['metrics']['customer_growth']}%"
        },
        "alerts": state["alerts"],
        "recommendations": state["recommendations"],
        "action_priority": "high" if state["metrics"]["today_profit"] <= 0 else "medium" if len(state["alerts"]) > 0 else "low"
    }
    
    return {
        **state,
        "final_report": final_report
    }

# Create Graph
def create_business_graph():
    """Create business analytics graph"""
    
    workflow = StateGraph(BusinessState)
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("processing", processing_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("recommendations", recommendation_node)
    workflow.add_node("output", output_node)
    
    # Define graph flow
    workflow.set_entry_point("input")
    workflow.add_edge("input", "processing")
    workflow.add_edge("processing", "analysis")
    workflow.add_edge("analysis", "recommendations")
    workflow.add_edge("recommendations", "output")
    workflow.add_edge("output", END)
    
    return workflow.compile()

# Test and run graph
def run_business_analysis():
    """Run complete business analysis"""
    
    # Create graph
    graph = create_business_graph()
    
    # Run graph
    initial_state = {
        "today_data": {},
        "yesterday_data": {},
        "metrics": {},
        "profit_status": "",
        "alerts": [],
        "recommendations": [],
        "final_report": {}
    }
    
    result = graph.invoke(initial_state)
    
    return result

# Display results function
def display_results(result):
    """Display results in a beautiful format"""
    
    report = result["final_report"]
    
    print("=" * 60)
    print("📊 BUSINESS ANALYTICS REPORT")
    print("=" * 60)
    
    print(f"\n💰 Financial Status: {report['business_summary']['profit_loss_status']}")
    print(f"💵 Today's Profit: ${report['business_summary']['total_profit']:,}")
    print(f"📈 Today's Revenue: ${report['business_summary']['revenue']:,}")
    print(f"💸 Today's Cost: ${report['business_summary']['cost']:,}")
    print(f"👥 Customer Count: {report['business_summary']['customers']}")
    
    print(f"\n📊 Key Metrics:")
    for key, value in report['key_metrics'].items():
        print(f"   • {key}: {value}")
    
    if report['alerts']:
        print(f"\n🚨 Alerts:")
        for alert in report['alerts']:
            print(f"   • {alert}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n⚡ Action Priority: {report['action_priority']}")
    
    print("\n" + "=" * 60)
    print("📋 JSON Output:")
    print(json.dumps(report, indent=2))

# Export for LangGraph Studio
app = create_business_graph()

# Run test
if __name__ == "__main__":
    print("🚀 Starting business analysis...")
    result = run_business_analysis()
    display_results(result)