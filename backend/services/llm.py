import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Using the requested model
MODEL_NAME = "gemini-2.5-flash-lite" 
# Backup if 2.5 is not yet public/stable in the SDK, but sticking to requirements.

class LLMService:
    def __init__(self):
        if not GENAI_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME, 
            google_api_key=GENAI_API_KEY, 
            temperature=0.7,
            convert_system_message_to_human=True
        )

    def generate_quiz_data(self, text_content: str, difficulty: str = "random"):
        # --- Prompt 1: Quiz & Entities ---
        
        difficulty_instruction = ""
        if difficulty != "random":
             difficulty_instruction = f"All questions MUST be of '{difficulty}' difficulty."
        else:
             difficulty_instruction = "Questions should vary in difficulty (easy, medium, hard)."

        quiz_template = """
        You are an expert educational content generator. Analyze the provided text from a Wikipedia article and generate a structured quiz and entity list.
        
        Article Text:
        {text}

        Requirements:
        1. Identify key entities mentioned in the text: People, Organizations, Locations.
        2. Generate 5 to 10 multiple-choice questions based ONLY on the provided text.
        3. Each question must have:
           - Clear question text
           - Exactly 4 options (A, B, C, D)
           - Correct answer (must match one option exactly)
           - Explanation (2-3 sentences, grounded in text)
           - Difficulty attribute ("easy", "medium", "hard")
        4. {difficulty_instruction}
        5. Questions should cover different sections.
        6. JSON Output ONLY. Use 'people', 'organizations', 'locations' keys for entities.
        
        Output Format:
        {{
            "key_entities": {{
                "people": ["name1", ...],
                "organizations": ["org1", ...],
                "locations": ["loc1", ...]
            }},
            "quiz": [
                {{
                    "question": "...",
                    "options": ["...", "...", "...", "..."],
                    "answer": "...",
                    "difficulty": "...",
                    "explanation": "..."
                }},
                ...
            ]
        }}
        """
        
        # --- Prompt 2: Related Topics ---
        topics_template = """
        Based on the provided article text, suggest 3 to 7 related Wikipedia topics for further reading.
        
        Article Text:
        {text}
        
        Requirements:
        1. Topics must be relevant.
        2. Return ONLY a JSON array of strings.
        
        Output Format:
        ["Topic 1", "Topic 2", ...]
        """

        prompt_quiz = PromptTemplate.from_template(quiz_template)
        prompt_topics = PromptTemplate.from_template(topics_template)
        
        chain_quiz = prompt_quiz | self.llm
        chain_topics = prompt_topics | self.llm

        try:
            # We trim text to avoid context limit if necessary
            truncated_text = text_content[:30000] 
            
            res_quiz = chain_quiz.invoke({
                "text": truncated_text,
                "difficulty_instruction": difficulty_instruction
            })
            res_topics = chain_topics.invoke({"text": truncated_text})

            # Parse JSON
            # Clean markdown code blocks if present
            quiz_str = res_quiz.content.replace("```json", "").replace("```", "").strip()
            topics_str = res_topics.content.replace("```json", "").replace("```", "").strip()

            try:
                quiz_data = json.loads(quiz_str)
            except json.JSONDecodeError:
                # Basic recovery fallback or re-raise
                print(f"JSON Decode Error in Quiz: {quiz_str}")
                quiz_data = {"key_entities": {"people":[], "organizations":[], "locations":[]}, "quiz":[]}

            try:
                topics_data = json.loads(topics_str)
            except json.JSONDecodeError:
                print(f"JSON Decode Error in Topics: {topics_str}")
                topics_data = []

            return {
                "key_entities": quiz_data.get("key_entities", {"people":[], "organizations":[], "locations":[]}),
                "quiz": quiz_data.get("quiz", []),
                "related_topics": topics_data
            }

        except Exception as e:
            print(f"LLM Error: {e}")
            raise e
