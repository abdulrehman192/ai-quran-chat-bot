# test_db.py
from database.queries import QuranQueries

def test_database():
    db = QuranQueries()
    
    # Test each table
    verses = db.search_verses("patience")
    print(f"Found {len(verses)} verses")
    
    surahs = db.get_all_surahs()
    print(f"Found {len(surahs)} surahs")
    
    names = db.get_allah_names()
    print(f"Found {len(names)} Allah's names")
    
    duas = db.search_duas()
    print(f"Found {len(duas)} duas")

if __name__ == "__main__":
    test_database()