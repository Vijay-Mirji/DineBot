"""
NLP Service for DineBot
Uses lightweight rule-based patterns + spaCy for entity extraction
Optimized for budget laptops

Enhanced NLP Service for DineBot
Fixes: Price query specificity, entity extraction, price range parsing
"""
import spacy
import re
from fuzzywuzzy import fuzz
from typing import Dict, List, Optional, Tuple

class NLPService:
    """Handles natural language understanding for DineBot with enhanced accuracy"""
    
    def __init__(self, config):
        """Initialize NLP service with spaCy model"""
        self.config = config
        try:
            self.nlp = spacy.load(config.SPACY_MODEL)
            print(f"✓ Loaded spaCy model: {config.SPACY_MODEL}")
        except OSError:
            print(f"⚠ spaCy model not found. Run: python -m spacy download {config.SPACY_MODEL}")
            self.nlp = None
    
    def process_query(self, user_input: str) -> Dict:
        """
        Process user input and extract intent + entities
        Returns: {
            'intent': str,
            'entities': dict,
            'confidence': float,
            'has_specific_item': bool  # NEW: indicates if query mentions specific dish
        }
        """
        user_input = user_input.strip().lower()
        
        # Extract intent using enhanced pattern matching
        intent_result = self._extract_intent(user_input)
        
        # Extract entities (dish names, categories, price bounds, etc.)
        entities = self._extract_entities(user_input)
        
        # FIX 1: Detect if query contains specific item name
        has_specific_item = self._has_specific_item_mention(user_input, entities)
        
        return {
            'intent': intent_result['intent'],
            'entities': entities,
            'confidence': intent_result['confidence'],
            'has_specific_item': has_specific_item,
            'original_query': user_input
        }
    
    def _extract_intent(self, text: str) -> Dict:
        """
        Enhanced intent classification with better price query detection
        
        FIX 1: Separate item-specific price queries from general price range queries
        New logic:
        - "pizza cost" → item_price_query (specific item)
        - "menu prices" → price_range_query (general)
        - "price of chicken tikka" → item_price_query (specific item)
        """
        
        # Greeting patterns
        greeting_patterns = [
            r'\b(hi|hello|hey|greetings|good morning|good evening)\b'
        ]
        
        # Menu listing patterns
        menu_patterns = [
            r'\b(show|display|list|what).*(menu|items|dishes|food)',
            r'\bwhat.*(?:have|available|serve)',
            r'\bmenu\b(?!.*price)',  # "menu" but not "menu price"
        ]
        
        # FIX 1: Enhanced price patterns with specificity detection
        # General price range patterns (CHECK FIRST - higher priority)
        price_range_patterns = [
            r'\b(?:menu|all|overall|general)\s*(?:price|cost|rate)',  # "menu prices"
            r'\bprice\s*(?:range|list)',  # "price range"
            r'\bhow much.*(?:everything|menu|all)',  # "how much for everything"
            r'\bwhat.*(?:price|cost).*(?:in general|overall|menu)',
            r'\b(?:show|tell|what).*(?:menu|all).*(?:price|cost)',  # "show menu prices"
        ]
        
        # Item-specific price patterns (check second - lower priority)
        item_price_patterns = [
            r'\b\w+\s+(cost|price|rate)',  # "pizza cost", "biryani price"
            r'\bhow much.*(?:is|for|does)\s+(?:the\s+)?\w+',  # "how much is pizza"
            r'\bprice.*(?:of|for)\s+\w+',  # "price of pizza"
            r'\bcost.*(?:of|for)\s+\w+',  # "cost of chicken"
            r'\bwhat.*(?:cost|price).*\w+(?:cost|price)',  # "what's the pizza price"
        ]
        
        # Item details patterns
        details_patterns = [
            r'\b(tell|what|about|info|details|describe).*(?!price|cost)',
            r'\b(ingredient|contain|made of|recipe)',
            r'\b(vegetarian|vegan|spicy|spice level)'
        ]
        
        # Category query patterns
        category_patterns = [
            r'\b(appetizer|starter|main course|dessert|beverage|drink)',
            r'\bshow.*(category|type)',
            r'\b(?:list|show).*(?:appetizer|starter|main|dessert|beverage)'
        ]
        
        # Restaurant info patterns
        info_patterns = [
            r'\b(address|location|where|situated)',
            r'\b(timing|hours|open|close|when)',
            r'\b(contact|phone|email|call)',
            r'\b(about|info).*restaurant',
            r'\brestaurant.*(?:info|detail|about)'
        ]
        
        # Check patterns in priority order
        if any(re.search(p, text) for p in greeting_patterns):
            return {'intent': 'greeting', 'confidence': 0.9}
        
        # FIX 1: Check general price range patterns FIRST (they're more specific)
        if any(re.search(p, text) for p in price_range_patterns):
            return {'intent': 'price_range_query', 'confidence': 0.9}
        
        # Then check item-specific price patterns
        if any(re.search(p, text) for p in item_price_patterns):
            # Additional check: ensure there's a potential item name
            if self._contains_potential_item_name(text):
                return {'intent': 'item_price_query', 'confidence': 0.9}
        
        # Generic price/cost mention (could be either)
        if re.search(r'\b(price|cost|how much|rate|expensive|cheap)', text):
            # If contains item indicators, treat as item query
            if self._contains_potential_item_name(text):
                return {'intent': 'item_price_query', 'confidence': 0.75}
            return {'intent': 'price_range_query', 'confidence': 0.7}
        
        if any(re.search(p, text) for p in category_patterns):
            return {'intent': 'category_query', 'confidence': 0.85}
        
        if any(re.search(p, text) for p in info_patterns):
            return {'intent': 'restaurant_info', 'confidence': 0.85}
        
        if any(re.search(p, text) for p in details_patterns):
            return {'intent': 'item_details', 'confidence': 0.8}
        
        if any(re.search(p, text) for p in menu_patterns):
            return {'intent': 'menu_list', 'confidence': 0.85}
        
        # Default to item details for simple queries
        if len(text.split()) <= 3:
            return {'intent': 'item_details', 'confidence': 0.6}
        
        return {'intent': 'unknown', 'confidence': 0.3}
    
    def _contains_potential_item_name(self, text: str) -> bool:
        """
        FIX 1: Check if query contains potential dish name
        Returns True if text has food-related nouns or common dish words
        """
        # Common dish-related words
        food_words = [
            'pizza', 'biryani', 'chicken', 'paneer', 'tikka', 'masala',
            'salad', 'wings', 'rolls', 'cake', 'lassi', 'chai', 'soda',
            'jamun', 'lava', 'spring', 'caesar', 'mango', 'chocolate',
            'butter', 'rice'
        ]
        
        # Check for any food words
        for word in food_words:
            if word in text:
                return True
        
        # Check for noun phrases using spaCy
        if self.nlp:
            doc = self.nlp(text)
            # Look for noun chunks that might be dish names
            for chunk in doc.noun_chunks:
                # Skip generic nouns
                if chunk.text not in ['price', 'cost', 'rate', 'menu', 'dish', 'item', 'food']:
                    return True
        
        return False
    
    def _has_specific_item_mention(self, text: str, entities: Dict) -> bool:
        """
        FIX 1: Determine if query mentions a specific item vs. general category
        """
        # If we found potential items in entity extraction
        if 'potential_items' in entities and entities['potential_items']:
            return True
        
        # If query has food-related words
        if self._contains_potential_item_name(text):
            return True
        
        # If query is very short and has a noun (likely item name)
        if len(text.split()) <= 3 and self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ == 'NOUN' and token.text not in ['price', 'cost', 'menu']:
                    return True
        
        return False
    
    def _extract_entities(self, text: str) -> Dict:
        """
        Enhanced entity extraction with better price bounds and dietary flags
        
        FIX 2: Stricter dietary filter mapping
        FIX 3: Better numeric price boundary extraction
        """
        entities = {}
        
        # Extract category mentions
        categories = ['appetizer', 'starter', 'main course', 'dessert', 'beverage', 'drink']
        for category in categories:
            if category in text:
                entities['category'] = category
                if category == 'drink':
                    entities['category'] = 'beverage'
                if category == 'starter':
                    entities['category'] = 'appetizer'
                break
        
        # FIX 2: Enhanced dietary preference extraction
        # Map to strict boolean flags
        if re.search(r'\b(vegetarian|veg\b|veggie)', text):
            entities['is_vegetarian'] = True
            entities['dietary_filter'] = 'vegetarian'
        
        if re.search(r'\bvegan\b', text):
            entities['is_vegan'] = True
            entities['dietary_filter'] = 'vegan'
        
        if re.search(r'\b(non-veg|non veg|nonveg|meat|chicken|fish)', text):
            entities['is_vegetarian'] = False
            entities['dietary_filter'] = 'non-vegetarian'
        
        # Extract spice level
        if re.search(r'\b(spicy|hot|chili)', text):
            entities['spice_level'] = 'hot'
        if re.search(r'\b(mild|less spicy|not spicy)', text):
            entities['spice_level'] = 'mild'
        
        # FIX 3: Enhanced price boundary extraction
        price_bounds = self._extract_price_bounds(text)
        if price_bounds:
            entities.update(price_bounds)
        
        # Extract price preference
        if re.search(r'\b(cheap|affordable|budget|low price)', text):
            entities['price_preference'] = 'low'
        if re.search(r'\b(expensive|premium|costly)', text):
            entities['price_preference'] = 'high'
        
        # Use spaCy for entity extraction if available
        if self.nlp:
            doc = self.nlp(text)
            # Extract noun phrases as potential dish names
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            # Filter out generic nouns
            filtered_phrases = [
                phrase for phrase in noun_phrases 
                if phrase not in ['price', 'cost', 'menu', 'item', 'dish', 'food', 
                                 'option', 'thing', 'restaurant', 'the price']
            ]
            if filtered_phrases:
                entities['potential_items'] = filtered_phrases
        
        return entities
    
    def _extract_price_bounds(self, text: str) -> Dict:
        """
        FIX 3: Extract numeric price boundaries with correct comparison logic
        
        Handles:
        - "under 300" → max_price = 299 (strict <)
        - "300 or less" → max_price = 300 (inclusive <=)
        - "above 200" → min_price = 201 (strict >)
        - "200 or more" → min_price = 200 (inclusive >=)
        - "between 200 and 300" → min_price = 200, max_price = 300
        """
        bounds = {}
        
        # Pattern: "under X" or "below X" (strict less than)
        under_match = re.search(r'\b(?:under|below|less than)\s+(\d+)', text)
        if under_match:
            # FIX 3: Use strict < by subtracting 1 from the number
            value = int(under_match.group(1))
            bounds['max_price'] = value - 1
            bounds['max_inclusive'] = True  # Since we already subtracted 1
        
        # Pattern: "X or less" or "up to X" (inclusive)
        or_less_match = re.search(r'\b(\d+)\s+or\s+less|up\s+to\s+(\d+)', text)
        if or_less_match:
            value = or_less_match.group(1) or or_less_match.group(2)
            bounds['max_price'] = int(value)
            bounds['max_inclusive'] = True
        
        # Pattern: "above X" or "over X" or "more than X" (strict greater than)
        above_match = re.search(r'\b(?:above|over|more than|greater than)\s+(\d+)', text)
        if above_match:
            bounds['min_price'] = int(above_match.group(1)) + 1
            bounds['min_inclusive'] = False
        
        # Pattern: "X or more" or "at least X" (inclusive)
        or_more_match = re.search(r'\b(\d+)\s+or\s+more|at\s+least\s+(\d+)', text)
        if or_more_match:
            value = or_more_match.group(1) or or_more_match.group(2)
            bounds['min_price'] = int(value)
            bounds['min_inclusive'] = True
        
        # Pattern: "between X and Y"
        between_match = re.search(r'\bbetween\s+(\d+)\s+and\s+(\d+)', text)
        if between_match:
            bounds['min_price'] = int(between_match.group(1))
            bounds['max_price'] = int(between_match.group(2))
            bounds['min_inclusive'] = True
            bounds['max_inclusive'] = True
        
        # Pattern: generic number mention (e.g., "300 rupees")
        if not bounds:
            generic_match = re.search(r'\b(\d+)\s*(?:rupees|rs|₹)?', text)
            if generic_match:
                # If "under" or "less" appears nearby, treat as max
                if re.search(r'\b(?:under|less|below)', text):
                    bounds['max_price'] = int(generic_match.group(1)) - 1
                    bounds['max_inclusive'] = False
        
        return bounds
    
    def fuzzy_match_item(self, query: str, menu_items: List[Dict], threshold: float = None) -> Optional[Dict]:
        """
        Find best matching menu item using fuzzy string matching
        Enhanced to better handle partial names
        """
        if threshold is None:
            threshold = self.config.SIMILARITY_THRESHOLD * 100
        
        best_match = None
        best_score = 0
        
        # Extract potential item name from query
        # Remove price-related words first
        cleaned_query = re.sub(r'\b(price|cost|rate|how much|rupees|rs)\b', '', query)
        cleaned_query = cleaned_query.strip()
        
        for item in menu_items:
            # Calculate multiple similarity scores
            full_score = fuzz.ratio(cleaned_query.lower(), item['name'].lower())
            partial_score = fuzz.partial_ratio(cleaned_query.lower(), item['name'].lower())
            token_score = fuzz.token_sort_ratio(cleaned_query.lower(), item['name'].lower())
            
            # Take the best score
            score = max(full_score, partial_score, token_score)
            
            if score > best_score:
                best_score = score
                best_match = item
        
        # Return match only if above threshold
        if best_score >= threshold:
            return {
                'item': best_match,
                'confidence': best_score / 100.0
            }
        
        return None
    
    def extract_info_type(self, text: str) -> str:
        """Determine what type of restaurant info user is asking about"""
        if re.search(r'\b(timing|hours|open|close|when)', text):
            return 'hours'
        if re.search(r'\b(address|location|where|situated)', text):
            return 'address'
        if re.search(r'\b(contact|phone|email|call)', text):
            return 'contact'
        return 'general'