# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import MagicMock

import pytest

from juju_k8s_crashdump.cmd import CmdClient
from juju_k8s_crashdump.juju_cmd.client import JujuCmdClient


@pytest.fixture
def mock_cmd_client():
    """Fixture for a mocked CmdClient."""
    return MagicMock(spec=CmdClient)


@pytest.fixture
def juju_client(mock_cmd_client):
    """Fixture for JujuCmdClient with mocked CmdClient."""
    return JujuCmdClient(cmd_client=mock_cmd_client)


@pytest.fixture
def app_log():
    """Fixture: Mock show-status-log output for generic application."""
    return """Time                        Type         Status   Message
15 Mar 2023 14:22:18+00:00  application  unset
15 Mar 2023 14:22:41+00:00  application  waiting  installing agent
15 Mar 2023 14:23:13+00:00  application  active"""


@pytest.fixture
def unit_log():
    """Fixture: Mock show-status-log output for generic unit."""
    return """Time                        Type       Status       Message
15 Mar 2023 14:22:40+00:00  juju-unit  allocating
15 Mar 2023 14:22:40+00:00  workload   waiting      installing agent
15 Mar 2023 14:23:07+00:00  workload   waiting      agent initialising
15 Mar 2023 14:23:12+00:00  juju-unit  idle
15 Mar 2023 14:23:12+00:00  workload   running"""


def _assert_cmd_args_match(call_args, expected_args):
    assert len(call_args) == len(expected_args)
    for name, value in expected_args:
        assert any(arg.name == name and arg.value == value for arg in call_args)


def test_status_log_with_application(
    juju_client,
    mock_cmd_client,
    app_log,
):
    """Test status_log with application."""
    mock_cmd_client.call.return_value = app_log
    result = juju_client.status_log("test-controller", "test-model", "application", "mysql", "tabular")
    assert result == app_log


def test_status_log_with_unit(
    juju_client,
    mock_cmd_client,
    unit_log,
):
    """Test status_log with unit."""
    mock_cmd_client.call.return_value = unit_log
    result = juju_client.status_log("test-controller", "test-model", "unit", "mysql/0", "tabular")
    assert result == unit_log


def test_status_log_calls_with_correct_parameters(juju_client, mock_cmd_client, app_log):
    """Test that show-status-log is called with correct parameters."""
    mock_cmd_client.call.return_value = app_log

    juju_client.status_log("prod-controller", "my-model", "application", "mysql", "yaml")

    # Get the call made to mock_cmd_client.call
    call_args = mock_cmd_client.call.call_args[0]

    expected_args = [
        (None, "juju"),
        (None, "show-status-log"),
        ("model", "prod-controller:my-model"),
        ("format", "yaml"),
        ("type", "application"),
        (None, "mysql"),
    ]

    _assert_cmd_args_match(call_args, expected_args)
