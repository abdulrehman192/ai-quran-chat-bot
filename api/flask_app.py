from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from main import QuranChatbot
from utils.formatters import ResponseFormatter

app = Flask(__name__)
CORS(app)  # Enable CORS for web frontend

# Initialize chatbot
chatbot = QuranChatbot()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Quran Chatbot API"})

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        
        # Process query asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(chatbot.process_single_query(query))
        loop.close()
        
        # Format for API
        formatted_response = ResponseFormatter.format_for_api(response)
        
        return jsonify(formatted_response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sources/<source_type>', methods=['GET'])
def get_sources(source_type):
    """Get available sources by type"""
    try:
        if source_type not in ['verses', 'duas', 'names']:
            return jsonify({"error": "Invalid source type"}), 400
        
        # This would fetch from database
        # Implementation depends on specific requirements
        return jsonify({"message": f"List of {source_type} would be returned here"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)