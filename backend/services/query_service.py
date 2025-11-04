"""
Query Service for DineBot
Handles business logic and response generation

Enhanced Query Service for DineBot
Fixes: Item-specific price queries, strict dietary filtering, price boundary logic
"""
import random
import re
from typing import Dict, List, Optional

class QueryService:
    """Processes intents and generates appropriate responses with enhanced filtering"""
    
    def __init__(self, db_manager, nlp_service, config):
        """Initialize with database manager and NLP service"""
        self.db = db_manager
        self.nlp = nlp_service
        self.config = config
    
    def handle_query(self, user_input: str) -> Dict:
        """
        Main query handler with enhanced intent routing
        
        FIX 1: Separate handling for item_price_query vs price_range_query
        """
        # Process input with NLP
        nlp_result = self.nlp.process_query(user_input)
        intent = nlp_result['intent']
        entities = nlp_result['entities']
        confidence = nlp_result['confidence']
        has_specific_item = nlp_result['has_specific_item']
        
        # Route to appropriate handler based on intent
        handlers = {
            'greeting': self._handle_greeting,
            'menu_list': self._handle_menu_list,
            'item_details': self._handle_item_details,
            'item_price_query': self._handle_item_price_query,  # FIX 1: New handler
            'price_range_query': self._handle_price_range_query,  # FIX 1: Renamed
            'category_query': self._handle_category_query,
            'restaurant_info': self._handle_restaurant_info,
        }
        
        # FIX 1: Legacy 'price_query' intent support (map to appropriate handler)
        if intent == 'price_query':
            if has_specific_item:
                handler = self._handle_item_price_query
            else:
                handler = self._handle_price_range_query
        else:
            handler = handlers.get(intent, self._handle_unknown)
        
        result = handler(user_input, entities)
        
        # Add metadata
        result['intent'] = intent
        result['confidence'] = confidence
        
        return result
    
    def _handle_greeting(self, query: str, entities: Dict) -> Dict:
        """Handle greeting intent"""
        greetings = [
            "Hello! Welcome to The Golden Spoon. How can I help you today?",
            "Hi there! I'm DineBot, your virtual assistant. Ask me about our menu!",
            "Greetings! Looking for something delicious? I can help you explore our menu.",
        ]
        
        return {
            'response': random.choice(greetings),
            'suggestions': [
                'Show me the menu',
                'What are your timings?',
                'Tell me about desserts'
            ]
        }
    
    def _handle_menu_list(self, query: str, entities: Dict) -> Dict:
        """
        Handle menu listing with enhanced filtering
        
        FIX 2: Strict dietary filtering
        FIX 3: Correct price boundary application
        """
        # Get all items or filter by category
        if 'category' in entities:
            items = self.db.get_items_by_category(entities['category'])
            category_name = entities['category'].title()
            response = f"Here are our {category_name} items:"
        else:
            items = self.db.get_all_items()
            response = "Here's our complete menu:"
        
        # FIX 2: Apply strict dietary filters
        items = self._apply_dietary_filters(items, entities)
        
        # FIX 3: Apply price filters with correct boundaries
        items = self._apply_price_filters(items, entities)
        
        # Update response based on filters
        if 'dietary_filter' in entities:
            diet_type = entities['dietary_filter'].title()
            response += f" ({diet_type} options)"
        
        if 'max_price' in entities or 'min_price' in entities:
            price_desc = self._get_price_filter_description(entities)
            response += f" {price_desc}"
        
        if not items:
            # FIX 4: Better fallback message with filter details
            filter_desc = self._describe_applied_filters(entities)
            return {
                'response': f"Sorry, I couldn't find any items matching your criteria{filter_desc}.",
                'data': [],
                'suggestions': [
                    'Show me the full menu',
                    'What vegetarian options do you have?',
                    'Show me appetizers'
                ]
            }
        
        return {
            'response': response,
            'data': self._format_menu_items(items),
            'count': len(items)
        }
    
    def _handle_item_price_query(self, query: str, entities: Dict) -> Dict:
        """
        FIX 1: Handle item-specific price queries
        
        Examples: "pizza cost", "how much is biryani", "price of chicken tikka"
        Returns: Specific item price, not range
        """
        all_items = self.db.get_all_items()
        
        # Try fuzzy matching with the full query
        match_result = self.nlp.fuzzy_match_item(query, all_items)
        
        if match_result and match_result['confidence'] > 0.6:
            item = match_result['item']
            
            # Format response with item details
            veg_tag = "🥬 Vegetarian" if item['is_vegetarian'] else "🍖 Non-Vegetarian"
            response = (
                f"💰 {item['name']} costs ₹{item['price']}\n\n"
                f"{veg_tag} | {item['category']}\n"
                f"📝 {item['description']}"
            )
            
            return {
                'response': response,
                'data': {
                    'name': item['name'],
                    'price': item['price'],
                    'category': item['category'],
                    'is_vegetarian': item['is_vegetarian'],
                    'is_vegan': item['is_vegan']
                },
                'matched_item': item['name'],
                'match_confidence': match_result['confidence']
            }
        
        # If no good match found, try searching by potential item names
        if 'potential_items' in entities:
            for potential_name in entities['potential_items']:
                items = self.db.search_items(potential_name)
                if items:
                    if len(items) == 1:
                        item = items[0]
                        return {
                            'response': f"{item['name']} costs ₹{item['price']}.",
                            'data': {
                                'name': item['name'],
                                'price': item['price'],
                                'category': item['category']
                            }
                        }
                    else:
                        # Multiple matches - ask for clarification
                        item_list = ', '.join([f"{item['name']} (₹{item['price']})" for item in items[:3]])
                        return {
                            'response': f"I found multiple items. Which one did you mean?\n{item_list}",
                            'data': items[:3]
                        }
        
        # No match found - suggest alternatives
        return {
            'response': "I couldn't find that specific item. Could you try rephrasing? Or type 'show menu' to see all items.",
            'suggestions': [
                'Show me the menu',
                'How much is pizza?',
                'What are your prices?'
            ]
        }
    
    def _handle_price_range_query(self, query: str, entities: Dict) -> Dict:
        """
        FIX 1: Handle general price range queries (renamed from _handle_price_query)
        
        Examples: "menu prices", "price range", "how much for everything"
        Returns: Price range/statistics
        """
        items = self.db.get_all_items()
        
        # Apply category filter if specified
        if 'category' in entities:
            items = self.db.get_items_by_category(entities['category'])
        
        # FIX 2: Apply dietary filters
        items = self._apply_dietary_filters(items, entities)
        
        if not items:
            filter_desc = self._describe_applied_filters(entities)
            return {
                'response': f"I couldn't find any items matching your criteria{filter_desc}.",
                'suggestions': ['Show me the full menu']
            }
        
        # Calculate price statistics
        prices = [item['price'] for item in items]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        category_text = f" for {entities['category']}" if 'category' in entities else ""
        diet_text = f" ({entities['dietary_filter']})" if 'dietary_filter' in entities else ""
        
        response = (
            f"💰 Our prices{category_text}{diet_text}:\n\n"
            f"• Lowest: ₹{min_price}\n"
            f"• Highest: ₹{max_price}\n"
            f"• Average: ₹{avg_price:.0f}\n\n"
            f"Total items: {len(items)}"
        )
        
        return {
            'response': response,
            'data': {
                'min': min_price,
                'max': max_price,
                'average': round(avg_price, 2),
                'count': len(items)
            }
        }
    
    def _handle_item_details(self, query: str, entities: Dict) -> Dict:
        """Handle requests for specific item details"""
        all_items = self.db.get_all_items()
        
        # Check if query is a simple search (like "show chicken items")
        # This should return a list, not details
        if re.search(r'\b(show|list|display).*\b(chicken|fish|meat|paneer|veg)\b', query.lower()):
            # Treat as a filtered menu query
            keyword = None
            if 'chicken' in query.lower():
                keyword = 'chicken'
            elif 'fish' in query.lower():
                keyword = 'fish'
            elif 'paneer' in query.lower():
                keyword = 'paneer'
            
            if keyword:
                items = self.db.search_items(keyword)
                if items:
                    return {
                        'response': f"Here are items with {keyword}:",
                        'data': self._format_menu_items(items),
                        'count': len(items)
                    }
        
        # Try fuzzy matching
        match_result = self.nlp.fuzzy_match_item(query, all_items)
        
        if match_result and match_result['confidence'] > 0.6:
            item = match_result['item']
            response = self._format_item_details(item)
            
            return {
                'response': response,
                'data': item,
                'matched_item': item['name'],
                'match_confidence': match_result['confidence']
            }
        
        # Try keyword search
        if 'potential_items' in entities:
            for potential_name in entities['potential_items']:
                items = self.db.search_items(potential_name)
                if items:
                    if len(items) == 1:
                        item = items[0]
                        response = self._format_item_details(item)
                        return {
                            'response': response,
                            'data': item,
                            'matched_item': item['name']
                        }
                    else:
                        # Multiple matches found
                        item_names = [item['name'] for item in items[:5]]
                        return {
                            'response': f"I found multiple items. Did you mean: {', '.join(item_names)}?",
                            'data': items[:5]
                        }
        
        # No match found
        return {
            'response': "I couldn't find that item. Try asking about specific dishes like 'pizza' or 'chicken tikka', or type 'show menu'.",
            'suggestions': ['Show menu', 'What are your appetizers?', 'Tell me about desserts']
        }
    
    def _handle_category_query(self, query: str, entities: Dict) -> Dict:
        """
        Handle category-specific queries with enhanced filtering
        
        FIX 2 & FIX 3: Apply dietary and price filters
        """
        category = entities.get('category')
        
        if category:
            items = self.db.get_items_by_category(category)
            
            # FIX 2: Apply dietary filters
            items = self._apply_dietary_filters(items, entities)
            
            # FIX 3: Apply price filters
            items = self._apply_price_filters(items, entities)
            
            if items:
                response = f"Here are our {category.title()} items"
                
                # Add filter descriptions
                if 'dietary_filter' in entities:
                    response += f" ({entities['dietary_filter']})"
                if 'max_price' in entities or 'min_price' in entities:
                    response += f" {self._get_price_filter_description(entities)}"
                response += ":"
                
                return {
                    'response': response,
                    'data': self._format_menu_items(items),
                    'count': len(items)
                }
            else:
                filter_desc = self._describe_applied_filters(entities)
                return {
                    'response': f"Sorry, I couldn't find any {category} items{filter_desc}.",
                    'suggestions': [f'Show all {category}s', 'Show me the full menu']
                }
        
        # Show all categories
        categories = self.db.get_categories()
        return {
            'response': f"We have these categories: {', '.join(categories)}. Which would you like to explore?",
            'data': {'categories': categories}
        }
    
    def _handle_restaurant_info(self, query: str, entities: Dict) -> Dict:
        """Handle restaurant information queries"""
        info_type = self.nlp.extract_info_type(query)
        restaurant = self.config.RESTAURANT_INFO
        
        if info_type == 'hours':
            hours = restaurant['opening_hours']
            response = (
                f"⏰ Opening Hours:\n"
                f"Weekdays: {hours['weekday']}\n"
                f"Weekends: {hours['weekend']}\n"
                f"Closed on: {hours['closed']}"
            )
        
        elif info_type == 'address':
            response = (
                f"📍 Location:\n{restaurant['name']}\n"
                f"{restaurant['address']}"
            )
        
        elif info_type == 'contact':
            response = (
                f"📞 Contact Us:\n"
                f"Phone: {restaurant['phone']}\n"
                f"Email: {restaurant['email']}"
            )
        
        else:
            # General info
            response = (
                f"🍽️ {restaurant['name']}\n"
                f"📍 {restaurant['address']}\n"
                f"📞 {restaurant['phone']}\n"
                f"⏰ Open {restaurant['opening_hours']['weekday']} (Closed {restaurant['opening_hours']['closed']})\n"
                f"🍴 Cuisines: {', '.join(restaurant['cuisine_types'])}\n"
                f"💺 Seating: {restaurant['seating_capacity']} people\n"
                f"✨ Facilities: {', '.join(restaurant['facilities'])}"
            )
        
        return {
            'response': response,
            'data': restaurant
        }
    
    def _handle_unknown(self, query: str, entities: Dict) -> Dict:
        """Handle unrecognized queries"""
        return {
            'response': random.choice(self.config.FALLBACK_RESPONSES),
            'suggestions': [
                'Show me the menu',
                'What are your timings?',
                'Tell me about your location'
            ]
        }
    
    # ========== ENHANCED FILTERING METHODS ==========
    
    def _apply_dietary_filters(self, items: List[Dict], entities: Dict) -> List[Dict]:
        """
        FIX 2: Apply strict dietary filters
        
        Logic:
        - If 'is_vegetarian' == True in entities, return ONLY vegetarian items
        - If 'is_vegan' == True, return ONLY vegan items
        - If 'is_vegetarian' == False, return ONLY non-vegetarian items
        - No mixed results
        """
        filtered_items = items
        
        # Vegan filter (most restrictive)
        if entities.get('is_vegan') is True:
            filtered_items = [item for item in filtered_items if item['is_vegan'] is True]
        
        # Vegetarian filter (if vegan not specified)
        elif entities.get('is_vegetarian') is True:
            filtered_items = [item for item in filtered_items if item['is_vegetarian'] is True]
        
        # Non-vegetarian filter
        elif entities.get('is_vegetarian') is False:
            filtered_items = [item for item in filtered_items if item['is_vegetarian'] is False]
        
        # Spice level filter
        if 'spice_level' in entities:
            spice = entities['spice_level']
            filtered_items = [item for item in filtered_items if item['spice_level'] == spice]
        
        return filtered_items
    
    def _apply_price_filters(self, items: List[Dict], entities: Dict) -> List[Dict]:
        """
        FIX 3: Apply price filters with correct boundary logic
        
        Logic:
        - "under 300" → price < 300 (price <= 299)
        - "300 or less" → price <= 300
        - "above 200" → price > 200 (price >= 201)
        - "200 or more" → price >= 200
        """
        filtered_items = items
        
        # Apply maximum price filter
        if 'max_price' in entities:
            max_price = entities['max_price']
            is_inclusive = entities.get('max_inclusive', False)
            
            if is_inclusive:
                # "300 or less" → price <= 300
                filtered_items = [item for item in filtered_items if item['price'] <= max_price]
            else:
                # "under 300" → price < 300 (already handled: max_price = 299)
                filtered_items = [item for item in filtered_items if item['price'] <= max_price]
        
        # Apply minimum price filter
        if 'min_price' in entities:
            min_price = entities['min_price']
            is_inclusive = entities.get('min_inclusive', True)
            
            if is_inclusive:
                # "200 or more" → price >= 200
                filtered_items = [item for item in filtered_items if item['price'] >= min_price]
            else:
                # "above 200" → price > 200 (already handled: min_price = 201)
                filtered_items = [item for item in filtered_items if item['price'] >= min_price]
        
        # Apply price preference (relative)
        if 'price_preference' in entities:
            pref = entities['price_preference']
            if filtered_items:
                prices = [item['price'] for item in filtered_items]
                median_price = sorted(prices)[len(prices) // 2]
                
                if pref == 'low':
                    filtered_items = [item for item in filtered_items if item['price'] <= median_price]
                elif pref == 'high':
                    filtered_items = [item for item in filtered_items if item['price'] >= median_price]
        
        return filtered_items
    
    def _get_price_filter_description(self, entities: Dict) -> str:
        """Generate human-readable price filter description"""
        parts = []
        
        if 'max_price' in entities:
            max_price = entities['max_price']
            if entities.get('max_inclusive'):
                parts.append(f"₹{max_price} or less")
            else:
                parts.append(f"under ₹{max_price + 1}")  # Display original value
        
        if 'min_price' in entities:
            min_price = entities['min_price']
            if entities.get('min_inclusive'):
                parts.append(f"₹{min_price} or more")
            else:
                parts.append(f"above ₹{min_price - 1}")  # Display original value
        
        if parts:
            return f"(priced {' and '.join(parts)})"
        return ""
    
    def _describe_applied_filters(self, entities: Dict) -> str:
        """Generate description of all applied filters for error messages"""
        filters = []
        
        if 'category' in entities:
            filters.append(entities['category'])
        
        if 'dietary_filter' in entities:
            filters.append(entities['dietary_filter'])
        
        if 'max_price' in entities or 'min_price' in entities:
            price_desc = self._get_price_filter_description(entities)
            filters.append(price_desc)
        
        if filters:
            return f" matching: {', '.join(filters)}"
        return ""
    
    # ========== FORMATTING METHODS ==========
    
    def _format_menu_items(self, items: List[Dict]) -> List[Dict]:
        """Format menu items for display"""
        formatted = []
        for item in items:
            formatted.append({
                'name': item['name'],
                'price': item['price'],
                'category': item['category'],
                'description': item['description'],
                'vegetarian': item['is_vegetarian'],
                'vegan': item['is_vegan'],
                'spice_level': item['spice_level']
            })
        return formatted
    
    def _format_item_details(self, item: Dict) -> str:
        """Format detailed item information as text"""
        veg_tag = "🥬 Vegetarian" if item['is_vegetarian'] else "🍖 Non-Vegetarian"
        vegan_tag = " | 🌱 Vegan" if item['is_vegan'] else ""
        spice_tag = f" | 🌶️ {item['spice_level'].title()}" if item['spice_level'] != 'none' else ""
        
        response = (
            f"🍽️ {item['name']} - ₹{item['price']}\n"
            f"{veg_tag}{vegan_tag}{spice_tag}\n\n"
            f"📝 {item['description']}\n\n"
            f"🥘 Ingredients: {', '.join(item['ingredients'])}\n"
            f"⏱️ Prep time: ~{item['preparation_time']} minutes"
        )
        
        return response
    
    # ========== PUBLIC API METHODS ==========
    
    def get_menu_items(self) -> List[Dict]:
        """Public method: Get all menu items"""
        return self.db.get_all_items()
    
    def get_item_details(self, item_name: str) -> Dict:
        """Public method: Get details of specific item"""
        return self.db.get_item_by_name(item_name)
    
    def get_restaurant_info(self, query_type: str = 'general') -> Dict:
        """Public method: Get restaurant information"""
        return self.config.RESTAURANT_INFO