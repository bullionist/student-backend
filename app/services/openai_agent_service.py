from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import settings
from app.models.program import ProgramModel
from app.database.supabase import supabase_client
import json
from loguru import logger
from agents import Agent, Runner, function_tool
from dataclasses import dataclass

@dataclass
class StudentContext:
    """Context for the counselor agent containing student information"""
    name: str
    email: str
    educational_qualifications: List[Dict[str, Any]]
    preferred_location: List[str]
    preferred_program: str
    preferred_field_of_study: List[str]
    budget: int
    special_requirements: List[str]
    
    def __str__(self):
        """String representation for logging"""
        return f"StudentContext(name={self.name}, email={self.email}, preferred_program={self.preferred_program}, preferred_field_of_study={self.preferred_field_of_study}, budget={self.budget})"

# Define the fetch_programs function outside the class
@function_tool
async def fetch_programs(
    field_of_study: str, 
    location: Optional[str] = None, 
    budget: Optional[float] = None,
    program_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch educational programs from the database based on criteria.
    
    This tool searches for educational programs that match the specified criteria.
    It returns a list of programs with detailed information about each program.
    
    Args:
        field_of_study: The field of study to search for (e.g., "Computer Science", "Business Administration")
        location: Optional location to filter programs by (e.g., "United States", "United Kingdom")
        budget: Optional maximum budget to filter programs by
        program_type: Optional program type to filter by (e.g., "undergraduate", "postgraduate", "phd")
        
    Returns:
        A dictionary containing:
        - success: Boolean indicating if the operation was successful
        - programs: List of matching programs with detailed information
        - message: Summary message about the results
        - error: Error message if the operation failed
    """
    logger.info(f"🔍 fetch_programs called with: field_of_study={field_of_study}, location={location}, budget={budget}, program_type={program_type}")
    try:
        # Check if Supabase client is available
        if not supabase_client:
            logger.error("❌ Supabase client is not initialized")
            return {
                "success": False,
                "error": "Database connection error. Please try again later."
            }

        # Validate inputs
        valid_fields = {
            "Computer Science",
            "Business Administration",
            "Engineering",
            "Data Science",
            "Medicine",
            "Law",
            "Psychology",
            "Environmental Science",
            "International Relations",
            "Architecture"
        }
        
        valid_locations = {
            "United States",
            "United Kingdom",
            "Canada",
            "Australia",
            "Germany",
            "New Zealand",
            "Singapore",
            "Ireland",
            "Netherlands",
            "Japan"
        }

        valid_program_types = {"undergraduate", "postgraduate", "phd"}

        # Input validation
        if field_of_study not in valid_fields:
            logger.warning(f"❌ Invalid field of study: {field_of_study}. Must be one of: {', '.join(valid_fields)}")
            return {
                "success": False,
                "error": f"Invalid field of study. Must be one of: {', '.join(valid_fields)}"
            }

        if location and location not in valid_locations:
            logger.warning(f"❌ Invalid location: {location}. Must be one of: {', '.join(valid_locations)}")
            return {
                "success": False,
                "error": f"Invalid location. Must be one of: {', '.join(valid_locations)}"
            }

        if program_type and program_type.lower() not in valid_program_types:
            logger.warning(f"❌ Invalid program type: {program_type}. Must be one of: {', '.join(valid_program_types)}")
            return {
                "success": False,
                "error": f"Invalid program type. Must be one of: {', '.join(valid_program_types)}"
            }

        # Build Supabase query
        logger.info("🔍 Building Supabase query for programs")
        query = supabase_client.table("programs").select("*")
        
        # Add filters
        query = query.eq("field_of_study", field_of_study)  # Exact match for field of study
        logger.info(f"🔍 Added filter: field_of_study = {field_of_study}")
        
        if location:
            query = query.eq("location", location)  # Exact match for location
            logger.info(f"🔍 Added filter: location = {location}")
            
        if program_type:
            query = query.eq("program_type", program_type.lower())  # Exact match for program type
            logger.info(f"🔍 Added filter: program_type = {program_type.lower()}")
            
        if budget is not None:
            # Convert budget to integer to avoid type error
            budget_int = int(budget)
            query = query.lte("budget", budget_int)  # Less than or equal for budget
            logger.info(f"🔍 Added filter: budget <= {budget_int}")
            
        # Execute query - ensure we're using await here
        logger.info("🔍 Executing Supabase query")
        try:
            # Use the execute() method which returns a response object
            response = query.execute()
            
            # Check if the response has data
            if not response.data:
                logger.info("🔍 No programs found matching criteria")
                return {
                    "success": True,
                    "programs": [],
                    "message": f"""No programs found matching your criteria:
                    - Field of Study: {field_of_study}
                    - Location: {location if location else 'Any'}
                    - Program Type: {program_type if program_type else 'Any'}
                    - Budget: {budget if budget else 'Any'}
                    
                    Consider adjusting your preferences or try different criteria."""
                }

            # Format the programs for response
            logger.info(f"🔍 Found {len(response.data)} matching programs")
            formatted_programs = []
            for program in response.data:
                formatted_programs.append({
                    "id": program.get("id"),
                    "program_title": program.get("program_title"),
                    "institution": program.get("institution"),
                    "program_overview": program.get("program_overview"),
                    "location": program.get("location"),
                    "program_type": program.get("program_type"),
                    "field_of_study": program.get("field_of_study"),
                    "budget": program.get("budget"),
                    "duration": program.get("duration"),
                    "curriculum": program.get("curriculum"),
                    "requirements": program.get("requirements")
                })
                
            logger.info(f"✅ Successfully formatted {len(formatted_programs)} programs")
            return {
                "success": True,
                "programs": formatted_programs,
                "message": f"Found {len(formatted_programs)} matching programs."
            }
        except Exception as query_error:
            logger.error(f"❌ Error executing Supabase query: {str(query_error)}")
            return {
                "success": False,
                "error": f"Database query error: {str(query_error)}"
            }
        
    except Exception as e:
        logger.error(f"❌ Error fetching programs: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

class OpenAIAgentService:
    """Service to interact with OpenAI Agents for student counseling"""
    
    def __init__(self):
        # Set the OpenAI API key for the Agents SDK
        import os
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        logger.info("🔑 OpenAI API key set for Agents SDK")
        
        # Initialize the counselor agent
        logger.info("🤖 Initializing Educational Counselor agent")
        self.counselor_agent = Agent(
            name="Educational Counselor",
            instructions="""You are an empathetic educational counselor helping students find the right educational programs.
            
            IMPORTANT: You have access to the student's context information through the 'context' parameter. 
            ALWAYS use this information first before asking the student for details they've already provided.
            
            Your role is to:
            1. Understand the student's educational qualifications, interests, and preferences FROM THE CONTEXT
            2. Provide personalized guidance and recommendations based on:
               - Educational qualifications (qualification, grade, year of completion) FROM THE CONTEXT
               - Preferred locations FROM THE CONTEXT
               - Preferred program type (undergraduate/postgraduate) FROM THE CONTEXT
               - Preferred fields of study FROM THE CONTEXT
               - Budget constraints FROM THE CONTEXT
               - Special requirements FROM THE CONTEXT
            3. Answer questions about educational programs and career paths
            4. Help students make informed decisions about their education
            5. Be friendly, supportive, and professional
            6. Focus on educational counseling only - redirect non-educational topics
            7. When a student asks about programs, countries, or educational options, ALWAYS use the fetch_programs tool to find suitable options
            8. Extract relevant information from the conversation to update the student's profile
            
            CRITICAL INSTRUCTION: For ANY question about countries, programs, or educational options, you MUST use the fetch_programs tool.
            For example, if a student asks "which countries best suit me?" or "what programs are available?", 
            you MUST call the fetch_programs tool with appropriate parameters based on the student's context.
            
            NEVER ask for information that's already available in the context. If you need additional information 
            beyond what's in the context, only then ask the student for it.
            """,
            model="gpt-4-turbo-preview",
            tools=[fetch_programs]  # Add the fetch_programs tool directly to the counselor agent
        )
        logger.info("✅ Educational Counselor agent initialized with fetch_programs tool")
        
        # Initialize the program matcher agent with the fetch_programs function tool
        logger.info("🤖 Initializing Program Matcher agent")
        self.program_matcher_agent = Agent(
            name="Program Matcher",
            instructions="""You are a specialized agent that matches students with educational programs.
            Your role is to:
            1. Analyze student profiles and preferences
            2. Match them with suitable educational programs based on:
               - Educational qualifications
               - Location preferences
               - Program type (undergraduate/postgraduate)
               - Field of study
               - Budget constraints
               - Program requirements
            3. Provide detailed match explanations
            4. Sort recommendations by relevance
            5. Use the fetch_programs tool to search for matching programs
            """,
            model="gpt-4-turbo-preview",
            tools=[fetch_programs]
        )
        logger.info("✅ Program Matcher agent initialized with fetch_programs tool")
        
        # Initialize conversation history storage
        self.conversation_histories = {}  # Dictionary to store conversation histories by student ID
        logger.info("💬 Initialized conversation history storage")
    
    async def chat_with_student(
        self,
        student_data: Dict[str, Any],
        message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Chat with the student using the counselor agent.
        The counselor agent can use the fetch_programs tool directly when needed.
        """
        student_id = student_data.get('id', 'unknown')
        logger.info(f"💬 Starting chat with student: {student_data.get('name', 'Unknown')} (ID: {student_id})")
        logger.info(f"💬 Student message: {message}")
        
        # Get or initialize conversation history for this student
        if student_id not in self.conversation_histories:
            self.conversation_histories[student_id] = []
            logger.info(f"💬 Created new conversation history for student: {student_id}")
        
        # Add the current message to the conversation history
        self.conversation_histories[student_id].append({
            "role": "student",
            "content": message
        })
        
        # Get the last 3 conversation messages (if available)
        recent_history = self.conversation_histories[student_id][-3:] if len(self.conversation_histories[student_id]) > 0 else []
        
        # Log the conversation history
        if recent_history:
            logger.info(f"💬 Including recent conversation history for student {student_id}:")
            for i, msg in enumerate(recent_history):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                logger.info(f"  Message {i+1}: {role.capitalize()}: {content[:100]}...")
        else:
            logger.info(f"💬 No conversation history available for student {student_id}")
        
        try:
            # Create student context for local context (used by tools and callbacks)
            logger.info("🔍 Creating student context from data")
            student_context = StudentContext(
                name=student_data.get('name', 'Not specified'),
                email=student_data.get('email', 'Not specified'),
                educational_qualifications=student_data.get('educational_qualifications', []),
                preferred_location=student_data.get('preferred_location', []),
                preferred_program=student_data.get('preferred_program', 'Not specified'),
                preferred_field_of_study=student_data.get('preferred_field_of_study', []),
                budget=student_data.get('budget', 0),
                special_requirements=student_data.get('special_requirements', [])
            )
            logger.info(f"✅ Student context created: {student_context}")
            
            # Log detailed context information
            logger.info("🔍 Detailed student context:")
            logger.info(f"  - Name: {student_context.name}")
            logger.info(f"  - Email: {student_context.email}")
            logger.info(f"  - Educational Qualifications: {json.dumps(student_context.educational_qualifications, indent=2)}")
            logger.info(f"  - Preferred Locations: {student_context.preferred_location}")
            logger.info(f"  - Preferred Program: {student_context.preferred_program}")
            logger.info(f"  - Preferred Fields of Study: {student_context.preferred_field_of_study}")
            logger.info(f"  - Budget: {student_context.budget}")
            logger.info(f"  - Special Requirements: {student_context.special_requirements}")

            # Format the conversation history
            conversation_context = ""
            if recent_history:
                conversation_context = "Recent Conversation History:\n"
                for i, msg in enumerate(recent_history):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    conversation_context += f"{i+1}. {role.capitalize()}: {content}\n"
                conversation_context += "\n"

            # Create a formatted input that includes both the message and student context
            # This ensures the LLM has access to the student information
            formatted_input = f"""Student Information:
Name: {student_context.name}
Email: {student_context.email}
Educational Qualifications: {json.dumps(student_context.educational_qualifications, indent=2)}
Preferred Locations: {', '.join(student_context.preferred_location)}
Preferred Program: {student_context.preferred_program}
Preferred Fields of Study: {', '.join(student_context.preferred_field_of_study)}
Budget: ${student_context.budget}
Special Requirements: {', '.join(student_context.special_requirements)}

{conversation_context}
Student Message: {message}

IMPORTANT: For questions about countries, programs, or educational options, you MUST use the fetch_programs tool.
For example, if the student asks about which countries suit them, use the fetch_programs tool with their preferred fields of study."""

            # Run the counselor agent using the async method
            logger.info("🤖 Running counselor agent with student message")
            logger.info(f"🤖 Agent input: {formatted_input}")
            logger.info(f"🤖 Agent context: {student_context}")
            
            # Pass both the formatted input (for LLM) and the context (for tools)
            result = await Runner.run(
                self.counselor_agent,
                formatted_input,
                context=student_context
            )
            
            logger.info(f"✅ Counselor agent response received: {result.final_output[:100]}...")
            
            # Add the agent's response to the conversation history
            self.conversation_histories[student_id].append({
                "role": "assistant",
                "content": result.final_output
            })
            
            # Log any tool calls made by the agent
            # The OpenAI Agents SDK doesn't expose tool calls in the result object directly
            # Instead, we can check if the fetch_programs function was called by looking at the logs
            # We've already added detailed logging in the fetch_programs function
            
            # Check if the response mentions programs or countries
            if "program" in result.final_output.lower() or "country" in result.final_output.lower():
                logger.info("✅ Agent response includes program or country information")
            else:
                logger.warning("⚠️ Agent response may not include program or country information")
            
            response = {
                "success": True,
                "response": result.final_output
            }
            logger.info(f"✅ Returning response to student: {response['response'][:100]}...")
            return response

        except Exception as e:
            logger.error(f"❌ Error in chat_with_student: {str(e)}")
            error_response = {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, I encountered an error while processing your request. Please try again later."
            }
            logger.info(f"✅ Returning error response to student: {error_response['response']}")
            return error_response 