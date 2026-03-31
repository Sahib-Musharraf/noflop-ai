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
        """Test validate endpoint with valid idea - Iteration 4 format"""
        test_idea = "A mobile app that uses AI to help people find the perfect coffee shop based on their mood, location, and taste preferences. It would integrate with local coffee shops and provide personalized recommendations."
        
        success, response = self.run_test(
            "Validate Idea - Success (Iteration 4)",
            "POST",
            "api/validate",
            200,
            data={"idea": test_idea},
            timeout=60  # AI calls can take time
        )
        
        if success and isinstance(response, dict):
            # Check if all required fields are present (NEW iteration 4 fields)
            required_fields = ["result_id", "idea", "verdict", "verdict_reason", "score", "breakdown", "strengths", "risks", "critical_insights", "actionable_suggestions", "user_questions", "differentiation_angles", "similar_failures", "pivot_suggestions", "created_at"]
            missing_fields = [field for field in required_fields if field not in response]
            
            # Also check backward compatibility fields
            backward_compat_fields = ["signal", "signal_reason"]
            missing_compat_fields = [field for field in backward_compat_fields if field not in response]
            
            if not missing_fields:
                print("   ✅ All required iteration 4 fields present in response")
                
                if not missing_compat_fields:
                    print("   ✅ Backward compatibility fields present")
                else:
                    print(f"   ❌ Missing backward compatibility fields: {missing_compat_fields}")
                    return False
                
                # Check verdict is one of the new values
                verdict = response.get("verdict", "")
                if verdict in ["Build", "Refine", "Avoid"]:
                    print(f"   ✅ Verdict is valid: {verdict}")
                else:
                    print(f"   ❌ Verdict should be Build/Refine/Avoid, got: {verdict}")
                    return False
                
                # Check signal mapping for backward compatibility
                signal = response.get("signal", "")
                expected_signal = "BUILD IT" if verdict == "Build" else ("KILL IT" if verdict == "Avoid" else "PIVOT IT")
                if signal == expected_signal:
                    print(f"   ✅ Signal correctly mapped from verdict: {signal}")
                else:
                    print(f"   ❌ Signal mapping incorrect: expected {expected_signal}, got {signal}")
                    return False
                
                # Check final_score is float with 1 decimal place (stored as "score")
                score = response.get("score", 0)
                if isinstance(score, (int, float)) and 0 <= score <= 10:
                    print(f"   ✅ Score is valid: {score}/10")
                else:
                    print(f"   ❌ Score should be 0-10, got: {score}")
                    return False
                
                # Check breakdown has 9 dimensions
                breakdown = response.get("breakdown", {})
                expected_dimensions = ["problem", "market", "icp", "behavior", "feasibility", "monetization", "advantage", "execution", "risk"]
                missing_dimensions = [dim for dim in expected_dimensions if dim not in breakdown]
                
                if not missing_dimensions:
                    print("   ✅ Breakdown has all 9 dimensions")
                    # Check each dimension is 0-10
                    for dim, score in breakdown.items():
                        if not isinstance(score, (int, float)) or score < 0 or score > 10:
                            print(f"   ❌ Dimension {dim} has invalid score: {score}")
                            return False
                    print("   ✅ All dimension scores are valid (0-10)")
                else:
                    print(f"   ❌ Missing breakdown dimensions: {missing_dimensions}")
                    return False
                
                # Check strengths is a list with items
                strengths = response.get("strengths", [])
                if isinstance(strengths, list) and len(strengths) >= 1:
                    print(f"   ✅ Strengths has {len(strengths)} items")
                else:
                    print(f"   ❌ Strengths should be non-empty list, got: {len(strengths) if isinstance(strengths, list) else 'not a list'}")
                    return False
                
                # Check risks is a list with items
                risks = response.get("risks", [])
                if isinstance(risks, list) and len(risks) >= 1:
                    print(f"   ✅ Risks has {len(risks)} items")
                else:
                    print(f"   ❌ Risks should be non-empty list, got: {len(risks) if isinstance(risks, list) else 'not a list'}")
                    return False
                
                # Check critical_insights is a list with items
                critical_insights = response.get("critical_insights", [])
                if isinstance(critical_insights, list) and len(critical_insights) >= 1:
                    print(f"   ✅ Critical insights has {len(critical_insights)} items")
                else:
                    print(f"   ❌ Critical insights should be non-empty list, got: {len(critical_insights) if isinstance(critical_insights, list) else 'not a list'}")
                    return False
                
                # Check actionable_suggestions is a list with items
                actionable_suggestions = response.get("actionable_suggestions", [])
                if isinstance(actionable_suggestions, list) and len(actionable_suggestions) >= 1:
                    print(f"   ✅ Actionable suggestions has {len(actionable_suggestions)} items")
                else:
                    print(f"   ❌ Actionable suggestions should be non-empty list, got: {len(actionable_suggestions) if isinstance(actionable_suggestions, list) else 'not a list'}")
                    return False
                
                # Check user_questions is a list with 3 items
                user_questions = response.get("user_questions", [])
                if isinstance(user_questions, list) and len(user_questions) == 3:
                    print("   ✅ User questions has 3 items")
                else:
                    print(f"   ❌ User questions should be list of 3 items, got: {len(user_questions) if isinstance(user_questions, list) else 'not a list'}")
                    return False
                
                # Check differentiation_angles is a list with items
                diff_angles = response.get("differentiation_angles", [])
                if isinstance(diff_angles, list) and len(diff_angles) >= 1:
                    print(f"   ✅ Differentiation angles has {len(diff_angles)} items")
                else:
                    print(f"   ❌ Differentiation angles should be non-empty list, got: {len(diff_angles) if isinstance(diff_angles, list) else 'not a list'}")
                    return False
                
                # Check similar_failures is a list with items, each with name and reason
                similar_failures = response.get("similar_failures", [])
                if isinstance(similar_failures, list) and len(similar_failures) >= 1:
                    print(f"   ✅ Similar failures has {len(similar_failures)} items")
                    for i, failure in enumerate(similar_failures):
                        if isinstance(failure, dict) and "name" in failure and "reason" in failure:
                            print(f"   ✅ Failure {i+1} has name and reason fields")
                        else:
                            print(f"   ❌ Failure {i+1} missing name or reason fields")
                            return False
                else:
                    print(f"   ❌ Similar failures should be non-empty list, got: {len(similar_failures) if isinstance(similar_failures, list) else 'not a list'}")
                    return False
                
                # Check pivot_suggestions is a list with items, each with idea and why
                pivot_suggestions = response.get("pivot_suggestions", [])
                if isinstance(pivot_suggestions, list) and len(pivot_suggestions) >= 1:
                    print(f"   ✅ Pivot suggestions has {len(pivot_suggestions)} items")
                    for i, pivot in enumerate(pivot_suggestions):
                        if isinstance(pivot, dict) and "idea" in pivot and "why" in pivot:
                            print(f"   ✅ Pivot {i+1} has idea and why fields")
                        else:
                            print(f"   ❌ Pivot {i+1} missing idea or why fields")
                            return False
                else:
                    print(f"   ❌ Pivot suggestions should be non-empty list, got: {len(pivot_suggestions) if isinstance(pivot_suggestions, list) else 'not a list'}")
                    return False
                
                # Store the result ID for later testing
                self.test_result_id = response.get("result_id")
                return True
            else:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
        else:
            print("   ❌ Response is not a valid JSON object")
            return False

    def test_validate_endpoint_structured_input(self):
        """Test validate endpoint with structured context fields - Iteration 4"""
        test_data = {
            "idea": "A mobile app that uses AI to help people find the perfect coffee shop based on their mood, location, and taste preferences.",
            "target_user": "Urban professionals aged 25-40 who drink coffee daily",
            "problem": "People waste time visiting coffee shops that don't match their current mood or taste preferences",
            "current_behavior": "They use Google Maps or Yelp to find nearby coffee shops without personalization",
            "trigger_moment": "When they want coffee but don't know which shop will have what they're craving",
            "frequency": "Daily",
            "pain_level": "Medium",
            "existing_alternatives": "Foursquare, Yelp, Google Maps",
            "monetization_idea": "Commission from coffee shops, premium subscription for advanced features",
            "willingness_to_pay": "Yes",
            "why_now": "AI personalization technology is mature, post-COVID people are more selective about where they go",
            "unfair_advantage": "Proprietary mood-to-coffee matching algorithm",
            "mvp_plan": "Simple app with mood selector and coffee shop recommendations in one city",
            "time_to_build": "2-4 weeks",
            "failure_risk": "Coffee shops may not want to pay commission, users may not trust AI recommendations"
        }
        
        success, response = self.run_test(
            "Validate Idea - Structured Input",
            "POST",
            "api/validate",
            200,
            data=test_data,
            timeout=60  # AI calls can take time
        )
        
        if success and isinstance(response, dict):
            # Check if context fields are stored
            context_fields = response.get("context_fields", {})
            if isinstance(context_fields, dict):
                print("   ✅ Context fields stored in response")
                
                # Check if some key context fields are preserved
                key_fields = ["target_user", "problem", "monetization_idea"]
                for field in key_fields:
                    if field in context_fields and context_fields[field] == test_data[field]:
                        print(f"   ✅ Context field '{field}' preserved correctly")
                    else:
                        print(f"   ❌ Context field '{field}' not preserved correctly")
                        return False
                
                # Check that structured input produces valid response
                if response.get("verdict") in ["Build", "Refine", "Avoid"]:
                    print("   ✅ Structured input produces valid verdict")
                    return True
                else:
                    print("   ❌ Structured input doesn't produce valid verdict")
                    return False
            else:
                print("   ❌ Context fields not stored properly")
                return False
        else:
            print("   ❌ Structured input test failed")
            return False
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
        """Test get result endpoint - Iteration 4"""
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
            # Check if all required fields are present (iteration 4 fields)
            required_fields = ["result_id", "idea", "verdict", "verdict_reason", "score", "breakdown", "strengths", "risks", "critical_insights", "actionable_suggestions", "user_questions", "differentiation_angles", "similar_failures", "pivot_suggestions", "created_at"]
            missing_fields = [field for field in required_fields if field not in response]
            
            # Also check backward compatibility fields
            backward_compat_fields = ["signal", "signal_reason"]
            missing_compat_fields = [field for field in backward_compat_fields if field not in response]
            
            if not missing_fields and not missing_compat_fields:
                print("   ✅ Result retrieval returns all required fields (iteration 4 + backward compatibility)")
                return True
            else:
                all_missing = missing_fields + missing_compat_fields
                print(f"   ❌ Missing fields in result: {all_missing}")
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
            required_fields = ["rank", "id", "idea_preview", "signal", "score", "signal_reason", "verdict"]
            missing_fields = [field for field in required_fields if field not in first_entry]
            
            if missing_fields:
                print(f"   ❌ Missing required fields in leaderboard entry: {missing_fields}")
                return False
            
            print("   ✅ Leaderboard entries have all required fields (including verdict)")
            
            # Check verdict values are valid (new for iteration 4)
            valid_verdicts = ["Build", "Refine", "Avoid"]
            for i, entry in enumerate(leaderboard):
                if "verdict" in entry and entry["verdict"] not in valid_verdicts:
                    print(f"   ❌ Invalid verdict at position {i}: {entry['verdict']}")
                    return False
            
            print("   ✅ All verdicts are valid (Build/Refine/Avoid)")
            
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

    def test_challenge_verdict_endpoint(self):
        """Test challenge verdict endpoint - NEW for iteration 5"""
        # First get a result ID from leaderboard
        success, response = self.run_test(
            "Get Leaderboard for Challenge Test",
            "GET",
            "api/leaderboard",
            200
        )
        
        if not success or 'leaderboard' not in response or len(response['leaderboard']) == 0:
            print("❌ No results available for challenge testing")
            return False
            
        result_id = response['leaderboard'][0]['id']
        print(f"   Using result ID: {result_id}")
        
        # Test valid challenge
        challenge_data = {
            "result_id": result_id,
            "counter_argument": "The analysis underestimated the market demand. Dog walking is a $1B+ industry and there's clear evidence of unmet demand in urban areas. The convenience factor and safety features (GPS tracking) provide significant differentiation from existing services that justifies the evaluation."
        }
        
        success, response = self.run_test(
            "Challenge Verdict - Valid Request",
            "POST",
            "api/challenge",
            200,
            data=challenge_data,
            timeout=60  # AI calls take time
        )
        
        if success:
            # Check required fields
            required_fields = ["counter_status", "reasoning"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Response missing required fields: {missing_fields}")
                return False
            
            # Validate counter_status format
            if response['counter_status'] in ['ACCEPTED', 'REJECTED']:
                print(f"   ✅ Valid counter_status: {response['counter_status']}")
            else:
                print(f"   ❌ Invalid counter_status: {response['counter_status']}")
                return False
                
            # Validate reasoning format
            if isinstance(response['reasoning'], str) and len(response['reasoning']) > 10:
                print(f"   ✅ Valid reasoning (length: {len(response['reasoning'])})")
                print(f"   Reasoning preview: {response['reasoning'][:100]}...")
            else:
                print("   ❌ Invalid reasoning format or too short")
                return False
                
            return True
        else:
            return False

    def test_challenge_validation_errors(self):
        """Test challenge endpoint validation - NEW for iteration 5"""
        # Get a valid result ID first
        success, response = self.run_test(
            "Get Leaderboard for Validation Test",
            "GET",
            "api/leaderboard",
            200
        )
        
        if not success or 'leaderboard' not in response or len(response['leaderboard']) == 0:
            print("❌ No results available for validation testing")
            return False
            
        result_id = response['leaderboard'][0]['id']
        
        # Test 1: Short argument (should fail with 400)
        short_data = {
            "result_id": result_id,
            "counter_argument": "No"
        }
        
        success1, response1 = self.run_test(
            "Challenge Validation - Short Argument",
            "POST",
            "api/challenge",
            400,  # Should return 400 for short argument
            data=short_data
        )
        
        if success1:
            print("   ✅ Correctly rejects short arguments")
        
        # Test 2: Invalid result ID (should fail with 404)
        invalid_data = {
            "result_id": "invalid_id_12345",
            "counter_argument": "This is a longer argument that should pass validation but fail on result lookup because the result ID does not exist in the database."
        }
        
        success2, response2 = self.run_test(
            "Challenge Validation - Invalid Result ID",
            "POST",
            "api/challenge",
            404,  # Should return 404 for invalid result ID
            data=invalid_data
        )
        
        if success2:
            print("   ✅ Correctly rejects invalid result IDs")
        
        # Test 3: Missing fields
        missing_field_data = {
            "result_id": result_id
            # Missing counter_argument
        }
        
        success3, response3 = self.run_test(
            "Challenge Validation - Missing Counter Argument",
            "POST",
            "api/challenge",
            422,  # Should return 422 for missing required field
            data=missing_field_data
        )
        
        if success3:
            print("   ✅ Correctly rejects missing fields")
        
        return success1 and success2 and success3

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting NoFlop.ai API Tests - Iteration 5")
        print("=" * 50)
        
        # Test health endpoint
        health_success = self.test_health_endpoint()
        
        # Test validate endpoint - success case
        validate_success = self.test_validate_endpoint_success()
        
        # Test validate endpoint - structured input (NEW for iteration 4)
        validate_structured_success = self.test_validate_endpoint_structured_input()
        
        # Test validate endpoint - error cases
        validate_short_success = self.test_validate_endpoint_short_idea()
        validate_empty_success = self.test_validate_endpoint_empty_idea()
        
        # Test get result endpoint
        get_result_success = self.test_get_result_endpoint()
        get_result_invalid_success = self.test_get_result_invalid_id()
        
        # Test leaderboard endpoint
        leaderboard_success = self.test_leaderboard_endpoint()
        
        # Test challenge endpoint - NEW for iteration 5
        challenge_success = self.test_challenge_verdict_endpoint()
        challenge_validation_success = self.test_challenge_validation_errors()
        
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