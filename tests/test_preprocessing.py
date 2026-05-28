from src.intent_detection import process_user_query


test_queries = [
    "Hello",
    "Hi",
    "Thank you!",
    "Who are you?",
    "Can you help me?",
    "Bye",
    "Where can I reset my Moodle password?",
    "How do I register for courses?",
    "Where is the bus stop?",
    "This is my question about Moodle",
    "I want to know the academic calendar"
]


for query in test_queries:
    result = process_user_query(query)

    print("=" * 60)
    print("Original Query:", result["original_query"])
    print("Cleaned Query:", result["cleaned_query"])
    print("Is Rule Based:", result["is_rule_based"])
    print("Intent:", result["intent"])
    print("Route:", result["route"])
    print("Response:", result["response"])