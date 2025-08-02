import asyncio
from main import QuranChatbot

async def test_chatbot():
    """Test function to demonstrate different types of queries"""
    chatbot = QuranChatbot()
    
    test_queries = [
        "Show me verses about patience",
        "I need a dua for success",
        "Tell me about Allah's name Ar-Rahman",
        "I'm feeling anxious, please guide me",
        "What does Quran say about charity?",
        "صبر کے بارے میں آیات دکھائیں",  # Urdu
    ]
    
    print("🧪 Testing Quran Chatbot with sample queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        response = await chatbot.process_single_query(query)
        print(f"Response: {response['content'][:100]}...")
        print(f"Worker: {response.get('worker', 'Unknown')}")
        print(f"Language: {response.get('language', 'Unknown')}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_chatbot())