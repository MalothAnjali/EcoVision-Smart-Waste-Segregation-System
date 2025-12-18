"""
Environmental Chatbot Service using Google Gemini API
"""
import google.generativeai as genai
from typing import List, Dict
from app.core.config import settings

class EnvironmentalChatbot:
    """Chatbot for environmental and waste management queries"""
    
    def __init__(self):
        """Initialize Gemini API"""
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY not configured in settings")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash (more generous free tier)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 200,  # Reduced for lower quota usage
            }
        )
        
        # System prompt for environmental focus
        self.system_context = """You are EcoBot, an environmental expert and waste management assistant for EcoVision.

Your expertise includes:
- Waste classification (Recyclable, Non-Recyclable, Hazardous, Organic)
- Recycling best practices
- Environmental conservation
- Sustainability tips
- Waste reduction strategies
- Composting and organic waste
- Hazardous waste disposal
- Climate change and carbon footprint
- Circular economy
- Green living tips

Guidelines:
- Be friendly, encouraging, and educational
- Use emojis occasionally to be engaging 🌱♻️🌍
- Keep responses concise (2-4 paragraphs max)
- Provide actionable advice when possible
- If asked about non-environmental topics, politely redirect to environmental matters
- When discussing waste, reference the 4 categories: Recyclable, Non-Recyclable, Hazardous, Organic
- Encourage sustainable practices

Always be accurate, helpful, and inspiring about environmental topics!"""
    
    def chat(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Send a message to the chatbot and get a response
        
        Args:
            message: User's message
            chat_history: Not used (kept for API compatibility)
        
        Returns:
            Chatbot's response
        """
        try:
            # Simple prompt with context hint
            prompt = f"""You are EcoBot, an environmental assistant.

Question: {message}

Answer briefly (under 80 words)."""
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_response(message)
        
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Chatbot error: {e}")
            
            # Check if quota/rate limit error
            if "429" in error_msg or "quota" in error_msg or "rate" in error_msg:
                return self._get_fallback_response(message)
            else:
                return "I'm having trouble connecting right now. Please try again in a moment."
    
    def _get_fallback_response(self, message: str) -> str:
        """Provide fallback responses when API is unavailable"""
        msg_lower = message.lower()
        
        # Recycling questions
        if any(word in msg_lower for word in ['recycle', 'recyclable', 'recycling']):
            if 'plastic' in msg_lower:
                return "♻️ To recycle plastic: Empty and rinse containers, remove caps, check for recycling numbers (#1-#7), and place in your recycling bin. Most communities accept #1 (PET) and #2 (HDPE) plastics."
            elif 'paper' in msg_lower or 'cardboard' in msg_lower:
                return "📄 Paper and cardboard are highly recyclable! Keep them dry, flatten boxes, remove plastic tape/labels, and place in recycling. Pizza boxes with grease should go to compost or trash."
            elif 'glass' in msg_lower:
                return "🍾 Glass is endlessly recyclable! Rinse containers, remove caps/lids, and place in recycling. Separate by color if required in your area. Broken glass should be wrapped safely."
            else:
                return "♻️ Check if items have recycling symbols, rinse containers, separate materials, and follow your local recycling guidelines. When in doubt, check with your municipality!"
        
        # Composting questions
        elif any(word in msg_lower for word in ['compost', 'organic', 'food waste']):
            return "🌱 Composting turns organic waste into nutrient-rich soil! Add: fruit/veggie scraps, coffee grounds, eggshells, yard waste. Avoid: meat, dairy, oils, pet waste. Keep it moist and turn regularly!"
        
        # Hazardous waste
        elif any(word in msg_lower for word in ['hazardous', 'battery', 'electronic', 'chemical']):
            return "⚠️ Hazardous waste (batteries, electronics, chemicals, paint) requires special disposal. Never put in regular trash! Take to designated collection centers or hazardous waste events in your community."
        
        # Waste reduction
        elif any(word in msg_lower for word in ['reduce', 'less waste', 'zero waste']):
            return "🌍 Reduce waste by: using reusable bags/bottles/containers, buying in bulk, choosing products with less packaging, repairing items, and saying no to single-use plastics. Start small!"
        
        # Sustainability general
        elif any(word in msg_lower for word in ['sustainable', 'sustainability', 'eco-friendly', 'green']):
            return "🌿 Live sustainably by: reducing consumption, reusing items, recycling properly, composting, conserving energy/water, choosing eco-friendly products, and supporting local/sustainable businesses."
        
        # Climate/environment
        elif any(word in msg_lower for word in ['climate', 'environment', 'carbon', 'footprint']):
            return "🌍 Reduce your environmental impact: minimize waste, use public transport/bike, conserve energy, eat less meat, support renewable energy, and choose sustainable products. Every action counts!"
        
        # Default helpful response
        else:
            return "🌱 I'm here to help with waste management, recycling, composting, and sustainability! Ask me about: how to recycle materials, composting tips, reducing waste, or eco-friendly living."
    
    def get_quick_tip(self) -> str:
        """Get a random environmental tip"""
        try:
            prompt = "Give one quick environmental tip about waste management or recycling in 2 sentences."
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "♻️ Remember: Reduce, Reuse, Recycle! Small actions make a big difference."
        
        except Exception as e:
            print(f"Quick tip error: {e}")
            return "🌱 Every sustainable choice counts. Start small, think big!"

# Global chatbot instance
_chatbot_instance = None

def get_chatbot() -> EnvironmentalChatbot:
    """Get or create chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = EnvironmentalChatbot()
    return _chatbot_instance