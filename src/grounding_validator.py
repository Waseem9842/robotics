from typing import List, Dict, Any
import re


def validate_response_grounding(response: str, retrieved_context: List[Dict[str, Any]]) -> bool:
    """
    Validate that the response is grounded in the retrieved context
    """
    if not retrieved_context:
        return False

    # Check if the response contains information that can be found in the retrieved context
    response_lower = response.lower()

    # Look for evidence of grounding by checking if key phrases from context appear in response
    for context_item in retrieved_context:
        content = context_item.get("content", "").lower()
        if content and content in response_lower:
            return True

    # If direct content matching fails, check for semantic similarity or related terms
    # This is a simplified check - in practice you might use more sophisticated NLP techniques
    for context_item in retrieved_context:
        content = context_item.get("content", "")
        # Extract key terms from context
        key_terms = extract_key_terms(content)
        if any(term.lower() in response_lower for term in key_terms if len(term) > 3):
            return True

    return False


def extract_key_terms(text: str) -> List[str]:
    """
    Extract key terms from text for grounding validation
    """
    # Simple approach: extract capitalized words, numbers, and important terms
    # In practice, you might use NER, keyword extraction algorithms, etc.
    import re

    # Find capitalized words (potential entities)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)

    # Find numbers and terms with special characters
    other_terms = re.findall(r'\b\w+\b', text)

    # Filter for potentially important terms
    key_terms = [term for term in capitalized_words + other_terms
                 if len(term) > 2 and term.lower() not in
                 ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'men', 'run', 'too', 'any', 'big', 'end', 'far', 'got', 'hot', 'let', 'lot', 'put', 'say', 'she', 'try', 'use', 'way', 'why', 'ask', 'boy', 'got', 'new', 'old', 'way', 'use']]

    return key_terms


def filter_response_by_context(response: str, retrieved_context: List[Dict[str, Any]]) -> str:
    """
    Filter the response to ensure it only contains information from the retrieved context
    """
    if not retrieved_context:
        return "I cannot answer this question as no relevant context was found."

    # Validate that response is grounded
    if validate_response_grounding(response, retrieved_context):
        return response
    else:
        # If not properly grounded, return a safe response
        return "I cannot provide a response that is fully grounded in the retrieved context."