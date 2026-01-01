# Quickstart: Frontend-Backend Integration

## Prerequisites

- Python 3.11+
- Node.js 18+
- Access to Qdrant vector database
- OpenAI API key (if using OpenAI models)

## Setup Backend (FastAPI)

1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn python-multipart python-dotenv
   ```

2. **Create the API server** (`api.py`):
   ```python
   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   import uuid
   from datetime import datetime
   import os
   from typing import Optional, List, Dict, Any

   from agent import RAGAgent  # Import existing agent

   app = FastAPI(
       title="RAG Chatbot API",
       description="API for RAG chatbot integration with Docusaurus frontend",
       version="1.0.0"
   )

   # Initialize the agent
   agent = RAGAgent()  # Initialize with your agent configuration

   class QueryRequest(BaseModel):
       query: str
       session_id: Optional[str] = None
       context: Optional[Dict[str, Any]] = {}

   class QueryResponse(BaseModel):
       response: str
       session_id: str
       sources: Optional[List[Dict[str, Any]]] = []
       timestamp: str
       status: str

   @app.post("/api/query", response_model=QueryResponse)
   async def query_endpoint(request: QueryRequest):
       try:
           # Generate session ID if not provided
           session_id = request.session_id or str(uuid.uuid4())

           # Call the existing agent to process the query
           response = await agent.process_query(request.query, session_id)

           return QueryResponse(
               response=response.answer,
               session_id=session_id,
               sources=response.sources if hasattr(response, 'sources') else [],
               timestamp=datetime.utcnow().isoformat(),
               status="success"
           )
       except Exception as e:
           raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

   @app.get("/api/health")
   async def health_check():
       return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

3. **Run the API server**:
   ```bash
   python api.py
   ```

## Setup Frontend (Docusaurus)

1. **Create Chatbot component** (`book_frontend/src/components/Chatbot/index.js`):
   ```jsx
   import React, { useState, useEffect, useRef } from 'react';
   import './Chatbot.css';

   const Chatbot = () => {
     const [messages, setMessages] = useState([]);
     const [inputValue, setInputValue] = useState('');
     const [isLoading, setIsLoading] = useState(false);
     const [sessionId, setSessionId] = useState(null);
     const messagesEndRef = useRef(null);

     const scrollToBottom = () => {
       messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
     };

     useEffect(() => {
       scrollToBottom();
     }, [messages]);

     const handleSubmit = async (e) => {
       e.preventDefault();
       if (!inputValue.trim() || isLoading) return;

       const userMessage = {
         id: Date.now(),
         role: 'user',
         content: inputValue,
         timestamp: new Date().toISOString()
       };

       setMessages(prev => [...prev, userMessage]);
       setInputValue('');
       setIsLoading(true);

       try {
         const response = await fetch('http://localhost:8000/api/query', {
           method: 'POST',
           headers: {
             'Content-Type': 'application/json',
           },
           body: JSON.stringify({
             query: inputValue,
             session_id: sessionId
           })
         });

         const data = await response.json();

         if (response.ok) {
           setSessionId(data.session_id);

           const botMessage = {
             id: Date.now() + 1,
             role: 'assistant',
             content: data.response,
             sources: data.sources,
             timestamp: data.timestamp
           };

           setMessages(prev => [...prev, botMessage]);
         } else {
           throw new Error(data.detail || 'Failed to get response');
         }
       } catch (error) {
         const errorMessage = {
           id: Date.now() + 1,
           role: 'assistant',
           content: 'Sorry, I encountered an error processing your request. Please try again.',
           timestamp: new Date().toISOString()
         };
         setMessages(prev => [...prev, errorMessage]);
       } finally {
         setIsLoading(false);
       }
     };

     return (
       <div className="chatbot-container">
         <div className="chatbot-header">
           <h3>Book Assistant</h3>
         </div>
         <div className="chatbot-messages">
           {messages.map((message) => (
             <div key={message.id} className={`message ${message.role}`}>
               <div className="message-content">{message.content}</div>
               {message.sources && message.sources.length > 0 && (
                 <div className="message-sources">
                   Sources: {message.sources.map((source, idx) =>
                     <span key={idx} className="source">{source.title || `Source ${idx + 1}`}</span>
                   )}
                 </div>
               )}
             </div>
           ))}
           {isLoading && (
             <div className="message assistant">
               <div className="message-content">Thinking...</div>
             </div>
           )}
           <div ref={messagesEndRef} />
         </div>
         <form onSubmit={handleSubmit} className="chatbot-input-form">
           <input
             type="text"
             value={inputValue}
             onChange={(e) => setInputValue(e.target.value)}
             placeholder="Ask a question about this book..."
             disabled={isLoading}
           />
           <button type="submit" disabled={isLoading}>
             Send
           </button>
         </form>
       </div>
     );
   };

   export default Chatbot;
   ```

2. **Add CSS for Chatbot** (`book_frontend/src/components/Chatbot/Chatbot.css`):
   ```css
   .chatbot-container {
     display: flex;
     flex-direction: column;
     height: 500px;
     border: 1px solid #ddd;
     border-radius: 8px;
     overflow: hidden;
     box-shadow: 0 2px 10px rgba(0,0,0,0.1);
   }

   .chatbot-header {
     background-color: #25c2a0;
     color: white;
     padding: 12px 16px;
     font-weight: bold;
   }

   .chatbot-messages {
     flex: 1;
     overflow-y: auto;
     padding: 16px;
     display: flex;
     flex-direction: column;
     gap: 12px;
   }

   .message {
     max-width: 80%;
     padding: 12px;
     border-radius: 8px;
     line-height: 1.4;
   }

   .message.user {
     align-self: flex-end;
     background-color: #e3f2fd;
     border-bottom-right-radius: 0;
   }

   .message.assistant {
     align-self: flex-start;
     background-color: #f5f5f5;
     border-bottom-left-radius: 0;
   }

   .message-sources {
     margin-top: 8px;
     font-size: 0.8em;
     color: #666;
   }

   .source {
     background-color: #e0e0e0;
     padding: 2px 6px;
     border-radius: 4px;
     margin-right: 4px;
   }

   .chatbot-input-form {
     display: flex;
     padding: 16px;
     border-top: 1px solid #ddd;
     background-color: white;
   }

   .chatbot-input-form input {
     flex: 1;
     padding: 12px;
     border: 1px solid #ddd;
     border-radius: 4px 0 0 4px;
     font-size: 14px;
   }

   .chatbot-input-form button {
     padding: 12px 16px;
     background-color: #25c2a0;
     color: white;
     border: none;
     border-radius: 0 4px 4px 0;
     cursor: pointer;
   }

   .chatbot-input-form button:disabled {
     background-color: #ccc;
     cursor: not-allowed;
   }
   ```

3. **Integrate Chatbot into Docusaurus Layout**:
   Add the Chatbot component to your Docusaurus layout in `book_frontend/src/theme/Layout/index.js` or by using the Docusaurus plugin system.

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

## Running the Full Stack

1. Start the FastAPI backend:
   ```bash
   python api.py
   ```

2. Start the Docusaurus frontend:
   ```bash
   cd book_frontend
   npm start
   ```

3. Access the application at `http://localhost:3000`