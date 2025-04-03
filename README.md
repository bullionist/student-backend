# AI-Powered Student Counseling Platform Backend

A FastAPI-based backend for an AI-powered student counseling platform.

## Features

- RESTful API for student counseling services
- Program data management for admins
- NLP integration with Groq API for processing student inputs
- Authentication via Supabase Email OTP
- Secure data storage using Supabase

## Tech Stack

- FastAPI
- Supabase (PostgreSQL)
- Groq API
- Python 3.9+

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Supabase account
- Groq API access

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables (see `.env.example`)
5. Run the development server:
   ```
   uvicorn app.main:app --reload
   ```

### Environment Variables

Create a `.env` file with the following variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

Run tests using pytest:

```
pytest
```
