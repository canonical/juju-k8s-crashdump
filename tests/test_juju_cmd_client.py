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


def test_status_log_with_applications_and_units(
    juju_client,
    mock_cmd_client,
    app_log,
    unit_log,
):
    """Test status_log with both applications and units."""
    # Configure mock to return different values based on call
    mock_cmd_client.call.side_effect = [
        app_log,  # mysql application log
        app_log,  # prometheus application log
        unit_log,  # mysql/0 unit log
        unit_log,  # prometheus/0 unit log
        unit_log,  # prometheus/1 unit log
    ]

    application_names = ["mysql", "prometheus"]
    unit_names = ["mysql/0", "prometheus/0", "prometheus/1"]

    # Execute
    result = juju_client.status_log("test-controller", "test-model", application_names, unit_names, "tabular")

    # Verify content
    assert result["applications"]["mysql"] == app_log
    assert result["applications"]["prometheus"] == app_log
    assert result["units"]["mysql/0"] == unit_log
    assert result["units"]["prometheus/0"] == unit_log
    assert result["units"]["prometheus/1"] == unit_log
    # Verify correct number of calls
    assert mock_cmd_client.call.call_count == 5


def test_status_log_with_no_applications_or_units(juju_client):
    """Test status_log with no applications or units."""
    result = juju_client.status_log("test-controller", "test-model", [], [])

    assert "applications" in result
    assert "units" in result
    assert len(result["applications"]) == 0
    assert len(result["units"]) == 0


def test_status_log_with_no_units(juju_client, mock_cmd_client, app_log):
    """Test status_log with status that has applications but no units."""
    mock_cmd_client.call.side_effect = [
        app_log,
    ]

    result = juju_client.status_log("test-controller", "test-model", ["nginx"], [])

    assert "applications" in result
    assert "units" in result
    assert "nginx" in result["applications"]
    assert len(result["units"]) == 0
    assert result["applications"]["nginx"] == app_log
    assert mock_cmd_client.call.call_count == 1


def _assert_cmd_args_match(call_args, expected_args):
    assert len(call_args) == len(expected_args)
    for name, value in expected_args:
        assert any(arg.name == name and arg.value == value for arg in call_args)


def test_status_log_calls_with_correct_parameters(juju_client, mock_cmd_client, app_log, unit_log):
    """Test that show-status-log is called with correct parameters."""
    mock_cmd_client.call.side_effect = [
        app_log,
        app_log,
        unit_log,
        unit_log,
        unit_log,
    ]

    application_names = ["mysql", "prometheus"]
    unit_names = ["mysql/0", "prometheus/0", "prometheus/1"]

    juju_client.status_log("prod-controller", "my-model", application_names, unit_names, "yaml")

    # Get all the calls made to mock_cmd_client.call
    calls = mock_cmd_client.call.call_args_list

    expected_call_args = [
        [
            (None, "juju"),
            (None, "show-status-log"),
            ("model", "prod-controller:my-model"),
            ("format", "yaml"),
            ("type", "application"),
            (None, "mysql"),
        ],
        [
            (None, "juju"),
            (None, "show-status-log"),
            ("model", "prod-controller:my-model"),
            ("format", "yaml"),
            ("type", "application"),
            (None, "prometheus"),
        ],
        [
            (None, "juju"),
            (None, "show-status-log"),
            ("model", "prod-controller:my-model"),
            ("format", "yaml"),
            ("type", "unit"),
            (None, "mysql/0"),
        ],
        [
            (None, "juju"),
            (None, "show-status-log"),
            ("model", "prod-controller:my-model"),
            ("format", "yaml"),
            ("type", "unit"),
            (None, "prometheus/0"),
        ],
        [
            (None, "juju"),
            (None, "show-status-log"),
            ("model", "prod-controller:my-model"),
            ("format", "yaml"),
            ("type", "unit"),
            (None, "prometheus/1"),
        ],
    ]

    for i in range(5):
        _assert_cmd_args_match(calls[i][0], expected_call_args[i])
