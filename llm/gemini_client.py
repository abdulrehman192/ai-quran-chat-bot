import google.generativeai as genai
from config.settings import Settings
from config.prompts import SYSTEM_PROMPTS
from llm.prompt_templates import PromptTemplates
import logging

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=Settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name ='gemini-2.0-flash')
        self.logger = logging.getLogger(__name__)
    
    async def generate_response(self, prompt: str, context: str = "", language: str = "en", 
                              response_type: str = "general") -> str:
        """Generate response using Gemini with proper context and templates"""
        try:
            # Get appropriate template
            template = PromptTemplates.get_template(response_type, language)
            
            # If no database context is provided, indicate it in the prompt
            if not context or context.strip() == "":
                context = self._get_no_database_context_message(language)
            
            # Format the template with context and query
            if template:
                formatted_prompt = template.format(context=context, query=prompt)
            else:
                # Fallback formatting
                system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
                formatted_prompt = f"""
                {system_prompt}
                
                Context: {context}
                
                User question: {prompt}
                
                Please provide a respectful, helpful response in {language} language.
                """
            
            response = self.model.generate_content(formatted_prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._get_error_message(language)
    
    def _get_no_database_context_message(self, language: str) -> str:
        """Return appropriate message when no database context is available"""
        messages = {
            "en": """No specific verses or references were found in the database for this query. 
                     Please provide guidance based on general Islamic knowledge and principles. 
                     Mention that for specific Quranic references, the user may want to consult 
                     Islamic scholars or authentic Quranic resources.""",
            
            "ur": """اس سوال کے لیے ڈیٹابیس میں کوئی مخصوص آیات یا حوالے نہیں ملے۔ 
                     براہ کرم عمومی اسلامی علم اور اصولوں کی بنیاد پر رہنمائی فراہم کریں۔ 
                     یہ بتائیں کہ مخصوص قرآنی حوالوں کے لیے صارف علماء کرام یا مستند قرآنی وسائل سے رجوع کر سکتے ہیں۔""",
            
            "ar": """لم يتم العثور على آيات أو مراجع محددة في قاعدة البيانات لهذا الاستعلام. 
                     يرجى تقديم التوجيه بناء على المعرفة والمبادئ الإسلامية العامة. 
                     اذكر أنه للحصول على مراجع قرآنية محددة، قد يرغب المستخدم في استشارة العلماء أو المصادر القرآنية الموثقة."""
        }
        
        return messages.get(language, messages["en"])
    
    def _get_error_message(self, language: str) -> str:
        """Return appropriate error message based on language"""
        messages = {
            "en": "I apologize, but I'm having trouble processing your request. Please try again.",
            "ur": "معذرت، آپ کی درخواست پر عمل کرنے میں مسئلہ ہو رہا ہے۔ براہ کرم دوبارہ کوشش کریں۔",
            "ar": "أعتذر، لكنني أواجه مشكلة في معالجة طلبك. يرجى المحاولة مرة أخرى."
        }
        return messages.get(language, messages["en"])