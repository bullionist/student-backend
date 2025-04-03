import httpx
from app.config import settings
from typing import Dict, Any, Optional, List
from loguru import logger
import json

class GroqService:
    """Service to interact with Groq API for NLP processing"""
    
    GROQ_API_URL = settings.GROQ_API_URL
    GROQ_API_KEY = settings.GROQ_API_KEY
    
    @staticmethod
    async def extract_student_details(input_text: str) -> Dict[str, Any]:
        """
        Extract structured student details from free-form text input.
        
        Args:
            input_text: The student's free-form text input
            
        Returns:
            Dictionary containing extracted structured information
        """
        try:
            headers = {
                "Authorization": f"Bearer {GroqService.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Define the prompt for information extraction
            prompt = f"""
            Extract the following information from the student's input:
            - Academic background (degrees, qualifications, institutions)
            - Preferred location for study
            - Field of study or interest
            - Exam scores (with name and score)
            - Additional preferences (study mode, budget, etc.)
            
            Format the response as a JSON object with these keys: 
            academic_background, preferred_location, field_of_study, exam_scores, additional_preferences.
            
            For exam_scores, use an array of objects with exam_name and score properties.
            For additional_preferences, create a structured object.
            
            Student Input: {input_text}
            
            JSON Response:
            """
            
            # Request payload
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You are an AI assistant that extracts structured information from student inputs."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{GroqService.GROQ_API_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    return {
                        "error": f"API error: {response.status_code}",
                        "raw_input": input_text
                    }
                
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                # Try to parse the JSON from the response
                try:
                    # Find JSON content - sometimes the model wraps it in markdown or adds text
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > 0:
                        json_content = content[json_start:json_end]
                        extracted_data = json.loads(json_content)
                    else:
                        # Fall back to the entire content if JSON markers not found
                        extracted_data = json.loads(content)
                        
                    return extracted_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Groq response: {str(e)}")
                    return {
                        "error": "Failed to parse structured data",
                        "raw_input": input_text,
                        "raw_output": content
                    }
                
        except Exception as e:
            logger.error(f"Error in extract_student_details: {str(e)}")
            return {
                "error": f"Service error: {str(e)}",
                "raw_input": input_text
            }
