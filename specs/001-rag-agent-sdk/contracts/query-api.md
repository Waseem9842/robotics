# OpenAPI Specification: Query Endpoint

## API: `/query`

### Endpoint: `POST /api/query`

**Description**: Accepts a natural language query from the frontend and returns a response from the RAG agent.

**Request Body**:
```json
{
  "query": "string (required) - The natural language question from the user",
  "session_id": "string (optional) - Unique identifier for the conversation session",
  "context": "object (optional) - Additional context information for the query"
}
```

**Request Validation**:
- `query` must be a non-empty string with 1-1000 characters
- `session_id` must be a valid UUID format if provided
- `context` can contain any additional metadata needed for the query

**Response (200 OK)**:
```json
{
  "response": "string (required) - The agent's response to the user's query",
  "session_id": "string (required) - Unique identifier for the conversation session",
  "sources": "array (optional) - List of source documents used to generate the response",
  "timestamp": "string (required) - ISO 8601 timestamp of the response",
  "status": "string (required) - Status of the query processing (success, error, timeout)"
}
```

**Response Validation**:
- `response` must be a non-empty string
- `session_id` must be a valid UUID format
- `status` must be one of: "success", "error", "timeout"
- `timestamp` must be a valid ISO 8601 string

**Error Responses**:
- `400 Bad Request`: Invalid request format or validation errors
- `422 Unprocessable Entity`: Query validation failed
- `500 Internal Server Error`: Agent processing error

### Endpoint: `GET /api/health`

**Description**: Health check endpoint to verify API availability.

**Response (200 OK)**:
```json
{
  "status": "string - API health status",
  "timestamp": "string - ISO 8601 timestamp"
}
```

## Security Configuration

**CORS Settings**:
- Allow origins: `['http://localhost:3000', 'http://localhost:3001', 'https://your-book-domain.com']`
- Allow methods: `['GET', 'POST', 'OPTIONS']`
- Allow headers: `['Content-Type', 'Authorization']`

**Rate Limiting**:
- Limit: 100 requests per minute per IP
- Window: 60 seconds

## API Implementation Requirements

1. **Request Processing**:
   - Validate input parameters according to schema
   - Pass query to existing agent from `agent.py`
   - Handle session management if session_id provided

2. **Response Generation**:
   - Format response according to schema
   - Include source documents used in response generation
   - Add appropriate timestamps

3. **Error Handling**:
   - Return appropriate HTTP status codes
   - Provide meaningful error messages
   - Log errors for debugging

## Integration Points

- **Agent Integration**: Connect to the existing agent in `agent.py`
- **Frontend Integration**: Docusaurus frontend will call this API to get chatbot responses
- **Session Management**: Optional session tracking for conversation history