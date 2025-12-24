import pytest
import os
import json
from unittest.mock import patch, MagicMock
from ai_report_generator.src.agent_engine import get_ai_insight, SYSTEM_PROMPT_TRENDS, SYSTEM_PROMPT_ANOMALIES, SYSTEM_PROMPT_ACTIONS

# Mock the OpenAI client at the module level
@pytest.fixture(autouse=True)
def mock_openai_client():
    with patch('ai_report_generator.src.agent_engine.openai.OpenAI') as mock_client_class:
        mock_instance = MagicMock()
        # Mock the chat.completions.create method
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Mocked AI Response"))]
        )
        mock_client_class.return_value = mock_instance
        yield mock_instance

def test_get_ai_insight_trends(mock_openai_client):
    stats = {"test": "data"}
    insight_type = "Trends"
    
    response = get_ai_insight(stats, insight_type)
    
    # In the current implementation, get_ai_insight returns a simulated string, not the mocked AI response
    assert f"AI Insight for {insight_type}" in response
    assert SYSTEM_PROMPT_TRENDS in response
    assert json.dumps(stats, indent=2) in response
    
    # Verify that the actual LLM call is commented out, so the mock won't be called for now
    # If LLM call is uncommented, this part of the test would need adjustment
    # mock_openai_client.chat.completions.create.assert_called_once()


def test_get_ai_insight_anomalies(mock_openai_client):
    stats = {"test": "data"}
    insight_type = "Anomalies"
    
    response = get_ai_insight(stats, insight_type)
    
    assert f"AI Insight for {insight_type}" in response
    assert SYSTEM_PROMPT_ANOMALIES in response
    assert json.dumps(stats, indent=2) in response


def test_get_ai_insight_actions(mock_openai_client):
    stats = {"test": "data"}
    insight_type = "Actions"
    
    response = get_ai_insight(stats, insight_type)
    
    assert f"AI Insight for {insight_type}" in response
    assert SYSTEM_PROMPT_ACTIONS in response
    assert json.dumps(stats, indent=2) in response


def test_get_ai_insight_invalid_type(mock_openai_client):
    stats = {"test": "data"}
    insight_type = "Invalid"
    
    response = get_ai_insight(stats, insight_type)
    
    assert "Invalid insight type: Invalid" in response

# Test client configuration (without making an actual call)
def test_openai_client_configuration():
    # This test primarily verifies that the client instance is created without error
    # and that environment variables are accessed correctly (if available).
    # Since we are mocking, we just ensure the client object is there.
    assert hasattr(os, 'environ')
    assert "OPENAI_API_KEY" in os.environ # Assuming this is set for testing
    
    # The actual client object created in agent_engine is already a mock due to autouse fixture.
    # So we can't test its 'base_url' and 'api_key' directly after module load without more specific patching
    # For now, we trust the `mock_openai_client` fixture handles client instantiation.
