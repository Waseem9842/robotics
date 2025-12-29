---
id: 1
title: Update Constitution
stage: constitution
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: claude
command: /sp.constitution
labels: [constitution, setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - .specify/templates/plan-template.md
 - .specify/templates/spec-template.md
 - .specify/templates/tasks-template.md
tests:
 - null
---

## Prompt

```
Project: AI-Spec-Driven Book with Embedded RAG Chatbot

Mission:
Author and publish a technical book using Docusaurus and Spec-Kit Plus, deployed on
GitHub Pages, with an embedded RAG chatbot that answers questions strictly from the
book content, including user-selected text.

Core Principles:
- Spec-first development
- Zero hallucination (answers only from retrieved content)
- Clarity for technical readers
- Modular, reproducible architecture

Book Standards:
- Platform: Docusaurus (Markdown/MDX)
- Clear chapter structure with examples
- Runnable or well-documented code snippets
- Version-controlled on GitHub

RAG Chatbot Standards:
- Backend: FastAPI
- LLM: OpenAI Agents / ChatKit SDKs
- Vector DB: Qdrant Cloud (Free Tier)
- Metadata DB: Neon Serverless Postgres
- Supports full-book and selected-text queries
- Refuses unsupported questions

Constraints:
- No hard-coded secrets
- Environment-based configuration
- Retrieved context required for every response

Deployment:
- Book: GitHub Pages via GitHub Actions
- API: Cloud-hosted FastAPI
- UI: Embedded chatbot in Docusaurus

Documentation:
- README with setup, architecture, and deployment
- Specs for book structure, RAG ingestion, and query flow

Success Criteria:
- Publicly accessible book
- Accurate, grounded chatbot responses
- Deterministic selected-text answering
- End-to-end reproducibility
```

## Response snapshot

Updated the project constitution to reflect the AI-Spec-Driven Book with Embedded RAG Chatbot project requirements. Created 6 core principles (Spec-First Development, Zero Hallucination, Technical Clarity for Readers, Modular and Reproducible Architecture, Test-First for Critical Components, Security and Configuration Management) and added specific sections for Book Standards, RAG Chatbot Standards, and Development Workflow. Updated dependent templates to align with the new constitution principles.

## Outcome

- ✅ Impact: Created project constitution and updated templates to align with project principles
- 🧪 Tests: N/A
- 📁 Files: Updated constitution.md and 3 template files
- 🔁 Next prompts: Plan and spec creation for book and RAG system
- 🧠 Reflection: Constitution now properly reflects the specific requirements of the AI-Spec-Driven Book with RAG Chatbot project

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin creating feature specifications