"""Unit tests for the AgentEngineSandboxCodeExecutor configuration and execution."""

import pytest
from unittest.mock import MagicMock, patch

from app.agent import root_agent, SANDBOX_RESOURCE_NAME
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)
from google.adk.code_executors.base_code_executor import CodeExecutionInput


def test_agent_has_agent_engine_code_executor():
    assert root_agent.code_executor is not None
    assert isinstance(root_agent.code_executor, AgentEngineSandboxCodeExecutor)
    assert root_agent.code_executor.sandbox_resource_name == SANDBOX_RESOURCE_NAME
    assert "sandboxEnvironments" in root_agent.code_executor.sandbox_resource_name


def test_execute_code_mocked():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_output = MagicMock()
    mock_output.mime_type = "application/json"
    mock_output.metadata = None
    mock_output.data = b'{"msg_out": "42\\n", "msg_err": ""}'
    mock_response.outputs = [mock_output]
    mock_client.agent_engines.sandboxes.execute_code.return_value = mock_response

    executor = AgentEngineSandboxCodeExecutor(sandbox_resource_name=SANDBOX_RESOURCE_NAME)

    with patch.object(executor, "_get_api_client", return_value=mock_client):
        result = executor.execute_code(
            invocation_context=None,
            code_execution_input=CodeExecutionInput(code="print(42)"),
        )

        mock_client.agent_engines.sandboxes.execute_code.assert_called_once_with(
            name=SANDBOX_RESOURCE_NAME,
            input_data={"code": "print(42)"},
        )
        assert result.stdout == "42\n"
        assert result.stderr == ""
