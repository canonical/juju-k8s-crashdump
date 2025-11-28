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
def status_with_apps_and_units():
    """Fixture: Dummy juju status with applications and units."""
    return """
applications:
  mysql:
    charm: mysql-k8s
    scale: 1
  prometheus:
    charm: prometheus-k8s
    scale: 2
units:
  mysql/0:
    workload-status:
      current: active
  prometheus/0:
    workload-status:
      current: active
  prometheus/1:
    workload-status:
      current: active
"""


@pytest.fixture
def status_with_only_apps():
    """Fixture: Dummy juju status with only applications."""
    return """
applications:
  nginx:
    charm: nginx-k8s
    scale: 1
units: {}
"""


@pytest.fixture
def status_empty():
    """Fixture: Empty juju status."""
    return """
applications: {}
units: {}
"""


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
    status_with_apps_and_units,
    app_log,
    unit_log,
):
    """Test status_log with both applications and units."""
    # Configure mock to return different values based on call
    mock_cmd_client.call.side_effect = [
        status_with_apps_and_units,  # First call to get status
        app_log,  # mysql application log
        app_log,  # prometheus application log
        unit_log,  # mysql/0 unit log
        unit_log,  # prometheus/0 unit log
        unit_log,  # prometheus/1 unit log
    ]

    # Execute
    result = juju_client.status_log("test-controller", "test-model", "tabular")

    # Verify structure
    assert "applications" in result
    assert "units" in result
    assert "mysql" in result["applications"]
    assert "prometheus" in result["applications"]
    assert "mysql/0" in result["units"]
    assert "prometheus/0" in result["units"]
    assert "prometheus/1" in result["units"]

    # Verify content
    assert result["applications"]["mysql"] == app_log
    assert result["applications"]["prometheus"] == app_log
    assert result["units"]["mysql/0"] == unit_log
    assert result["units"]["prometheus/0"] == unit_log
    assert result["units"]["prometheus/1"] == unit_log
    # Verify correct number of calls
    assert mock_cmd_client.call.call_count == 6


def test_status_log_with_empty_status(juju_client, mock_cmd_client, status_empty):
    """Test status_log with empty status (no applications or units)."""
    mock_cmd_client.call.side_effect = [
        status_empty,
    ]

    result = juju_client.status_log("test-controller", "test-model")

    assert "applications" in result
    assert "units" in result
    assert len(result["applications"]) == 0
    assert len(result["units"]) == 0
    assert mock_cmd_client.call.call_count == 1


def test_status_log_with_no_units(juju_client, mock_cmd_client, status_with_only_apps, app_log):
    """Test status_log with status that has applications but no units."""
    mock_cmd_client.call.side_effect = [
        status_with_only_apps,
        app_log,
    ]

    result = juju_client.status_log("test-controller", "test-model")

    assert "applications" in result
    assert "units" in result
    assert "nginx" in result["applications"]
    assert len(result["units"]) == 0
    assert result["applications"]["nginx"] == app_log
    assert mock_cmd_client.call.call_count == 2


def _check_call_args(call_args, expected_args):
    for name, value in expected_args:
        assert len(call_args) == len(expected_args)
        assert any(arg.name == name and arg.value == value for arg in call_args)


def test_status_log_calls_with_correct_parameters(
    juju_client, mock_cmd_client, status_with_apps_and_units, app_log, unit_log
):
    """Test that show-status-log is called with correct parameters."""
    mock_cmd_client.call.side_effect = [
        status_with_apps_and_units,
        app_log,
        app_log,
        unit_log,
        unit_log,
        unit_log,
    ]

    juju_client.status_log("prod-controller", "my-model", "yaml")

    # Get all the calls made to mock_cmd_client.call
    calls = mock_cmd_client.call.call_args_list

    expected_call_args = [
        [
            (None, "juju"),
            (None, "status"),
            ("model", "prod-controller:my-model"),
            ("format", "yaml"),
            (None, None),  # status call has an empty argument because format is not tabular
        ],
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

    for i in range(6):
        _check_call_args(calls[i][0], expected_call_args[i])
