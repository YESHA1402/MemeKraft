"""
Bollywood Cloud Computing Book Generator
Handles content generation using LLM
"""
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
from typing import List, Dict

# Language-specific system messages
LANGUAGE_CONFIGS = {
    "english": {
        "name": "English",
        "system_msg": """You are a Bollywood-style professor who teaches Cloud Computing using memes, jokes, and filmy dialogues while maintaining 100% academic accuracy. Generate content in English."""
    },
    "hindi": {
        "name": "Hindi (हिंदी)",
        "system_msg": """आप एक बॉलीवुड स्टाइल के प्रोफेसर हैं जो memes, jokes और filmy dialogues का use करके Cloud Computing सिखाते हैं। 100% academic accuracy बनाए रखें। Generate content in Hindi (Devanagari script)."""
    },
    "gujarati": {
        "name": "Gujarati (ગુજરાતી)",
        "system_msg": """તમે બોલીવુડ સ્ટાઇલના પ્રોફેસર છો જે memes, jokes અને filmy dialogues વાપરીને Cloud Computing શીખવો છો। 100% academic accuracy જાળવો. Generate content in Gujarati."""
    },
    "marathi": {
        "name": "Marathi (मराठी)",
        "system_msg": """तुम्ही बॉलिवूड स्टाईलचे प्राध्यापक आहात जे memes, jokes आणि filmy dialogues वापरून Cloud Computing शिकवता. 100% academic accuracy ठेवा. Generate content in Marathi."""
    },
    "tamil": {
        "name": "Tamil (தமிழ்)",
        "system_msg": """நீங்கள் பாலிவுட் ஸ்டைல் பேராசிரியர், memes, jokes மற்றும் filmy dialogues பயன்படுத்தி Cloud Computing கற்பிக்கிறீர்கள். 100% academic accuracy பராமரிக்கவும். Generate content in Tamil."""
    },
    "telugu": {
        "name": "Telugu (తెలుగు)",
        "system_msg": """మీరు బాలీవుడ్ స్టైల్ ప్రొఫెసర్, memes, jokes మరియు filmy dialogues ఉపయోగించి Cloud Computing నేర్పుతున్నారు. 100% academic accuracy నిర్వహించండి. Generate content in Telugu."""
    },
    "bengali": {
        "name": "Bengali (বাংলা)",
        "system_msg": """আপনি একজন বলিউড স্টাইলের প্রফেসর যিনি memes, jokes এবং filmy dialogues ব্যবহার করে Cloud Computing শেখান। 100% academic accuracy বজায় রাখুন। Generate content in Bengali."""
    },
    "punjabi": {
        "name": "Punjabi (ਪੰਜਾਬੀ)",
        "system_msg": """ਤੁਸੀਂ ਬਾਲੀਵੁੱਡ ਸਟਾਈਲ ਦੇ ਪ੍ਰੋਫੈਸਰ ਹੋ ਜੋ memes, jokes ਅਤੇ filmy dialogues ਵਰਤ ਕੇ Cloud Computing ਸਿਖਾਉਂਦੇ ਹੋ। 100% academic accuracy ਰੱਖੋ। Generate content in Punjabi."""
    },
    "kannada": {
        "name": "Kannada (ಕನ್ನಡ)",
        "system_msg": """ನೀವು ಬಾಲಿವುಡ್ ಸ್ಟೈಲ್ ಪ್ರೊಫೆಸರ್, memes, jokes ಮತ್ತು filmy dialogues ಬಳಸಿ Cloud Computing ಕಲಿಸುತ್ತೀರಿ. 100% academic accuracy ನಿರ್ವಹಿಸಿ. Generate content in Kannada."""
    },
    "malayalam": {
        "name": "Malayalam (മലയാളം)",
        "system_msg": """നിങ്ങൾ ബോളിവുഡ് സ്റ്റൈൽ പ്രൊഫസർ ആണ്, memes, jokes, filmy dialogues ഉപയോഗിച്ച് Cloud Computing പഠിപ്പിക്കുന്നു. 100% academic accuracy പാലിക്കുക. Generate content in Malayalam."""
    }
}

class BollywoodBookGenerator:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
    
    def _get_chat_instance(self, language: str, session_id: str):
        """Create LLM chat instance with language-specific system message"""
        lang_config = LANGUAGE_CONFIGS.get(language.lower(), LANGUAGE_CONFIGS["english"])
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=lang_config["system_msg"]
        )
        # Use GPT-4o for best creative content generation
        chat.with_model("openai", "gpt-4o")
        return chat
    
    async def generate_table_of_contents(self, language: str, user_content: str = "") -> str:
        """Generate table of contents based on syllabus"""
        chat = self._get_chat_instance(language, f"toc_{language}")
        
        prompt = f"""Generate a detailed Table of Contents for a 60-page Bollywood-style Cloud Computing book.
        
Base syllabus topics (adapt as needed):
1. Introduction to Cloud Computing
2. Virtualization & Hypervisors
3. Virtual Machines
4. Containers & Docker
5. Service Models (IaaS, PaaS, SaaS)
6. Deployment Models
7. Cloud Storage
8. Cloud Networking
9. Load Balancing
10. Auto-Scaling & Elasticity
11. Cloud Security
12. Fault Tolerance & Disaster Recovery
13. Serverless Computing
14. Edge & Fog Computing
15. Cloud Providers (AWS, Azure, GCP)
16. Real-world Case Studies
17. Pricing & SLAs

{f'Additional context from user materials: {user_content[:500]}' if user_content else ''}

Generate a structured TOC with chapter numbers, topics, and page numbers (for 60-page book).
Make it fun and Bollywood-themed but academically complete."""

        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        return response
    
    async def generate_chapter(
        self, 
        chapter_num: int, 
        chapter_title: str, 
        language: str,
        user_content: str = "",
        pages: int = 5
    ) -> str:
        """Generate a single chapter with multiple pages"""
        chat = self._get_chat_instance(language, f"chapter_{chapter_num}_{language}")
        
        prompt = f"""Generate Chapter {chapter_num}: {chapter_title}

This chapter should have approximately {pages} pages in Bollywood comic-style format.

**CRITICAL FORMAT FOR EACH PAGE:**

Page [Number]
━━━━━━━━━━━━━━━━━━━━━
📖 Topic: [Specific topic name]

🎬 Bollywood Meme Prompt:
[Describe the meme - e.g., "Raju from Hera Pheri shocked face when seeing cloud bills"]

🎭 Comic Panel Description:
[Describe the scene - characters, setting, visual composition]

💬 Dialogue:
[Character 1]: "[Funny Bollywood-style dialogue]"
[Character 2]: "[Response with cloud computing reference]"

📚 Academic Explanation:
[Clear, accurate technical explanation of the cloud computing concept]

🎯 Key Points:
• [Important point 1]
• [Important point 2]
• [Important point 3]

😄 Punchline/Joke:
[Funny ending related to the topic]

━━━━━━━━━━━━━━━━━━━━━

{f'Reference material: {user_content[:300]}' if user_content else ''}

**REQUIREMENTS:**
1. Use simple, student-friendly language
2. Include Bollywood movie references (Hera Pheri, 3 Idiots, Sholay, DDLJ, etc.)
3. Make technical concepts relatable through funny analogies
4. Maintain 100% technical accuracy
5. Each page should teach one specific concept
6. Use emojis for visual appeal
7. Make it engaging and memorable

Generate all {pages} pages now."""

        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        return response
    
    async def generate_full_book(
        self,
        language: str,
        user_content: str = "",
        total_pages: int = 60
    ) -> Dict[str, str]:
        """Generate complete book with all chapters"""
        result = {
            "title_page": "",
            "toc": "",
            "chapters": []
        }
        
        # Generate title page
        chat = self._get_chat_instance(language, f"title_{language}")
        title_prompt = f"""Create a Bollywood-style title page for the Cloud Computing book in {language}.

Include:
- 🎬 Main Title (creative and filmy)
- 📚 Subtitle
- 💫 Tagline (Bollywood dialogue style)
- 🎭 Visual description for cover design

Make it exciting and appealing to B.Tech CSE students!"""
        
        title_msg = UserMessage(text=title_prompt)
        result["title_page"] = await chat.send_message(title_msg)
        
        # Generate TOC
        result["toc"] = await self.generate_table_of_contents(language, user_content)
        
        # Define chapters (can be customized based on user content)
        chapters = [
            {"num": 1, "title": "Introduction to Cloud Computing", "pages": 5},
            {"num": 2, "title": "Virtualization Magic", "pages": 4},
            {"num": 3, "title": "Virtual Machines - The Copy Machine", "pages": 4},
            {"num": 4, "title": "Containers: Docker Ka Jadoo", "pages": 5},
            {"num": 5, "title": "Service Models: IaaS, PaaS, SaaS", "pages": 5},
            {"num": 6, "title": "Deployment Models", "pages": 4},
            {"num": 7, "title": "Cloud Storage", "pages": 4},
            {"num": 8, "title": "Cloud Networking", "pages": 4},
            {"num": 9, "title": "Load Balancing & Auto-Scaling", "pages": 5},
            {"num": 10, "title": "Cloud Security", "pages": 5},
            {"num": 11, "title": "Serverless Computing", "pages": 4},
            {"num": 12, "title": "Cloud Providers (AWS, Azure, GCP)", "pages": 6},
            {"num": 13, "title": "Real-World Case Studies", "pages": 5},
        ]
        
        # Generate each chapter
        for chapter in chapters:
            chapter_content = await self.generate_chapter(
                chapter["num"],
                chapter["title"],
                language,
                user_content,
                chapter["pages"]
            )
            result["chapters"].append({
                "number": chapter["num"],
                "title": chapter["title"],
                "content": chapter_content
            })
        
        return result
