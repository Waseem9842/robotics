import pytest
from unittest.mock import Mock, patch
from agent import process_question_with_agent, rag_agent, get_qdrant_context


class TestAgentFunctionality:
    """
    Unit tests for the agent functionality
    """

    def test_agent_creation(self):
        # Arrange & Act
        agent = rag_agent

        # Assert
        assert agent is not None
        assert agent.name == "RAG Assistant"

    def test_process_question_with_agent_exists(self):
        # Act & Assert
        # Check that the function exists and is callable
        assert callable(process_question_with_agent)

    @patch('agents.Runner.run_sync')
    def test_process_question_with_agent_success(self, mock_runner_run_sync):
        # Arrange
        mock_runner_run_sync.return_value.final_output = "This is the agent's response based on the context."

        # Act
        result = process_question_with_agent("Test question?")

        # Assert
        assert "response" in result
        mock_runner_run_sync.assert_called_once()

    @patch('agents.Runner.run_sync')
    def test_process_question_with_agent_error(self, mock_runner_run_sync):
        # Arrange
        mock_runner_run_sync.side_effect = Exception("Agent execution error")

        # Act
        result = process_question_with_agent("Test question?")

        # Assert
        assert "Error" in result

    def test_get_qdrant_context_tool_exists(self):
        # Assert
        # Check that the tool exists and is properly decorated
        assert get_qdrant_context is not None


if __name__ == "__main__":
    pytest.main([__file__])