#!/bin/env/python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
import os
import tarfile
from datetime import datetime, timedelta
from tempfile import TemporaryDirectory

from .cmd import CmdClient
from .juju import JujuClient
from .juju_cmd import JujuCmdClient
from .k8s import KubectlClient
from .k8s_cmd import KubectlCmdClient


def create_parser():
    parser = argparse.ArgumentParser(description="Collect logs for standard resources juju creates in kubernetes.")
    parser.add_argument("kubeconf", help="Path to a kubeconf with permissions to reach the resources juju creates.")
    parser.add_argument("controller", help="Name of the controller to get logs for.")
    parser.add_argument(
        "-o",
        "--output_path",
        help="full name and path for the output tar.gz, otherwise current directory and datetime will be used.",
        default=f"{os.getcwd()}/{datetime.now().strftime('%Y-%m-%d-%H.%M.%S')}.tar.gz",
    )
    return parser


def write_kubernetes_version_to_file(kubectl_client: KubectlClient, path: str):
    with open(f"{path}/kubernetes-version.txt", "w+") as f:
        f.write(kubectl_client.version_info_string())
    with open(f"{path}/kubernetes-version.yaml", "w+") as f:
        f.write(kubectl_client.version_info_string(format="yaml"))


def get_namespaces(juju_client: JujuClient, controller: str) -> list[str]:
    namespaces = [f"controller-{controller}"]
    for model in juju_client.models(controller):
        if "controller" in model:
            continue
        namespaces.append(model)
    return namespaces


def write_resource_info_to_file(kubectl_client: KubectlClient, namespace: str, resource_type: str, path: str):
    for name in kubectl_client.get_resources(namespace, resource_type):
        with open(f"{path}/describe-{name}.txt", "w+") as f:
            f.write(kubectl_client.describe_resource(namespace, resource_type, name))
        if resource_type == "pod":
            with open(f"{path}/{name}.log", "w+") as f:
                f.write(kubectl_client.pod_logs(namespace, name))


def write_juju_model_info_to_file(juju_client: JujuClient, controller: str, model: str, path: str):
    with open(f"{path}/juju-status.txt", "w+") as f:
        f.write(juju_client.status_string(controller, model))
    with open(f"{path}/juju-status.yaml", "w+") as f:
        f.write(juju_client.status_string(controller, model, format="yaml"))
    with open(f"{path}/debug-log.txt", "w+") as f:
        f.write(juju_client.debug_log(controller, model))
    with open(f"{path}/bundle.yaml", "w+") as f:
        try:
            bundle_string = juju_client.bundle_string(controller, model)
        except Exception as e:
            bundle_string = str(e)
        f.write(bundle_string)
    with open(f"{path}/db-dump.yaml", "w+") as f:
        f.write(juju_client.dump_db(controller, model, format="yaml"))

    status_logs = juju_client.status_log(controller, model)
    for application in status_logs["applications"]:
        with open(f"{path}/status-log/applications/{application}.txt", "w+") as f:
            f.write(status_logs["applications"][application])
    for unit in status_logs["units"]:
        with open(f"{path}/status-log/units/{unit}.txt", "w+") as f:
            f.write(status_logs["units"][unit])

    yaml_status_logs = juju_client.status_log(controller, model, format="yaml")
    for application in yaml_status_logs["applications"]:
        with open(f"{path}/status-log/applications/{application}.yaml", "w+") as f:
            f.write(yaml_status_logs["applications"][application])
    for unit in yaml_status_logs["units"]:
        with open(f"{path}/status-log/units/{unit}.yaml", "w+") as f:
            f.write(yaml_status_logs["units"][unit])


def os_mkdir(path: str):
    os.mkdir(path)
    return path


def write_tar(tar_path: str, directory: str):
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(directory, arcname="")


def main():
    parser = create_parser()
    args = parser.parse_args()
    cmd_client = CmdClient(retry_count=5, retry_delay=timedelta(seconds=5))
    juju_client = JujuCmdClient(cmd_client=cmd_client)
    kubectl_client = KubectlCmdClient(args.kubeconf, cmd_client=cmd_client)
    with TemporaryDirectory() as tempdir:
        write_kubernetes_version_to_file(kubectl_client, tempdir)
        for namespace in get_namespaces(juju_client, args.controller):
            namespace_dir = os_mkdir(f"{tempdir}/{namespace}")
            for resource_type in ["pod", "replicaset", "deployment", "statefulset", "pvc", "service"]:
                resource_dir = os_mkdir(f"{namespace_dir}/{resource_type}")
                write_resource_info_to_file(kubectl_client, namespace, resource_type, resource_dir)
            if not namespace.startswith("controller-"):
                status_log_dir = os_mkdir(f"{namespace_dir}/status-log")
                os_mkdir(f"{status_log_dir}/applications")
                os_mkdir(f"{status_log_dir}/units")
                write_juju_model_info_to_file(juju_client, args.controller, namespace, namespace_dir)
        write_tar(args.output_path, tempdir)
    print(f"Log tarfile written to {args.output_path}")


if __name__ == "__main__":
    main()
