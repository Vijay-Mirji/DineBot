# 🧪 DineBot Testing Guide

This guide helps you test DineBot thoroughly for your college project demonstration.

## 📋 Pre-Testing Checklist

- [ ] Backend server is running (`python app.py`)
- [ ] Frontend is accessible (open `index.html` in browser)
- [ ] No console errors in browser
- [ ] Database contains sample data

## 🎯 Test Scenarios

### 1. Basic Functionality Tests

#### Test 1.1: Greeting Response
**Input:** "Hi"  
**Expected:** Friendly greeting with suggestions  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 1.2: Menu Listing
**Input:** "Show me the menu"  
**Expected:** Complete list of all menu items with categories  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 1.3: Empty Input
**Input:** (Submit empty)  
**Expected:** No action or error message  
**Status:** ⬜ Pass / ⬜ Fail

---

### 2. Menu Query Tests

#### Test 2.1: Category Query
**Input:** "Show me appetizers"  
**Expected:** List of items in Appetizer category  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 2.2: Specific Item Query
**Input:** "Tell me about pizza"  
**Expected:** Detailed information about Margherita Pizza  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 2.3: Fuzzy Matching
**Input:** "piza" (misspelled)  
**Expected:** Still matches "Margherita Pizza"  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 2.4: Non-existent Item
**Input:** "Do you have sushi?"  
**Expected:** Appropriate "not found" message  
**Status:** ⬜ Pass / ⬜ Fail

---

### 3. Price Query Tests

#### Test 3.1: Item Price
**Input:** "How much is the pizza?"  
**Expected:** Price of Margherita Pizza (₹299)  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 3.2: Category Price Range
**Input:** "What's the price of desserts?"  
**Expected:** Price range for dessert items  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 3.3: Multiple Keywords
**Input:** "pizza cost"  
**Expected:** Price information for pizza  
**Status:** ⬜ Pass / ⬜ Fail

---

### 4. Dietary Filter Tests

#### Test 4.1: Vegetarian Filter
**Input:** "Show me vegetarian options"  
**Expected:** Only vegetarian items listed  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 4.2: Vegan Filter
**Input:** "Do you have vegan food?"  
**Expected:** Only vegan items listed  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 4.3: Spice Level Query
**Input:** "What's spicy here?"  
**Expected:** Items with medium/hot spice level  
**Status:** ⬜ Pass / ⬜ Fail

---

### 5. Restaurant Information Tests

#### Test 5.1: Opening Hours
**Input:** "What are your timings?"  
**Expected:** Operating hours displayed  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 5.2: Location
**Input:** "Where are you located?"  
**Expected:** Full address displayed  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 5.3: Contact Information
**Input:** "How can I contact you?"  
**Expected:** Phone and email displayed  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 5.4: General Info
**Input:** "Tell me about the restaurant"  
**Expected:** Complete restaurant information  
**Status:** ⬜ Pass / ⬜ Fail

---

### 6. Intent Recognition Tests

#### Test 6.1: Complex Query
**Input:** "What vegetarian main course items do you have under 300 rupees?"  
**Expected:** Filtered list of vegetarian main courses ≤ ₹300  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 6.2: Ingredient Query
**Input:** "Does chicken tikka contain dairy?"  
**Expected:** Ingredient list with cream mentioned  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 6.3: Ambiguous Query
**Input:** "chicken"  
**Expected:** Shows chicken-related items or asks for clarification  
**Status:** ⬜ Pass / ⬜ Fail

---

### 7. UI/UX Tests

#### Test 7.1: Mobile Responsiveness
**Action:** Resize browser to mobile width  
**Expected:** UI adapts properly, no overflow  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 7.2: Quick Suggestions
**Action:** Click "Show Menu" suggestion button  
**Expected:** Automatically sends query and shows response  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 7.3: Scrolling
**Action:** Send 10+ messages  
**Expected:** Auto-scrolls to latest message  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 7.4: Typing Indicator
**Action:** Send any message  
**Expected:** Typing indicator appears while processing  
**Status:** ⬜ Pass / ⬜ Fail

---

### 8. Error Handling Tests

#### Test 8.1: Backend Offline
**Action:** Stop backend server, send message  
**Expected:** Friendly error message displayed  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 8.2: Invalid API Response
**Action:** Modify API to return invalid JSON  
**Expected:** Error handled gracefully  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 8.3: Long Query
**Input:** (500+ character message)  
**Expected:** Processes without crash  
**Status:** ⬜ Pass / ⬜ Fail

---

### 9. Performance Tests

#### Test 9.1: Response Time
**Action:** Send 5 different queries, measure time  
**Expected:** < 500ms average response time  
**Results:** 
- Query 1: ___ms
- Query 2: ___ms
- Query 3: ___ms
- Query 4: ___ms
- Query 5: ___ms
**Status:** ⬜ Pass / ⬜ Fail

#### Test 9.2: Concurrent Queries
**Action:** Open 2 browser tabs, send messages simultaneously  
**Expected:** Both receive correct responses  
**Status:** ⬜ Pass / ⬜ Fail

#### Test 9.3: Memory Usage
**Action:** Monitor backend RAM usage during operation  
**Expected:** < 300MB RAM  
**Result:** ___MB  
**Status:** ⬜ Pass / ⬜ Fail

---

## 🎬 Demo Script for Presentation

### Opening (1 minute)
1. "Hi! I'm going to demonstrate DineBot, a restaurant chatbot."
2. Show the welcome screen
3. Explain: "It uses NLP to understand customer queries about our menu and services."

### Core Features Demo (3-4 minutes)

**Feature 1: Menu Browsing**
- Click "Show Menu" suggestion
- Show the complete menu with categories
- Say: "Notice how items are organized by category with prices and dietary tags."

**Feature 2: Smart Search**
- Type: "Tell me about pizza"
- Show detailed item information
- Say: "The bot understands natural language and provides complete details."

**Feature 3: Fuzzy Matching**
- Type: "chiken tikka" (intentionally misspelled)
- Show it still finds "Chicken Tikka Masala"
- Say: "It handles typos using fuzzy matching algorithms."

**Feature 4: Dietary Filters**
- Type: "Show me vegetarian options"
- Show filtered results
- Say: "Customers can filter by dietary preferences."

**Feature 5: Restaurant Info**
- Type: "What are your timings?"
- Show operating hours
- Say: "It also handles general restaurant queries."

### Technical Highlights (1 minute)
- "Backend: Python Flask with SQLite database"
- "NLP: spaCy for entity extraction"
- "Lightweight: Runs on budget laptops"
- "Offline: No cloud dependencies"

### Closing (30 seconds)
- "Questions?"
- Be prepared to explain: NLP processing, database schema, API design

---

## 📊 Test Results Summary

**Total Tests:** 27  
**Passed:** ___  
**Failed:** ___  
**Pass Rate:** ___%

**Critical Issues Found:**
1. _________________________
2. _________________________
3. _________________________

**Minor Issues Found:**
1. _________________________
2. _________________________
3. _________________________

---

## 🐛 Common Issues & Solutions

### Issue: "spaCy model not found"
**Solution:** Run `python -m spacy download en_core_web_sm`

### Issue: "CORS error in browser"
**Solution:** Ensure CORS is enabled in Flask (`flask-cors` installed)

### Issue: "Database not initialized"
**Solution:** Delete `restaurant.db` and restart server

### Issue: "Slow response times"
**Solution:** 
1. Check if debug mode is on
2. Reduce SIMILARITY_THRESHOLD if too many fuzzy matches
3. Add database indexes (already included)

### Issue: "Bot doesn't understand query"
**Solution:** 
1. Check NLP patterns in `nlp_service.py`
2. Add more training patterns
3. Adjust confidence thresholds

---

## 💡 Tips for College Project Presentation

1. **Prepare Demo Data:** Have 5-7 pre-written queries ready
2. **Explain Trade-offs:** Discuss why you chose rules over deep learning
3. **Show Code Structure:** Briefly walk through modular architecture
4. **Discuss Scalability:** How would you scale this for production?
5. **Know Your NLP:** Be ready to explain spaCy, intent detection, entity extraction
6. **Performance Metrics:** Know your response times and resource usage
7. **Future Improvements:** Have 2-3 enhancement ideas ready

---

## ✅ Final Checklist Before Demo

- [ ] All tests passing
- [ ] Backend starts without errors
- [ ] Frontend loads correctly
- [ ] Sample queries work as expected
- [ ] UI is responsive on different screen sizes
- [ ] No console errors
- [ ] Code is well-commented
- [ ] README is complete
- [ ] You understand the entire codebase
- [ ] You can explain NLP concepts used
- [ ] You have backup plan if live demo fails (screenshots/video)

---

**Good luck with your project! 🚀**