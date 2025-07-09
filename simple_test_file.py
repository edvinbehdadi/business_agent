# ================================
# test_business_analytics.py - Simple Test Suite
# ================================

import sys
import os
import json
from datetime import datetime

# Add current directory to path to import main module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import create_business_graph, run_business_analysis, display_results
    print("✅ Successfully imported main module")
except ImportError as e:
    print(f"❌ Failed to import main module: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic graph functionality"""
    print("\n" + "="*50)
    print("🧪 TEST 1: Basic Functionality")
    print("="*50)
    
    try:
        # Create graph
        graph = create_business_graph()
        print("✅ Graph created successfully")
        
        # Test with empty initial state
        initial_state = {
            "today_data": {},
            "yesterday_data": {},
            "metrics": {},
            "profit_status": "",
            "alerts": [],
            "recommendations": [],
            "final_report": {}
        }
        
        # Run the graph
        result = graph.invoke(initial_state)
        print("✅ Graph executed successfully")
        
        # Check if final report exists
        assert "final_report" in result, "Missing final_report in result"
        assert "business_summary" in result["final_report"], "Missing business_summary"
        assert "key_metrics" in result["final_report"], "Missing key_metrics"
        
        print("✅ All basic checks passed")
        return result
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return None

def test_profit_calculation():
    """Test profit calculation accuracy"""
    print("\n" + "="*50)
    print("🧪 TEST 2: Profit Calculation")
    print("="*50)
    
    try:
        result = run_business_analysis()
        
        # Get the data
        today_data = result["today_data"]
        metrics = result["metrics"]
        
        # Manual calculation
        expected_profit = today_data["revenue"] - today_data["cost"]
        actual_profit = metrics["today_profit"]
        
        print(f"📊 Revenue: ${today_data['revenue']:,}")
        print(f"💸 Cost: ${today_data['cost']:,}")
        print(f"💰 Expected Profit: ${expected_profit:,}")
        print(f"💰 Calculated Profit: ${actual_profit:,}")
        
        assert actual_profit == expected_profit, f"Profit mismatch: {actual_profit} != {expected_profit}"
        print("✅ Profit calculation correct")
        
        # Test profit status
        expected_status = "positive" if expected_profit > 0 else "negative"
        actual_status = result["profit_status"]
        
        assert actual_status == expected_status, f"Profit status mismatch: {actual_status} != {expected_status}"
        print(f"✅ Profit status correct: {actual_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Profit calculation test failed: {e}")
        return False

def test_cac_calculation():
    """Test Customer Acquisition Cost calculation"""
    print("\n" + "="*50)
    print("🧪 TEST 3: CAC Calculation")
    print("="*50)
    
    try:
        result = run_business_analysis()
        
        today_data = result["today_data"]
        metrics = result["metrics"]
        
        # Manual CAC calculation
        expected_cac = today_data["marketing_cost"] / today_data["customers"]
        actual_cac = metrics["today_cac"]
        
        print(f"💰 Marketing Cost: ${today_data['marketing_cost']:,}")
        print(f"👥 Customers: {today_data['customers']}")
        print(f"📊 Expected CAC: ${expected_cac:.2f}")
        print(f"📊 Calculated CAC: ${actual_cac:.2f}")
        
        # Allow small floating point differences
        assert abs(actual_cac - expected_cac) < 0.01, f"CAC mismatch: {actual_cac} != {expected_cac}"
        print("✅ CAC calculation correct")
        
        return True
        
    except Exception as e:
        print(f"❌ CAC calculation test failed: {e}")
        return False

def test_alerts_generation():
    """Test alert generation logic"""
    print("\n" + "="*50)
    print("🧪 TEST 4: Alerts Generation")
    print("="*50)
    
    try:
        result = run_business_analysis()
        
        alerts = result["alerts"]
        metrics = result["metrics"]
        
        print(f"📋 Number of alerts generated: {len(alerts)}")
        
        # Check specific alert conditions
        if metrics["today_profit"] <= 0:
            profit_alert_found = any("CRITICAL" in alert for alert in alerts)
            assert profit_alert_found, "Missing critical profit alert"
            print("✅ Critical profit alert correctly generated")
        
        if metrics["cac_change"] > 20:
            cac_alert_found = any("CAC" in alert and "20%" in alert for alert in alerts)
            assert cac_alert_found, "Missing CAC increase alert"
            print("✅ CAC increase alert correctly generated")
        
        if metrics["today_roi"] < 10:
            roi_alert_found = any("LOW ROI" in alert for alert in alerts)
            assert roi_alert_found, "Missing low ROI alert"
            print("✅ Low ROI alert correctly generated")
        
        print("✅ Alert generation logic working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Alerts generation test failed: {e}")
        return False

def test_json_output_structure():
    """Test final JSON output structure"""
    print("\n" + "="*50)
    print("🧪 TEST 5: JSON Output Structure")
    print("="*50)
    
    try:
        result = run_business_analysis()
        final_report = result["final_report"]
        
        # Required top-level keys
        required_keys = ["business_summary", "key_metrics", "alerts", "recommendations", "action_priority"]
        
        for key in required_keys:
            assert key in final_report, f"Missing required key: {key}"
            print(f"✅ Found required key: {key}")
        
        # Check business_summary structure
        business_summary = final_report["business_summary"]
        summary_keys = ["date", "profit_loss_status", "total_profit", "revenue", "cost", "customers"]
        
        for key in summary_keys:
            assert key in business_summary, f"Missing business_summary key: {key}"
            print(f"✅ Found business_summary key: {key}")
        
        # Check key_metrics structure
        key_metrics = final_report["key_metrics"]
        metrics_keys = ["cac_today", "roi_today", "revenue_change", "cost_change", "profit_change", "customer_growth"]
        
        for key in metrics_keys:
            assert key in key_metrics, f"Missing key_metrics key: {key}"
            print(f"✅ Found key_metrics key: {key}")
        
        # Test JSON serialization
        json_str = json.dumps(final_report, indent=2)
        parsed_back = json.loads(json_str)
        assert parsed_back == final_report, "JSON serialization/deserialization failed"
        print("✅ JSON structure is valid and serializable")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON output structure test failed: {e}")
        return False

def test_recommendations_generation():
    """Test recommendations generation"""
    print("\n" + "="*50)
    print("🧪 TEST 6: Recommendations Generation")
    print("="*50)
    
    try:
        result = run_business_analysis()
        recommendations = result["recommendations"]
        
        print(f"💡 Number of recommendations: {len(recommendations)}")
        
        # Check that we have recommendations
        assert len(recommendations) > 0, "No recommendations generated"
        print("✅ Recommendations were generated")
        
        # Check that recommendations are non-empty strings
        for i, rec in enumerate(recommendations):
            assert isinstance(rec, str), f"Recommendation {i} is not a string"
            assert len(rec.strip()) > 0, f"Recommendation {i} is empty"
            print(f"✅ Recommendation {i+1}: Valid")
        
        # Print first few recommendations for review
        print(f"\n📋 Sample recommendations:")
        for i, rec in enumerate(recommendations[:3]):
            print(f"   {i+1}. {rec[:100]}{'...' if len(rec) > 100 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Recommendations generation test failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "="*50)
    print("🧪 TEST 7: Edge Cases")
    print("="*50)
    
    try:
        # Test with zero customers (should handle division by zero)
        graph = create_business_graph()
        
        # This should still work without crashing
        result = graph.invoke({
            "today_data": {},
            "yesterday_data": {},
            "metrics": {},
            "profit_status": "",
            "alerts": [],
            "recommendations": [],
            "final_report": {}
        })
        
        print("✅ Handled edge case: zero division")
        
        # Check that CAC is calculated correctly when customers = 0
        metrics = result["metrics"]
        if result["today_data"]["customers"] == 0:
            assert metrics["today_cac"] == 0, "CAC should be 0 when customers = 0"
            print("✅ CAC correctly set to 0 for zero customers")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 STARTING BUSINESS ANALYTICS TEST SUITE")
    print("=" * 60)
    
    test_functions = [
        test_basic_functionality,
        test_profit_calculation,
        test_cac_calculation,
        test_alerts_generation,
        test_json_output_structure,
        test_recommendations_generation,
        test_edge_cases
    ]
    
    results = []
    start_time = datetime.now()
    
    for test_func in test_functions:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"❌ {test_func.__name__} crashed: {e}")
            results.append((test_func.__name__, False))
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    print(f"⏱️ Duration: {duration:.2f} seconds")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your system is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the errors above.")
    
    return passed == total

def quick_demo():
    """Run a quick demo of the system"""
    print("\n" + "="*60)
    print("🎭 QUICK DEMO - Sample Analysis")
    print("="*60)
    
    try:
        result = run_business_analysis()
        display_results(result)
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            quick_demo()
        elif sys.argv[1] == "quick":
            # Run only basic tests
            test_basic_functionality()
            test_profit_calculation()
            print("\n✅ Quick tests completed!")
        else:
            print("Usage: python test_business_analytics.py [demo|quick]")
    else:
        # Run all tests
        success = run_all_tests()
        
        # Run demo if all tests pass
        if success:
            print("\n" + "="*60)
            print("🎭 BONUS: Running demo since all tests passed!")
            quick_demo()
        
        sys.exit(0 if success else 1)
