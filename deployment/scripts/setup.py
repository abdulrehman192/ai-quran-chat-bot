"""Setup script for Quran Chatbot"""

import os
import sys
import subprocess

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["cache", "logs", "data"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✓ {directory}/")

def check_database():
    """Check if database file exists"""
    db_path = "quran.db"
    if os.path.exists(db_path):
        print(f"✅ Database found: {db_path}")
        return True
    else:
        print(f"❌ Database not found: {db_path}")
        print("   Please ensure your Quran database file is in the project root")
        return False

def check_api_key():
    """Check if API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✅ Gemini API key found")
        return True
    else:
        print("❌ Gemini API key not found")
        print("   Please add GEMINI_API_KEY to your .env file")
        return False

def main():
    """Main setup function"""
    print("🌙 Setting up Quran Chatbot...\n")
    
    try:
        install_requirements()
        create_directories()
        
        db_ok = check_database()
        api_ok = check_api_key()
        
        if db_ok and api_ok:
            print("\n✅ Setup completed successfully!")
            print("🚀 You can now run: python main.py")
        else:
            print("\n⚠️ Setup completed with warnings. Please fix the issues above.")
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()