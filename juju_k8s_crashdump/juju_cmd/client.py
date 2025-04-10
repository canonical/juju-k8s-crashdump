# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.


import yaml

from juju_k8s_crashdump.cmd import CmdArg, CmdClient
from juju_k8s_crashdump.juju import JujuClient


class JujuCmdClient(JujuClient):
    cmd_client: CmdClient

    def __init__(self, cmd_client: CmdClient = None):
        self.cmd_client = cmd_client if cmd_client is not None else CmdClient()

    def _call_juju(self, *args: list[CmdArg], environment: dict[str, str] | None = None) -> str:
        return self.cmd_client.call(CmdArg(value="juju"), *args, environment=environment)

    def models(self, controller: str) -> list[str]:
        return [
            model["short-name"]
            for model in yaml.safe_load(
                self._call_juju(
                    CmdArg(value="models"),
                    CmdArg(value=controller, name="controller"),
                    CmdArg(value="yaml", name="format"),
                )
            )["models"]
        ]

    def status_string(self, controller: str, model: str, format: str = "tabular") -> str:
        return self._call_juju(
            CmdArg(value="status"),
            CmdArg(name="model", value=f"{controller}:{model}"),
            CmdArg(name="format", value=format),
            CmdArg(name="integrations") if format == "tabular" else CmdArg(),
        )

    def debug_log(self, controller: str, model: str) -> str:
        return self._call_juju(
            CmdArg(value="debug-log"),
            CmdArg(name="model", value=f"{controller}:{model}"),
            CmdArg(name="replay"),
            CmdArg(name="date"),
            CmdArg(name="no-tail"),
        )

    def bundle_string(self, controller: str, model: str) -> str:
        return self._call_juju(
            CmdArg(value="export-bundle"),
            CmdArg(name="model", value=f"{controller}:{model}"),
        )

    def dump_db(self, controller: str, model: str, format: str = "yaml") -> str:
        return self._call_juju(
            CmdArg(value="dump-db"),
            CmdArg(name="model", value=f"{controller}:{model}"),
            CmdArg(name="format", value=format),
            environment={"JUJU_DEV_FEATURE_FLAGS": "developer-mode"},
        )
