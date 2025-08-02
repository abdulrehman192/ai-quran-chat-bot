import asyncio
from main import QuranChatbot

async def test_english_queries():
    """Test how the system handles English queries with Arabic/Urdu database"""
    
    chatbot = QuranChatbot()
    
    # Test queries that demonstrate English handling
    test_cases = [
        {
            "query": "Show me verses about patience",
            "expected_behavior": "Search for Arabic terms related to patience (صبر), provide Arabic verses with explanations"
        },
        {
            "query": "I need guidance about forgiveness", 
            "expected_behavior": "Search for forgiveness-related Arabic terms (غفر, توبة), provide guidance"
        },
        {
            "query": "What does the Quran say about charity?",
            "expected_behavior": "Search for charity-related terms (زكاة, صدقة), explain Islamic charity"
        },
        {
            "query": "Tell me about Allah's mercy",
            "expected_behavior": "Find Allah's names related to mercy (الرحمن, الرحيم), explain the concept"
        },
        {
            "query": "How should I pray?",
            "expected_behavior": "Provide general Islamic guidance about prayer (صلاة) with LLM knowledge"
        },
        {
            "query": "I'm feeling anxious and need help",
            "expected_behavior": "Search for peace/comfort verses, provide spiritual guidance"
        }
    ]
    
    print("🧪 Testing English Query Handling\n" + "="*50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['query']}")
        print(f"Expected: {test_case['expected_behavior']}")
        print("-" * 40)
        
        try:
            response = await chatbot.process_single_query(test_case['query'])
            
            print(f"✅ Response Generated:")
            print(f"   Worker: {response.get('worker', 'Unknown')}")
            print(f"   Language: {response.get('language', 'Unknown')}")
            print(f"   Has DB Results: {response.get('has_database_results', False)}")
            print(f"   Sources Found: {len(response.get('sources', []))}")
            print(f"   Content: {response['content'][:200]}...")
            
            if response.get('disclaimer'):
                print(f"   Disclaimer: {response['disclaimer'][:100]}...")
            
            # Show sources if any
            sources = response.get('sources', [])
            if sources:
                print(f"   📚 Sources:")
                for j, source in enumerate(sources[:3], 1):
                    if source['type'] == 'verse':
                        print(f"      {j}. Verse: Surah {source['surah']}, Verse {source['verse_number']}")
                    elif source['type'] == 'allah_name':
                        print(f"      {j}. Name: {source['arabic']} ({source['english']})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()