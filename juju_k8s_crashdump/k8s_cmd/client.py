# Copyright 2024-2025 Canonical Ltd.
# See LICENSE file for licensing details.



import yaml

from juju_k8s_crashdump.cmd import CmdArg, CmdClient
from juju_k8s_crashdump.k8s import KubectlClient


class KubectlCmdClient(KubectlClient):
    cmd_client: CmdClient
    kubeconf: str

    def __init__(self, kubeconf, cmd_client: CmdClient = None):
        self.kubeconf = kubeconf
        self.cmd_client = cmd_client if cmd_client is not None else CmdClient()

    def _call_kubectl(self, *args: list[CmdArg]) -> str:
        return self.cmd_client.call(
                CmdArg(value="kubectl"),
                CmdArg(value=self.kubeconf, name="kubeconfig"),
                *args)

    def get_resources(self, namespace: str, resource: str) -> list[str]:
        return [res["metadata"]["name"] for res in yaml.safe_load(
                self._call_kubectl(
                    CmdArg(value="get"),
                    CmdArg(value=resource),
                    CmdArg(value=namespace, name="namespace"),
                    CmdArg(value="yaml", name="output")
                )
            )["items"]]

    def describe_resource(self, namespace: str, resource: str, name: str) -> str:
        return self._call_kubectl(
                CmdArg(value="describe"),
                CmdArg(value=resource),
                CmdArg(value=name),
                CmdArg(value=namespace, name="namespace")
            )

    def pod_logs(self, namespace: str, name: str) -> str:
        return self._call_kubectl(
                CmdArg(value="logs"),
                CmdArg(value=name),
                CmdArg(value=namespace, name="namespace"),
                CmdArg(name="all-containers")
            )
