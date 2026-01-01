# Research: URL Ingestion & Embedding Pipeline

## Decision: Project Structure and Dependencies
**Rationale**: Selected Python backend with uv project manager based on the user's specification requirements. The structure follows modular architecture principles from the constitution.

**Alternatives considered**:
- Poetry vs uv for project management (chose uv as specified in user input)
- Different embedding providers (Cohere chosen as specified in user input)
- Different vector databases (Qdrant Cloud chosen as specified in user input)

## Decision: URL Fetching and Content Extraction
**Rationale**: Using requests and BeautifulSoup for web scraping as they are standard, reliable libraries for fetching and parsing HTML content from deployed book URLs.

**Alternatives considered**:
- Selenium for JavaScript-heavy sites (overkill for Docusaurus sites)
- Scrapy for complex scraping (too heavy for simple content extraction)
- Playwright for dynamic content (unnecessary for static Docusaurus sites)

## Decision: Text Processing and Chunking
**Rationale**: Implementing text cleaning and chunking using standard Python libraries to ensure content is properly formatted for embedding generation.

**Alternatives considered**:
- Using LangChain's text splitters (decided to implement custom for better control)
- Different chunking strategies (fixed-size vs semantic - chose fixed-size for consistency)

## Decision: Embedding Generation with Cohere
**Rationale**: Using Cohere's embedding models as specified in the requirements, which provide reliable and high-quality vector representations.

**Alternatives considered**:
- OpenAI embeddings (not specified in requirements)
- Hugging Face models (self-hosted option, but Cohere was specified)
- Sentence Transformers (local option, but Cohere was specified)

## Decision: Qdrant Cloud Integration
**Rationale**: Using Qdrant Cloud as the vector database as specified in the requirements, providing managed vector storage with good performance characteristics.

**Alternatives considered**:
- Pinecone (alternative managed vector DB)
- Weaviate (open source alternative)
- Self-hosted Qdrant (managed option was specified)