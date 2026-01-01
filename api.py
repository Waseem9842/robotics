"""
FastAPI server for RAG Chatbot API
Exposes query endpoint that connects to existing RAG agent
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import the agent function from agent.py
from agent import process_question_with_agent

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class QueryRequest(BaseModel):
    """
    Request model for query endpoint
    Based on data model: QueryRequest entity
    """
    query: str = Field(..., description="The natural language question from the user")
    session_id: Optional[str] = Field(None, description="Unique identifier for the conversation session")
    context: Optional[Dict[str, Any]] = Field({}, description="Additional context information for the query")

    @validator('query')
    def validate_query(cls, v):
        if not v or len(v) < 1 or len(v) > 1000:
            raise ValueError('Query must be a non-empty string with 1-1000 characters')
        return v

    @validator('session_id')
    def validate_session_id(cls, v):
        if v is not None:
            try:
                UUID(v)  # Validate UUID format
            except ValueError:
                raise ValueError('Session ID must be a valid UUID format')
        return v


class QueryResponse(BaseModel):
    """
    Response model for query endpoint
    Based on data model: QueryResponse entity
    """
    response: str = Field(..., description="The agent's response to the user's query")
    session_id: str = Field(..., description="Unique identifier for the conversation session")
    sources: Optional[List[Dict[str, Any]]] = Field([], description="List of source documents used to generate the response")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the response")
    status: str = Field(..., description="Status of the query processing (success, error, timeout)")

    @validator('response')
    def validate_response(cls, v):
        if not v:
            raise ValueError('Response must be a non-empty string')
        return v

    @validator('session_id')
    def validate_response_session_id(cls, v):
        try:
            UUID(v)  # Validate UUID format
        except ValueError:
            raise ValueError('Session ID must be a valid UUID format')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["success", "error", "timeout"]
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class ChatMessage(BaseModel):
    """
    Model for chat messages
    Based on data model: ChatMessage entity
    """
    id: str = Field(..., description="Unique identifier for the message")
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")
    timestamp: str = Field(..., description="ISO 8601 timestamp of when the message was created")
    session_id: str = Field(..., description="ID of the chat session this message belongs to")

    @validator('role')
    def validate_role(cls, v):
        valid_roles = ["user", "assistant", "system"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v

    @validator('content')
    def validate_content(cls, v):
        if not v:
            raise ValueError('Content must be a non-empty string')
        return v


class ChatSession(BaseModel):
    """
    Model for chat sessions
    Based on data model: ChatSession entity
    """
    session_id: str = Field(..., description="Unique identifier for the chat session")
    created_at: str = Field(..., description="ISO 8601 timestamp of session creation")
    updated_at: str = Field(..., description="ISO 8601 timestamp of last session update")
    messages: Optional[List[ChatMessage]] = Field([], description="List of ChatMessage objects in the session")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata about the session")

    @validator('session_id')
    def validate_session_id(cls, v):
        try:
            UUID(v)  # Validate UUID format
        except ValueError:
            raise ValueError('Session ID must be a valid UUID format')
        return v


app = FastAPI(
    title="RAG Chatbot API",
    description="API for RAG chatbot integration with Docusaurus frontend",
    version="1.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware for Docusaurus frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-book-domain.com",
        "http://localhost:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "RAG Chatbot API is running"}


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify API availability"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/query", response_model=QueryResponse)
@limiter.limit("100/minute")  # Limit to 100 requests per minute per IP
async def query_endpoint(request: Request, query_request: QueryRequest):
    """Query endpoint that calls the existing agent and returns responses in JSON format"""
    try:
        # Generate session ID if not provided
        session_id = query_request.session_id or str(uuid.uuid4())

        # Call the existing agent to process the query
        response_text = process_question_with_agent(query_request.query)

        # Create response with success status
        response = QueryResponse(
            response=response_text,
            session_id=session_id,
            sources=[],  # For now, we're not capturing sources from the agent
            timestamp=datetime.utcnow().isoformat(),
            status="success"
        )

        return response
    except Exception as e:
        # Handle any errors in agent processing
        session_id = query_request.session_id or str(uuid.uuid4())
        error_response = QueryResponse(
            response=f"Error processing query: {str(e)}",
            session_id=session_id,
            sources=[],
            timestamp=datetime.utcnow().isoformat(),
            status="error"
        )
        raise HTTPException(status_code=500, detail=error_response.dict())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)