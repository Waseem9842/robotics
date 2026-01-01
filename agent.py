import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from src.qdrant_client import retrieve_context_for_question
from src.config import config
from src.grounding_validator import validate_response_grounding, filter_response_by_context
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY=""

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

third_party_model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="mistralai/devstral-2512:free"
)
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@function_tool
def get_qdrant_context(query: str) -> Dict[str, Any]:
    """
    Retrieve context from Qdrant based on the query.
    This function is available as a tool for the agent.
    """
    try:
        top_k = config.top_k
        threshold = config.grounding_threshold

        context_items = retrieve_context_for_question(
            query,
            top_k=top_k,
            threshold=threshold
        )

        logger.info(f"Retrieved {len(context_items)} context items for query: {query[:50]}...")

        return {
            "success": True,
            "context_items": context_items,
            "message": f"Retrieved {len(context_items)} relevant context items"
        }
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        return {
            "success": False,
            "context_items": [],
            "message": f"Error retrieving context: {str(e)}"
        }


# Create the RAG agent with instructions and tools
rag_agent = Agent(
    name="RAG Assistant",
    instructions="""You are a helpful RAG (Retrieval-Augmented Generation) assistant.
    Your primary function is to answer questions based on retrieved context.
    When a user asks a question, you should use the get_qdrant_context tool to retrieve
    relevant information from the knowledge base. Then, answer the user's question
    based only on the retrieved context. Do not use any knowledge from your training data.
    If the retrieved context is insufficient to answer the question, let the user know.""",
    model=third_party_model,  # This will use the temperature from the config
    tools=[get_qdrant_context]
)


import asyncio
import concurrent.futures
from functools import partial

def process_question_with_agent(question: str) -> str:
    """
    Process a question using the OpenAI Agents SDK
    """
    logger.info(f"Processing question with agent: {question}")

    try:
        # Check if we're in an event loop already
        try:
            # This will raise RuntimeError if no event loop is running
            asyncio.get_running_loop()
            # If we get here, there's already a loop running
            # Run the agent in a separate thread to avoid the nested event loop issue
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Use partial to pass the question to the function
                future = executor.submit(_run_agent_in_thread, question)
                response = future.result()
        except RuntimeError:
            # No event loop running, we can run normally
            from agents import Runner
            result = Runner.run_sync(rag_agent, question)
            response = result.final_output

        return response
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        return f"Error processing your request: {str(e)}"


def _run_agent_in_thread(question: str) -> str:
    """Run the agent in a separate thread to avoid event loop conflicts"""
    from agents import Runner
    import asyncio

    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Use run_until_complete to run the async Runner in this thread's loop
        coro = Runner.run(rag_agent, question)
        result = loop.run_until_complete(coro)
        return result.final_output
    finally:
        loop.close()


def main():
    """
    Main function to run the RAG agent using OpenAI Agents SDK
    """
    print("RAG Agent with OpenAI Agents SDK and Qdrant Integration")
    print("Type 'quit' to exit\n")

    while True:
        try:
            question = input("Enter your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not question:
                print("Please enter a valid question.\n")
                continue

            response = process_question_with_agent(question)
            print(f"\nResponse: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    main()
