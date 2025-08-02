# test_workers.py
import asyncio
from agents.workers.learning_worker import LearningWorker
from agents.workers.verse_worker import VerseWorker

async def test_workers():
    # Test Learning Worker
    learning_worker = LearningWorker()
    response = await learning_worker.process_request(
        "Teach me about the five pillars of Islam", 
        "en", 
        {}
    )
    print("Learning Worker Response:", response['content'][:100])
    
    # Test Verse Worker
    verse_worker = VerseWorker()
    response = await verse_worker.process_request(
        "Show me verses about patience", 
        "en", 
        {}
    )
    print("Verse Worker Response:", response['content'][:100])

if __name__ == "__main__":
    asyncio.run(test_workers())