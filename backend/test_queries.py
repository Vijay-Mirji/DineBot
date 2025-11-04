"""
Automated Test Script for DineBot
Tests all fixed issues from the enhancement request
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.db_setup import initialize_database
from services.nlp_service import NLPService
from services.query_service import QueryService

class DineBotTester:
    """Automated testing for DineBot query handling"""
    
    def __init__(self):
        """Initialize DineBot components"""
        print("Initializing DineBot Test Suite...")
        print("=" * 60)
        
        # Initialize components
        self.db_manager = initialize_database(Config)
        self.nlp_service = NLPService(Config)
        self.query_service = QueryService(self.db_manager, self.nlp_service, Config)
        
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def run_test(self, test_name: str, query: str, expected_criteria: dict):
        """
        Run a single test case
        
        Args:
            test_name: Name of the test
            query: User query to test
            expected_criteria: Dict with expected conditions
        """
        print(f"\n📝 Test: {test_name}")
        print(f"Query: '{query}'")
        
        try:
            result = self.query_service.handle_query(query)
            
            # Check criteria
            passed = True
            reasons = []
            
            # Check intent
            if 'intent' in expected_criteria:
                expected_intent = expected_criteria['intent']
                actual_intent = result.get('intent')
                if actual_intent != expected_intent:
                    passed = False
                    reasons.append(f"Intent mismatch: expected '{expected_intent}', got '{actual_intent}'")
            
            # Check if specific item found (for price queries)
            if expected_criteria.get('should_find_specific_item'):
                if 'matched_item' not in result:
                    passed = False
                    reasons.append("Should find specific item but didn't")
                else:
                    print(f"   ✓ Found item: {result['matched_item']}")
            
            # Check if should NOT return range (for item-specific price queries)
            if expected_criteria.get('should_not_be_range'):
                if 'data' in result and isinstance(result['data'], dict):
                    if 'min' in result['data'] and 'max' in result['data']:
                        passed = False
                        reasons.append("Returned price range instead of specific price")
            
            # Check dietary filter (all items should match)
            if 'dietary_filter' in expected_criteria:
                diet_type = expected_criteria['dietary_filter']
                if 'data' in result and isinstance(result['data'], list):
                    for item in result['data']:
                        if diet_type == 'vegetarian' and not item.get('vegetarian'):
                            passed = False
                            reasons.append(f"Non-vegetarian item found: {item['name']}")
                        elif diet_type == 'vegan' and not item.get('vegan'):
                            passed = False
                            reasons.append(f"Non-vegan item found: {item['name']}")
                        elif diet_type == 'non-vegetarian' and item.get('vegetarian'):
                            passed = False
                            reasons.append(f"Vegetarian item in non-veg results: {item['name']}")
            
            # Check price boundary (all items should be within bounds)
            if 'max_price' in expected_criteria:
                max_price = expected_criteria['max_price']
                inclusive = expected_criteria.get('max_inclusive', True)
                
                if 'data' in result and isinstance(result['data'], list):
                    for item in result['data']:
                        price = item.get('price')
                        if inclusive:
                            if price > max_price:
                                passed = False
                                reasons.append(f"Item exceeds max price: {item['name']} (₹{price} > ₹{max_price})")
                        else:
                            if price >= max_price:
                                passed = False
                                reasons.append(f"Item at/above strict max: {item['name']} (₹{price} >= ₹{max_price})")
            
            if 'min_price' in expected_criteria:
                min_price = expected_criteria['min_price']
                inclusive = expected_criteria.get('min_inclusive', True)
                
                if 'data' in result and isinstance(result['data'], list):
                    for item in result['data']:
                        price = item.get('price')
                        if inclusive and price < min_price:
                            passed = False
                            reasons.append(f"Item below min price: {item['name']} (₹{price} < ₹{min_price})")
                        elif not inclusive and price <= min_price:
                            passed = False
                            reasons.append(f"Item at/below strict min: {item['name']} (₹{price} <= ₹{min_price})")
            
            # Check if results should be empty
            if expected_criteria.get('should_be_empty'):
                if 'data' in result:
                    data = result['data']
                    if isinstance(data, list) and len(data) > 0:
                        passed = False
                        reasons.append(f"Expected no results, but got {len(data)} items")
            
            # Check if results should NOT be empty
            if expected_criteria.get('should_not_be_empty'):
                if 'data' in result:
                    data = result['data']
                    if isinstance(data, list) and len(data) == 0:
                        passed = False
                        reasons.append("Expected results, but got none")
            
            # Print result
            if passed:
                print(f"   ✅ PASSED")
                self.passed += 1
            else:
                print(f"   ❌ FAILED")
                for reason in reasons:
                    print(f"      - {reason}")
                self.failed += 1
            
            self.test_results.append({
                'test': test_name,
                'passed': passed,
                'reasons': reasons
            })
            
        except Exception as e:
            print(f"   ❌ FAILED - Exception: {e}")
            self.failed += 1
            self.test_results.append({
                'test': test_name,
                'passed': False,
                'reasons': [f"Exception: {e}"]
            })
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "=" * 60)
        print("STARTING TEST SUITE")
        print("=" * 60)
        
        # ========== FIX 1 TESTS: Item-Specific Price Queries ==========
        print("\n" + "=" * 60)
        print("FIX 1: Item-Specific Price Query Tests")
        print("=" * 60)
        
        self.run_test(
            "Item Price Query 1: 'pizza cost'",
            "pizza cost",
            {
                'intent': 'item_price_query',
                'should_find_specific_item': True,
                'should_not_be_range': True
            }
        )
        
        self.run_test(
            "Item Price Query 2: 'how much is biryani'",
            "how much is biryani",
            {
                'intent': 'item_price_query',
                'should_find_specific_item': True,
                'should_not_be_range': True
            }
        )
        
        self.run_test(
            "Item Price Query 3: 'price of chicken tikka'",
            "price of chicken tikka",
            {
                'intent': 'item_price_query',
                'should_find_specific_item': True,
                'should_not_be_range': True
            }
        )
        
        self.run_test(
            "General Price Query: 'menu prices'",
            "menu prices",
            {
                'intent': 'price_range_query',
            }
        )
        
        # ========== FIX 2 TESTS: Dietary Filters ==========
        print("\n" + "=" * 60)
        print("FIX 2: Dietary Filter Tests")
        print("=" * 60)
        
        self.run_test(
            "Vegetarian Filter: 'show vegetarian options'",
            "show vegetarian options",
            {
                'dietary_filter': 'vegetarian',
                'should_not_be_empty': True
            }
        )
        
        self.run_test(
            "Vegan Filter: 'show vegan dishes'",
            "show vegan dishes",
            {
                'dietary_filter': 'vegan',
                'should_not_be_empty': True
            }
        )
        
        self.run_test(
            "Non-Veg Query: 'show me chicken items'",
            "show me chicken items",
            {
                'should_not_be_empty': True
            }
        )
        
        # ========== FIX 3 TESTS: Price Boundaries ==========
        print("\n" + "=" * 60)
        print("FIX 3: Price Boundary Tests")
        print("=" * 60)
        
        self.run_test(
            "Under 300 (strict): 'vegetarian main course items under 300'",
            "vegetarian main course items under 300",
            {
                'dietary_filter': 'vegetarian',
                'max_price': 299,  # Should be < 300, so <= 299
                'max_inclusive': True  # We already subtracted 1, so use <=
            }
        )
        
        self.run_test(
            "300 or less (inclusive): 'vegetarian items 300 or less'",
            "vegetarian items 300 or less",
            {
                'dietary_filter': 'vegetarian',
                'max_price': 300,
                'max_inclusive': True
            }
        )
        
        self.run_test(
            "Under 150: 'show appetizers under 150'",
            "show appetizers under 150",
            {
                'max_price': 149,
                'max_inclusive': True  # We already subtracted 1
            }
        )
        
        # ========== COMBINED FILTER TESTS ==========
        print("\n" + "=" * 60)
        print("Combined Filter Tests")
        print("=" * 60)
        
        self.run_test(
            "Category + Diet + Price: 'vegetarian main course under 300'",
            "vegetarian main course under 300",
            {
                'dietary_filter': 'vegetarian',
                'max_price': 299,
                'max_inclusive': True  # Already subtracted 1
            }
        )
        
        self.run_test(
            "Vegan + Price: 'vegan items under 200'",
            "vegan items under 200",
            {
                'dietary_filter': 'vegan',
                'max_price': 199,
                'max_inclusive': True  # Already subtracted 1
            }
        )
        
        # ========== EDGE CASES ==========
        print("\n" + "=" * 60)
        print("Edge Case Tests")
        print("=" * 60)
        
        self.run_test(
            "Typo handling: 'piza cost'",
            "piza cost",
            {
                'intent': 'item_price_query',
                'should_find_specific_item': True
            }
        )
        
        self.run_test(
            "No results: 'vegetarian desserts under 50'",
            "vegetarian desserts under 50",
            {
                'should_be_empty': True
            }
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        if self.failed > 0:
            print("\n" + "=" * 60)
            print("FAILED TESTS DETAILS")
            print("=" * 60)
            for result in self.test_results:
                if not result['passed']:
                    print(f"\n❌ {result['test']}")
                    for reason in result['reasons']:
                        print(f"   - {reason}")
        
        print("\n" + "=" * 60)
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED! 🎉")
        else:
            print("⚠️  SOME TESTS FAILED - REVIEW ABOVE")
        
        print("=" * 60 + "\n")


if __name__ == "__main__":
    tester = DineBotTester()
    tester.run_all_tests()