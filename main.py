import asyncio
import logging
import gradio as gr
from typing import Dict, Any, List, Tuple
from agents.orchestrator import QuranChatbotOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class QuranChatbotUI:
    """Gradio UI for Quran Chatbot"""
    
    def __init__(self):
        self.orchestrator = QuranChatbotOrchestrator()
        self.logger = logging.getLogger(__name__)
        
    async def process_message(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """Process user message and return response with updated history"""
        try:
            if not message.strip():
                return "", history
            
            # Process query using orchestrator
            response = await self.orchestrator.process_query(message)
            
            # Format response
            formatted_response = self._format_response(response)
            
            # Update history
            history.append((message, formatted_response))
            
            return "", history
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            error_response = "Sorry, something went wrong. Please try again. 🤲"
            history.append((message, error_response))
            return "", history
    
    def _format_response(self, response: Dict[str, Any]) -> str:
        """Format the response for display in Gradio"""
        content = response.get('content', '')
        worker = response.get('worker', 'Unknown')
        sources = response.get('sources', [])
        
        # Start with main content
        formatted = f"**🤖 Response from {worker}:**\n\n{content}"
        
        # Add sources if available
        if sources:
            formatted += "\n\n**📚 Sources:**\n"
            for i, source in enumerate(sources[:3], 1):  # Limit to 3 sources
                if source['type'] == 'verse':
                    formatted += f"{i}. Surah {source['surah']}, Verse {source['verse_number']}\n"
                elif source['type'] == 'allah_name':
                    formatted += f"{i}. Allah's Name: {source['arabic']} ({source['english']})\n"
                elif source['type'] == 'dua':
                    formatted += f"{i}. Dua from Surah {source['surah']}, Verse {source['verse']}\n"
        
        return formatted
    
    def create_interface(self):
        """Create and configure Gradio interface"""
        
        # Custom CSS for Islamic theme
        css = """
        .gradio-container {
            font-family: 'Arial', sans-serif;
        }
        .chat-message {
            padding: 10px;
            margin: 5px;
            border-radius: 10px;
        }
        .header {
            text-align: center;
            background: linear-gradient(45deg, #2E8B57, #228B22);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        """
        
        with gr.Blocks(css=css, title="🌙 Quran Chatbot", theme=gr.themes.Soft()) as interface:
            
            # Header
            gr.HTML("""
            <div class="header">
                <h1>🌙 Quran Chatbot 🌙</h1>
                <p>Ask me about Quranic verses, duas, Allah's names, or seek spiritual guidance</p>
                <p><em>Supported languages: English, Urdu, Arabic</em></p>
            </div>
            """)
            
            # Chat interface
            chatbot = gr.Chatbot(
                label="💬 Chat with Quran Bot",
                height=500,
                bubble_full_width=False,
                show_label=True,
                container=True,
                avatar_images=("👤", "🤖")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Message",
                    placeholder="Ask about Quranic verses, duas, Allah's names, or seek guidance...",
                    container=False,
                    scale=4
                )
                submit_btn = gr.Button("Send 📤", variant="primary", scale=1)
            
            # Example questions
            with gr.Row():
                gr.Examples(
                    examples=[
                        ["Tell me about Surah Al-Fatiha"],
                        ["What are the 99 names of Allah?"],
                        ["Share a dua for protection"],
                        ["Explain the meaning of Bismillah"],
                        ["Tell me about prayer times"],
                        ["What does the Quran say about patience?"]
                    ],
                    inputs=msg,
                    label="💡 Example Questions"
                )
            
            # Information section
            with gr.Accordion("ℹ️ About", open=False):
                gr.Markdown("""
                ### Features:
                - **Quranic Verses**: Search and explore verses with translations
                - **Allah's Names**: Learn about the 99 beautiful names of Allah
                - **Duas**: Access authentic Islamic prayers and supplications  
                - **Spiritual Guidance**: Get Islamic guidance on various topics
                - **Multi-language**: Supports English, Urdu, and Arabic
                
                ### How to use:
                1. Type your question in the message box
                2. Click "Send" or press Enter
                3. The chatbot will provide relevant Islamic content with sources
                
                *May Allah bless your learning journey! 🤲*
                """)
            
            # Handle message submission
            def submit_message(message, history):
                # Run async function in event loop
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    _, updated_history = loop.run_until_complete(
                        self.process_message(message, history)
                    )
                    loop.close()
                    return "", updated_history
                except Exception as e:
                    self.logger.error(f"Error in submit_message: {e}")
                    history.append((message, "Sorry, an error occurred. Please try again."))
                    return "", history
            
            # Event handlers
            msg.submit(submit_message, [msg, chatbot], [msg, chatbot])
            submit_btn.click(submit_message, [msg, chatbot], [msg, chatbot])
            
            # Clear chat
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
            clear_btn.click(lambda: [], outputs=chatbot)
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface"""
        interface = self.create_interface()
        
        print("🌙 Starting Quran Chatbot UI...")
        
        interface.launch()

# Updated main.py integration
class QuranChatbot:
    """Main chatbot application with both CLI and UI support"""
    
    def __init__(self):
        self.orchestrator = QuranChatbotOrchestrator()
        self.logger = logging.getLogger(__name__)
        self.session_history = []
        self.ui = QuranChatbotUI()

    def _display_response(self, response: Dict[str, Any]):
        """Display formatted response to user"""
        print(f"\n🤖 Chatbot ({response.get('worker', 'Unknown')}):")
        print(f"{response['content']}")
        
        # Display sources if available
        sources = response.get('sources', [])
        if sources:
            print(f"\n📚 Sources:")
            for i, source in enumerate(sources[:3], 1):  # Limit to 3 sources
                if source['type'] == 'verse':
                    print(f"  {i}. Surah {source['surah']}, Verse {source['verse_number']}")
                elif source['type'] == 'allah_name':
                    print(f"  {i}. Allah's Name: {source['arabic']} ({source['english']})")
                elif source['type'] == 'dua':
                    print(f"  {i}. Dua from Surah {source['surah']}, Verse {source['verse']}")
        
        print("-" * 50)
    
    async def process_single_query(self, query: str) -> Dict[str, Any]:
        """Process a single query (useful for API integration)"""
        return await self.orchestrator.process_query(query)
    
    def start_ui(self, **kwargs):
        """Start the Gradio UI"""
        self.ui.launch(**kwargs)

# Usage example
async def main():
    """Main function with CLI argument support"""
    import sys
    
    chatbot = QuranChatbot()
    chatbot.start_ui()

if __name__ == "__main__":
    asyncio.run(main())