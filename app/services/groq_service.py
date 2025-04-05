import httpx
from app.config import settings
from typing import Dict, Any, Optional, List
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
            - Preferred locations for study (can be multiple)
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
                "preferred_location": ["string"],
                "field_of_study": "string",
                "exam_scores": {{
                    "exam_name": "score"
                }},
                "additional_preferences": {{
                    "preference_key": "preference_value"
                }}
            }}
            
            Only include fields that are explicitly mentioned in the input.
            For preferred_location, return an array of strings even if only one location is mentioned.
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
                except json.JSONDecodeError:
                    return {
                        "error": "Failed to parse structured data",
                        "raw_input": input_text,
                        "raw_output": content
                    }
                
        except Exception as e:
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
                "preferred_location": student_data.get("preferred_location", []),
                "field_of_study": student_data.get("field_of_study", "Not specified"),
                "exam_scores": student_data.get("exam_scores", []),
                "additional_preferences": student_data.get("additional_preferences", {})
            }
            
            # Pre-filter programs based on student's preferred locations
            filtered_programs = []
            preferred_locations = student_data.get("preferred_location", [])
            
            if preferred_locations and len(preferred_locations) > 0:
                # Filter programs that match any of the student's preferred locations
                for program in available_programs:
                    program_location = program.get("location", "").lower()
                    for location in preferred_locations:
                        location_lower = location.lower()
                        if location_lower in program_location or program_location in location_lower:
                            filtered_programs.append(program)
                            break  # Once a match is found, no need to check other locations
                
                # If no programs match any location, use all programs
                if not filtered_programs:
                    filtered_programs = available_programs
            else:
                # If no preferred locations are specified, use all programs
                filtered_programs = available_programs
            
            # Limit to a maximum of 50 programs to avoid token limits
            if len(filtered_programs) > 50:
                filtered_programs = filtered_programs[:50]
            
            # Format programs data for the prompt
            programs_info = []
            for program in filtered_programs:
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
            
            Available Programs (filtered by location preference):
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
                except json.JSONDecodeError:
                    return {
                        "error": "Failed to parse recommendations",
                        "raw_output": content
                    }
                
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to generate recommendations"
            }
    
    @staticmethod
    async def chat_with_student(student_data: Dict[str, Any], message: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Chat with the student using Groq API.
        Returns the AI's response and updates the conversation history.
        """
        try:
            # Get all available programs from the database
            all_programs = await ProgramModel.get_all()
            
            # Pre-filter programs based on student preferences
            filtered_programs = all_programs
            
            # 1. Filter by preferred location if available
            if "preferred_location" in student_data and student_data["preferred_location"]:
                preferred_locations = student_data["preferred_location"]
                
                # Handle different types of preferred_location data
                if isinstance(preferred_locations, str):
                    preferred_locations = [preferred_locations]
                elif isinstance(preferred_locations, dict):
                    # Handle case where preferred_location is a dictionary
                    preferred_locations = [str(preferred_locations)]
                elif isinstance(preferred_locations, list):
                    # Ensure all items in the list are strings
                    preferred_locations = [str(loc) for loc in preferred_locations]
                else:
                    # Handle any other type by converting to string
                    preferred_locations = [str(preferred_locations)]
                
                # Convert to lowercase for case-insensitive matching
                preferred_locations = [str(loc).lower() for loc in preferred_locations]
                
                # Filter programs by location
                filtered_programs = [
                    program for program in all_programs 
                    if isinstance(program.get("location"), str) and 
                    program.get("location", "").lower() in preferred_locations
                ]
                
                # If no programs match the location preference, use all programs
                if not filtered_programs:
                    filtered_programs = all_programs
            
            # 2. Filter by field of study if available
            if "field_of_study" in student_data and student_data["field_of_study"]:
                field_of_study = str(student_data["field_of_study"]).lower()
                field_filtered_programs = [
                    program for program in filtered_programs 
                    if isinstance(program.get("program_title"), str) and 
                    field_of_study in program.get("program_title", "").lower()
                ]
                
                # If programs match the field of study, use those
                if field_filtered_programs:
                    filtered_programs = field_filtered_programs
            
            # 3. Filter by tuition fees if budget preference is available
            if "additional_preferences" in student_data and student_data["additional_preferences"]:
                additional_preferences = student_data["additional_preferences"]
                if isinstance(additional_preferences, dict) and "budget_range" in additional_preferences:
                    budget_range = additional_preferences["budget_range"]
                    
                    # Parse budget range (format: "min-max")
                    try:
                        if isinstance(budget_range, str):
                            min_budget, max_budget = map(int, budget_range.split("-"))
                            
                            # Filter programs within budget range
                            budget_filtered_programs = [
                                program for program in filtered_programs 
                                if isinstance(program.get("fees"), (int, float)) and 
                                min_budget <= program.get("fees") <= max_budget
                            ]
                            
                            # If programs match the budget, use those
                            if budget_filtered_programs:
                                filtered_programs = budget_filtered_programs
                    except (ValueError, AttributeError):
                        # If budget parsing fails, continue with current filtered programs
                        pass
            
            # Limit the number of programs to avoid token limits
            if len(filtered_programs) > 50:
                filtered_programs = filtered_programs[:50]
            
            # Format student data for the prompt
            student_info = {
                "academic_background": str(student_data.get("academic_background", "Not specified")),
                "preferred_location": str(student_data.get("preferred_location", "Not specified")),
                "field_of_study": str(student_data.get("field_of_study", "Not specified")),
                "exam_scores": student_data.get("exam_scores", []),
                "additional_preferences": student_data.get("additional_preferences", {})
            }
            
            # Format programs data for the prompt
            programs_data = []
            for program in filtered_programs:
                programs_data.append({
                    "title": program.get("program_title", "Unknown Program"),
                    "institution": program.get("institution", "Unknown Institution"),
                    "location": program.get("location", "Unknown Location"),
                    "duration": program.get("duration", "Unknown Duration"),
                    "fees": program.get("fees", "Unknown Fees"),
                    "overview": program.get("program_overview", "No overview available"),
                    "delivery_mode": program.get("mode_of_delivery", "Unknown Delivery Mode")
                })
            
            # Create a JSON prompt for the Groq API
            prompt = {
                "role": "system",
                "content": f"""You are an AI educational counselor helping students find the right educational programs.
                
                Student Profile:
                - Academic Background: {student_info['academic_background']}
                - Preferred Location: {student_info['preferred_location']}
                - Field of Study: {student_info['field_of_study']}
                - Additional Preferences: {student_info['additional_preferences']}
                
                Available Programs (filtered based on student preferences):
                {json.dumps(programs_data, indent=2)}
                
                Guidelines:
                1. Behave like a human counselor - be friendly, empathetic, and conversational.
                2. Only provide program recommendations when the student explicitly asks for them.
                3. For general questions or greetings, respond naturally without forcing recommendations.
                4. Keep your responses concise and focused on the student's specific questions.
                5. When recommendations are requested, only recommend programs from the available programs list that match the student's profile.
                6. If the student asks about programs not in the list, explain that you can only recommend from available options.
                7. Prioritize programs that align with the student's academic background, location preferences, and field of study.
                8. Ask follow-up questions to better understand the student's needs if necessary.
                9. If no programs match the student's criteria, suggest broadening their search criteria.
                10. IMPORTANT: If the student asks questions unrelated to educational programs or academic counseling (such as personal advice, non-educational topics, or general knowledge questions), politely redirect them back to educational counseling. For example: "I'm here to help you with educational programs and academic guidance. Let's focus on finding the right educational path for you. What are your academic interests?"
                11. CRITICAL: If the student's profile (especially location preferences) doesn't match any universities in the database, inform them clearly and suggest they edit their profile to include more countries or locations. For example: "I couldn't find any programs matching your current location preferences. You might want to edit your profile to include more countries or regions to increase your chances of finding suitable programs. Would you like me to help you with that?"
                
                Previous conversation:
                {json.dumps(conversation_history, indent=2)}
                
                Student's message: {message}
                
                Provide a helpful, human-like response that addresses the student's question. Only include program recommendations if the student specifically asks for them."""
            }
            
            # Prepare the request payload
            payload = {
                "model": "llama3-8b-8192",
                "messages": [prompt],
                "max_tokens": 1024,
                "temperature": 0.7,
                "top_p": 1,
                "stream": False
            }
            
            # Make the API call
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{GroqService.GROQ_API_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GroqService.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    response_data = response.json()
                    return {
                        "success": True,
                        "response": response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response generated")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API request failed with status code {response.status_code}: {response.text}"
                    }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error in chat with student: {str(e)}"
            }
