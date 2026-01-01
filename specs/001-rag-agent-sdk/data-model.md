# Data Model: Frontend-Backend Integration

## Key Entities

### QueryRequest
- **Fields**:
  - `query` (string, required): The natural language question from the user
  - `session_id` (string, optional): Unique identifier for the conversation session
  - `context` (object, optional): Additional context information for the query

- **Validation**:
  - Query must be non-empty string with 1-1000 characters
  - Session ID must be a valid UUID format if provided

### QueryResponse
- **Fields**:
  - `response` (string, required): The agent's response to the user's query
  - `session_id` (string, required): Unique identifier for the conversation session
  - `sources` (array, optional): List of source documents used to generate the response
  - `timestamp` (string, required): ISO 8601 timestamp of the response
  - `status` (string, required): Status of the query processing (success, error, timeout)

- **Validation**:
  - Response must be non-empty string
  - Session ID must be a valid UUID format
  - Status must be one of: "success", "error", "timeout"

### ChatMessage
- **Fields**:
  - `id` (string, required): Unique identifier for the message
  - `role` (string, required): Role of the message sender ("user", "assistant", "system")
  - `content` (string, required): The content of the message
  - `timestamp` (string, required): ISO 8601 timestamp of when the message was created
  - `session_id` (string, required): ID of the chat session this message belongs to

- **Validation**:
  - Role must be one of: "user", "assistant", "system"
  - Content must be non-empty string

### ChatSession
- **Fields**:
  - `session_id` (string, required): Unique identifier for the chat session
  - `created_at` (string, required): ISO 8601 timestamp of session creation
  - `updated_at` (string, required): ISO 8601 timestamp of last session update
  - `messages` (array, optional): List of ChatMessage objects in the session
  - `metadata` (object, optional): Additional metadata about the session

- **Validation**:
  - Session ID must be a valid UUID format
  - Created and updated timestamps must be valid ISO 8601 strings

## Data Relationships

- A `ChatSession` contains multiple `ChatMessage` objects
- A `QueryRequest` creates or continues a `ChatSession`
- A `QueryResponse` is generated from a `QueryRequest` and updates the `ChatSession`

## State Transitions

### Query Processing States
1. **Received**: QueryRequest has been received by the API
2. **Processing**: Agent is retrieving context and generating response
3. **Completed**: Response has been generated and returned
4. **Failed**: Error occurred during processing

### Session States
1. **Active**: Session has ongoing conversation
2. **Inactive**: Session has not been updated in >30 minutes
3. **Archived**: Session has completed its lifecycle

## Validation Rules

1. All timestamps must follow ISO 8601 format
2. Session IDs must be valid UUIDs
3. Query strings must be between 1 and 1000 characters
4. Response strings must not be empty
5. Message roles must be valid values