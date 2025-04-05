import httpx
from app.config import settings
from typing import Dict, Any, Optional, List
from loguru import logger
import json
from app.models.program import ProgramModel

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
            - Academic background (current education level, subjects, grades)
            - Preferred location for study
            - Field of study interest
            - Exam scores (if mentioned)
            - Additional preferences (if any)
            
            Student input: {input_text}
            
            Return the information in JSON format with the following structure:
            {{
                "academic_background": {{
                    "current_education": "string",
                    "subjects": ["string"],
                    "grades": "string"
                }},
                "preferred_location": "string",
                "field_of_study": "string",
                "exam_scores": {{
                    "exam_name": "score"
                }},
                "additional_preferences": {{
                    "preference_key": "preference_value"
                }}
            }}
            
            Only include fields that are explicitly mentioned in the input.
            """
            
            # Request payload
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information from text."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 1024,
                "top_p": 1,
                "stream": False
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
            logger.error(f"Error extracting student details: {str(e)}")
            return {
                "error": str(e),
                "raw_input": input_text
            }
    
    @staticmethod
    async def generate_course_recommendations(student_data: Dict[str, Any], available_programs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate personalized course recommendations based on student profile and available programs.
        
        Args:
            student_data: The student's profile data
            available_programs: List of available educational programs
            
        Returns:
            Dictionary containing recommendations and explanation
        """
        try:
            headers = {
                "Authorization": f"Bearer {GroqService.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Format student data for the prompt
            student_info = {
                "academic_background": student_data.get("academic_background", "Not specified"),
                "preferred_location": student_data.get("preferred_location", "Not specified"),
                "field_of_study": student_data.get("field_of_study", "Not specified"),
                "exam_scores": student_data.get("exam_scores", []),
                "additional_preferences": student_data.get("additional_preferences", {})
            }
            
            # Format programs data for the prompt
            programs_info = []
            for program in available_programs:
                programs_info.append({
                    "id": program.get("id", ""),
                    "program_title": program.get("program_title", ""),
                    "institution": program.get("institution", ""),
                    "program_overview": program.get("program_overview", ""),
                    "eligibility_criteria": program.get("eligibility_criteria", {}),
                    "duration": program.get("duration", ""),
                    "fees": program.get("fees", ""),
                    "mode_of_delivery": program.get("mode_of_delivery", ""),
                    "location": program.get("location", ""),
                    "curriculum": {
                        "core_modules": [m.get("name", "") for m in program.get("curriculum", {}).get("core_modules", [])]
                    }
                })
            
            # Define the prompt for course recommendations
            prompt = f"""
            Based on the student's profile and available programs, generate personalized recommendations.
            
            Student Profile:
            {json.dumps(student_info, indent=2)}
            
            Available Programs:
            {json.dumps(programs_info, indent=2)}
            
            Generate recommendations in the following JSON format:
            {{
                "recommended_programs": [
                    {{
                        "program_id": "string",
                        "match_score": number,
                        "explanation": "string",
                        "key_benefits": ["string"],
                        "requirements_met": ["string"],
                        "requirements_missing": ["string"]
                    }}
                ],
                "summary": "string",
                "next_steps": ["string"]
            }}
            
            Consider:
            1. Academic background match
            2. Location preferences
            3. Field of study alignment
            4. Exam scores and eligibility
            5. Additional preferences
            
            Sort recommendations by match_score in descending order.
            """
            
            # Request payload
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are an AI counselor that generates personalized program recommendations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1024,
                "top_p": 1,
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{GroqService.GROQ_API_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    return {
                        "error": f"API error: {response.status_code}",
                        "message": "Failed to generate recommendations"
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
                        recommendations = json.loads(json_content)
                    else:
                        # Fall back to the entire content if JSON markers not found
                        recommendations = json.loads(content)
                    
                    # Add the raw response for debugging
                    recommendations["raw_response"] = content
                    
                    return recommendations
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Groq response: {str(e)}")
                    return {
                        "error": "Failed to parse recommendations",
                        "raw_output": content
                    }
                
        except Exception as e:
            logger.error(f"Error generating course recommendations: {str(e)}")
            return {
                "error": str(e),
                "message": "Failed to generate recommendations"
            }
    
    @staticmethod
    async def chat_with_student(
        student_data: Dict[str, Any],
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Chat with a student using Groq API and provide program recommendations.
        
        Args:
            student_data (Dict[str, Any]): The student's profile data
            message (str): The student's message
            conversation_history (List[Dict[str, str]]): Previous conversation messages
            
        Returns:
            Dict[str, Any]: The AI's response and any additional information
        """
        try:
            # Get available programs for recommendations
            available_programs = await ProgramModel.get_all()
            
            # Construct the system prompt with student context and available programs
            system_prompt = f"""
            You are an AI counselor helping students choose the right educational program.
            
            Student Profile:
            - Academic Background: {json.dumps(student_data.get('academic_background', {}))}
            - Preferred Location: {student_data.get('preferred_location', 'Not specified')}
            - Field of Interest: {student_data.get('field_of_study', 'Not specified')}
            - Exam Scores: {json.dumps(student_data.get('exam_scores', {}))}
            - Additional Preferences: {json.dumps(student_data.get('additional_preferences', {}))}
            
            Available Programs:
            {json.dumps(available_programs, indent=2)}
            
            Your role is to:
            1. Keep responses concise and focused on the student's specific query
            2. Provide personalized program recommendations based on the student's profile
            3. Match programs to the student's eligibility criteria and preferences
            4. Answer questions about educational pathways clearly and directly
            
            When recommending programs:
            - Prioritize programs that match the student's academic background
            - Consider location preferences as a key factor
            - Match field of study interests with program offerings
            - Take into account budget constraints if mentioned
            - Consider program duration and mode of delivery preferences
            
            Communication style:
            - Be concise and direct - avoid lengthy explanations
            - Focus on answering the specific question asked
            - Use bullet points for multiple recommendations
            - Highlight key eligibility criteria and application deadlines
            - If the student asks about programs, always reference specific programs from the available options
            
            Remember: Your goal is to help students find the right educational path efficiently and effectively.
            """
            
            # Prepare the conversation history for the API
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history (limit to last 10 messages to stay within context window)
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
                
            # Add the current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Make the API request to Groq
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{GroqService.GROQ_API_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GroqService.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama3-8b-8192",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 1,
                        "stream": False
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    return {
                        "error": f"API error: {response.status_code}",
                        "message": "I'm sorry, I'm having trouble processing your request right now."
                    }
                    
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                return {
                    "response": ai_response,
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Error in chat with student: {str(e)}")
            return {
                "error": str(e),
                "message": "I'm sorry, I'm having trouble processing your request right now."
            }
