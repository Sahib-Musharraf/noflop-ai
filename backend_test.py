import requests
import sys
import json
from datetime import datetime

class NoFlopAPITester:
    def __init__(self, base_url="https://brutal-signal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_data": None,
                "error": None
            }

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    result["error"] = error_data
                    print(f"   Error: {error_data}")
                except:
                    result["error"] = response.text
                    print(f"   Error: {response.text}")

            self.test_results.append(result)
            return success, result["response_data"] if success else result["error"]

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": None,
                "success": False,
                "response_data": None,
                "error": str(e)
            }
            self.test_results.append(result)
            return False, str(e)

    def test_health_endpoint(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        if success and isinstance(response, dict) and response.get("status") == "ok":
            print("   ✅ Health endpoint returns correct format")
            return True
        else:
            print("   ❌ Health endpoint doesn't return expected {status: ok}")
            return False

    def test_validate_endpoint_success(self):
        """Test validate endpoint with valid idea"""
        test_idea = "A mobile app that uses AI to help people find the perfect coffee shop based on their mood, location, and taste preferences. It would integrate with local coffee shops and provide personalized recommendations."
        
        success, response = self.run_test(
            "Validate Idea - Success",
            "POST",
            "api/validate",
            200,
            data={"idea": test_idea},
            timeout=60  # AI calls can take time
        )
        
        if success and isinstance(response, dict):
            # Check if all required fields are present (including NEW fields for iteration 2)
            required_fields = ["id", "idea", "signal", "signal_reason", "score", "score_reason", "brutal_truth", "user_questions", "differentiation_angles", "similar_failures", "pivot_suggestions", "created_at"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                print("   ✅ All required fields present in response (including new iteration 2 fields)")
                
                # Check brutal_truth structure
                brutal_truth = response.get("brutal_truth", {})
                truth_fields = ["market_demand", "timing_reality", "competition_problem"]
                missing_truth_fields = [field for field in truth_fields if field not in brutal_truth]
                
                if not missing_truth_fields:
                    print("   ✅ Brutal truth has all required fields")
                else:
                    print(f"   ❌ Missing brutal truth fields: {missing_truth_fields}")
                    return False
                
                # Check user_questions is a list with 3 items
                user_questions = response.get("user_questions", [])
                if isinstance(user_questions, list) and len(user_questions) == 3:
                    print("   ✅ User questions has 3 items")
                else:
                    print(f"   ❌ User questions should be list of 3 items, got: {len(user_questions) if isinstance(user_questions, list) else 'not a list'}")
                    return False
                
                # NEW: Check differentiation_angles is a list with 2-3 items
                diff_angles = response.get("differentiation_angles", [])
                if isinstance(diff_angles, list) and 2 <= len(diff_angles) <= 3:
                    print(f"   ✅ Differentiation angles has {len(diff_angles)} items")
                else:
                    print(f"   ❌ Differentiation angles should be list of 2-3 items, got: {len(diff_angles) if isinstance(diff_angles, list) else 'not a list'}")
                    return False
                
                # NEW: Check similar_failures is a list with 1-3 items, each with name and reason
                similar_failures = response.get("similar_failures", [])
                if isinstance(similar_failures, list) and 1 <= len(similar_failures) <= 3:
                    print(f"   ✅ Similar failures has {len(similar_failures)} items")
                    for i, failure in enumerate(similar_failures):
                        if isinstance(failure, dict) and "name" in failure and "reason" in failure:
                            print(f"   ✅ Failure {i+1} has name and reason fields")
                        else:
                            print(f"   ❌ Failure {i+1} missing name or reason fields")
                            return False
                else:
                    print(f"   ❌ Similar failures should be list of 1-3 items, got: {len(similar_failures) if isinstance(similar_failures, list) else 'not a list'}")
                    return False
                
                # NEW: Check pivot_suggestions is a list with 2-3 items, each with idea and why
                pivot_suggestions = response.get("pivot_suggestions", [])
                if isinstance(pivot_suggestions, list) and 2 <= len(pivot_suggestions) <= 3:
                    print(f"   ✅ Pivot suggestions has {len(pivot_suggestions)} items")
                    for i, pivot in enumerate(pivot_suggestions):
                        if isinstance(pivot, dict) and "idea" in pivot and "why" in pivot:
                            print(f"   ✅ Pivot {i+1} has idea and why fields")
                        else:
                            print(f"   ❌ Pivot {i+1} missing idea or why fields")
                            return False
                else:
                    print(f"   ❌ Pivot suggestions should be list of 2-3 items, got: {len(pivot_suggestions) if isinstance(pivot_suggestions, list) else 'not a list'}")
                    return False
                
                # Check signal is one of the expected values
                signal = response.get("signal", "")
                if signal in ["BUILD IT", "KILL IT", "PIVOT IT"]:
                    print(f"   ✅ Signal is valid: {signal}")
                else:
                    print(f"   ❌ Signal should be BUILD IT/KILL IT/PIVOT IT, got: {signal}")
                    return False
                
                # Check score is between 1-10
                score = response.get("score", 0)
                if isinstance(score, int) and 1 <= score <= 10:
                    print(f"   ✅ Score is valid: {score}/10")
                else:
                    print(f"   ❌ Score should be 1-10, got: {score}")
                    return False
                
                # Store the result ID for later testing
                self.test_result_id = response.get("id")
                return True
            else:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
        else:
            print("   ❌ Response is not a valid JSON object")
            return False

    def test_validate_endpoint_short_idea(self):
        """Test validate endpoint with too short idea"""
        success, response = self.run_test(
            "Validate Idea - Too Short",
            "POST",
            "api/validate",
            400,
            data={"idea": "Short"}
        )
        
        if success and isinstance(response, dict) and "detail" in response:
            print("   ✅ Correctly rejects short ideas with error message")
            return True
        else:
            print("   ❌ Should return 400 with error detail for short ideas")
            return False

    def test_validate_endpoint_empty_idea(self):
        """Test validate endpoint with empty idea"""
        success, response = self.run_test(
            "Validate Idea - Empty",
            "POST",
            "api/validate",
            400,
            data={"idea": ""}
        )
        
        if success and isinstance(response, dict) and "detail" in response:
            print("   ✅ Correctly rejects empty ideas with error message")
            return True
        else:
            print("   ❌ Should return 400 with error detail for empty ideas")
            return False

    def test_get_result_endpoint(self):
        """Test get result endpoint"""
        if not hasattr(self, 'test_result_id') or not self.test_result_id:
            print("   ⚠️  Skipping - No result ID from previous test")
            return False
            
        success, response = self.run_test(
            "Get Result - Valid ID",
            "GET",
            f"api/result/{self.test_result_id}",
            200
        )
        
        if success and isinstance(response, dict):
            # Check if all required fields are present (including NEW fields for iteration 2)
            required_fields = ["id", "idea", "signal", "signal_reason", "score", "score_reason", "brutal_truth", "user_questions", "differentiation_angles", "similar_failures", "pivot_suggestions", "created_at"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                print("   ✅ Result retrieval returns all required fields (including new iteration 2 fields)")
                return True
            else:
                print(f"   ❌ Missing fields in result: {missing_fields}")
                return False
        else:
            print("   ❌ Result retrieval failed or returned invalid data")
            return False

    def test_get_result_invalid_id(self):
        """Test get result endpoint with invalid ID"""
        success, response = self.run_test(
            "Get Result - Invalid ID",
            "GET",
            "api/result/invalid-id-123",
            404
        )
        
        if success and isinstance(response, dict) and "detail" in response:
            print("   ✅ Correctly returns 404 for invalid result ID")
            return True
        else:
            print("   ❌ Should return 404 with error detail for invalid ID")
            return False

    def test_leaderboard_endpoint(self):
        """Test leaderboard endpoint - NEW for iteration 3"""
        success, response = self.run_test(
            "Leaderboard - Get Top Ideas",
            "GET",
            "api/leaderboard",
            200
        )
        
        if success and isinstance(response, dict):
            # Check if leaderboard key exists
            if "leaderboard" not in response:
                print("   ❌ Response missing 'leaderboard' key")
                return False
            
            leaderboard = response["leaderboard"]
            
            # Check if leaderboard is a list
            if not isinstance(leaderboard, list):
                print("   ❌ Leaderboard should be a list")
                return False
            
            # Check if leaderboard has entries (context says there are already 10 entries)
            if len(leaderboard) == 0:
                print("   ❌ Leaderboard is empty (expected existing entries)")
                return False
            
            print(f"   ✅ Leaderboard has {len(leaderboard)} entries")
            
            # Check structure of first entry
            first_entry = leaderboard[0]
            required_fields = ["rank", "id", "idea_preview", "signal", "score", "signal_reason"]
            missing_fields = [field for field in required_fields if field not in first_entry]
            
            if missing_fields:
                print(f"   ❌ Missing required fields in leaderboard entry: {missing_fields}")
                return False
            
            print("   ✅ Leaderboard entries have all required fields")
            
            # Check rank ordering (should start from 1)
            for i, entry in enumerate(leaderboard):
                expected_rank = i + 1
                if entry["rank"] != expected_rank:
                    print(f"   ❌ Rank ordering incorrect at position {i}: expected {expected_rank}, got {entry['rank']}")
                    return False
            
            print("   ✅ Rank ordering is correct")
            
            # Check score ordering (should be descending)
            for i in range(len(leaderboard) - 1):
                current_score = leaderboard[i]["score"]
                next_score = leaderboard[i + 1]["score"]
                if current_score < next_score:
                    print(f"   ❌ Score ordering incorrect: {current_score} < {next_score} at positions {i} and {i+1}")
                    return False
            
            print("   ✅ Score ordering is correct (descending)")
            
            # Check idea_preview is truncated (should be <= 80 chars + "...")
            for i, entry in enumerate(leaderboard):
                idea_preview = entry["idea_preview"]
                if len(idea_preview) > 83:  # 80 chars + "..." = 83
                    print(f"   ❌ Idea preview too long at position {i}: {len(idea_preview)} chars")
                    return False
            
            print("   ✅ Idea previews are properly truncated")
            
            # Check signal values are valid
            valid_signals = ["BUILD IT", "KILL IT", "PIVOT IT"]
            for i, entry in enumerate(leaderboard):
                if entry["signal"] not in valid_signals:
                    print(f"   ❌ Invalid signal at position {i}: {entry['signal']}")
                    return False
            
            print("   ✅ All signals are valid")
            
            # Check scores are in valid range (1-10)
            for i, entry in enumerate(leaderboard):
                score = entry["score"]
                if not isinstance(score, int) or score < 1 or score > 10:
                    print(f"   ❌ Invalid score at position {i}: {score}")
                    return False
            
            print("   ✅ All scores are in valid range (1-10)")
            
            return True
        else:
            print("   ❌ Leaderboard endpoint failed or returned invalid data")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting NoFlop.ai API Tests")
        print("=" * 50)
        
        # Test health endpoint
        health_success = self.test_health_endpoint()
        
        # Test validate endpoint - success case
        validate_success = self.test_validate_endpoint_success()
        
        # Test validate endpoint - error cases
        validate_short_success = self.test_validate_endpoint_short_idea()
        validate_empty_success = self.test_validate_endpoint_empty_idea()
        
        # Test get result endpoint
        get_result_success = self.test_get_result_endpoint()
        get_result_invalid_success = self.test_get_result_invalid_id()
        
        # NEW: Test leaderboard endpoint
        leaderboard_success = self.test_leaderboard_endpoint()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            
            # Print failed tests
            failed_tests = [result for result in self.test_results if not result["success"]]
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"   - {test['test_name']}: {test.get('error', 'Unknown error')}")
            
            return 1

def main():
    tester = NoFlopAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())