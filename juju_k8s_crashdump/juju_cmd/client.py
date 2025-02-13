# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.


import yaml

from juju_k8s_crashdump.cmd import CmdArg, CmdClient
from juju_k8s_crashdump.juju import JujuClient


class JujuCmdClient(JujuClient):
    cmd_client: CmdClient

    def __init__(self, cmd_client: CmdClient = None):
        self.cmd_client = cmd_client if cmd_client is not None else CmdClient()

    def _call_juju(self, *args: list[CmdArg]) -> str:
        return self.cmd_client.call(CmdArg(value="juju"), *args)

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
