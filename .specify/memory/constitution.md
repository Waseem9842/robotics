<!-- SYNC IMPACT REPORT
Version change: N/A (initial) → 1.0.0
Modified principles: N/A
Added sections: Core Principles (6), Book Standards, RAG Chatbot Standards, Development Workflow
Removed sections: N/A
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ⚠ pending
- README.md ⚠ pending
Follow-up TODOs: None
-->

# AI-Spec-Driven Book with Embedded RAG Chatbot Constitution

## Core Principles

### I. Spec-First Development
Every feature and component must be specified before implementation. All changes to the book content, RAG system, or chatbot functionality must have corresponding specifications in the spec files before coding begins.

### II. Zero Hallucination
The RAG chatbot must only respond with information retrieved from the book content. No responses should be generated from the LLM's training data alone - all answers must be grounded in retrieved context from the vector database.

### III. Technical Clarity for Readers
All book content must be clear, well-structured with runnable code examples. Code snippets must be tested and verified to work as documented, with clear explanations of concepts for technical readers.

### IV. Modular and Reproducible Architecture
The system architecture must be modular with clear separation of concerns between the Docusaurus book, FastAPI backend, vector database, and chatbot UI. The entire system must be reproducible through version-controlled configuration.

### V. Test-First for Critical Components (NON-NEGOTIABLE)
All RAG retrieval logic, chatbot response generation, and book content ingestion must have comprehensive tests written before implementation. The red-green-refactor cycle must be strictly enforced for all critical functionality.

### VI. Security and Configuration Management
No hard-coded secrets or credentials. All sensitive configuration must be managed through environment variables and secure configuration management. All API endpoints must implement proper authentication and authorization where required.

## Book Standards
- Platform: Docusaurus (Markdown/MDX) for book content
- Clear chapter structure with examples and runnable code snippets
- All code examples must be well-documented and version-controlled on GitHub
- Book content must follow a consistent structure with proper navigation and search functionality

## RAG Chatbot Standards
- Backend: FastAPI for the RAG API service
- LLM: OpenAI Agents / ChatKit SDKs for response generation
- Vector DB: Qdrant Cloud (Free Tier) for document storage and retrieval
- Metadata DB: Neon Serverless Postgres for metadata management
- Must support both full-book queries and selected-text queries from user input
- Must refuse to answer questions outside the scope of the book content

## Development Workflow
- Use Spec-Kit Plus for all specification, planning, and task management
- All changes must follow the spec → plan → tasks workflow
- Code reviews must verify compliance with all constitution principles
- Automated testing must pass before merging any changes
- Documentation updates must accompany all feature implementations

## Governance

This constitution governs all development activities for the AI-Spec-Driven Book with Embedded RAG Chatbot project. All team members must adhere to these principles, and any deviations must be documented with proper justification. Amendments to this constitution require explicit approval and must be propagated to all dependent templates and documentation. All pull requests and code reviews must verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-23
