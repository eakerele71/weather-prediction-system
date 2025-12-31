"""
API Testing Script for Weather Application

This script tests the location validation and weather API endpoints.
"""

import requests
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"

def test_location(location: str) -> Dict[str, Any]:
    """Test a location with the weather API"""
    print(f"\n{'='*60}")
    print(f"Testing: '{location}'")
    print('='*60)
    
    try:
        # Test current weather endpoint
        response = requests.get(f"{BASE_URL}/api/v1/current/{location}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS - Location is valid!")
            print(f"Location: {data.get('location', {}).get('city')}, {data.get('location', {}).get('country')}")
            print(f"Temperature: {data.get('temperature')}°C")
            print(f"Weather: {data.get('weather_condition')}")
            print(f"Humidity: {data.get('humidity')}%")
            return {"success": True, "data": data}
        elif response.status_code == 404:
            error_detail = response.json().get('detail', 'Location not found')
            print(f"❌ FAILED - {error_detail}")
            return {"success": False, "error": error_detail}
        else:
            print(f"❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Cannot connect to API. Is the backend running?")
        return {"success": False, "error": "Connection failed"}
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """Run API tests"""
    print("\n" + "="*60)
    print("WEATHER API TESTING")
    print("="*60)
    
    # Test cases
    test_cases = [
        # Valid locations
        ("London", True),
        ("New York", True),
        ("Tokyo", True),
        ("Paris", True),
        
        # Invalid locations (should fail)
        ("rice and beans", False),
        ("pizza", False),
        ("12345", False),
        ("asdf", False),
        ("xyz123", False),
    ]
    
    results = {"passed": 0, "failed": 0}
    
    for location, should_succeed in test_cases:
        result = test_location(location)
        
        # Check if result matches expectation
        if should_succeed and result["success"]:
            results["passed"] += 1
        elif not should_succeed and not result["success"]:
            results["passed"] += 1
            print("✅ Correctly rejected invalid location")
        else:
            results["failed"] += 1
            print(f"⚠️ Unexpected result!")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    print(f"Passed: {results['passed']}/{len(test_cases)}")
    print(f"Failed: {results['failed']}/{len(test_cases)}")
    print('='*60)


if __name__ == "__main__":
    main()
