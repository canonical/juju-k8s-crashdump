#!/bin/env/python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
import os
import tarfile
from datetime import datetime
from tempfile import TemporaryDirectory

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

def write_juju_status_to_file(juju_client: JujuClient, controller: str, model: str, path: str):
    with open(f"{path}/juju-status.txt", "w+") as f:
        f.write(juju_client.status_string(controller, model))
    with open(f"{path}/juju-status.yaml", "w+") as f:
        f.write(juju_client.status_string(controller, model, format="yaml"))


def os_mkdir(path: str):
    os.mkdir(path)
    return path


def write_tar(tar_path: str, directory: str):
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(directory, arcname="")


def main():
    parser = create_parser()
    args = parser.parse_args()
    juju_client = JujuCmdClient()
    kubectl_client = KubectlCmdClient(args.kubeconf)
    with TemporaryDirectory() as tempdir:
        for namespace in get_namespaces(juju_client, args.controller):
            namespace_dir = os_mkdir(f"{tempdir}/{namespace}")
            for resource_type in ["pod", "replicaset", "deployment", "statefulset", "pvc", "service"]:
                resource_dir = os_mkdir(f"{namespace_dir}/{resource_type}")
                write_resource_info_to_file(kubectl_client, namespace, resource_type, resource_dir)
            if not namespace.startswith("controller-"):
                write_juju_status_to_file(juju_client, args.controller, namespace, namespace_dir)
        write_tar(args.output_path, tempdir)
    print(f"Log tarfile written to {args.output_path}")


if __name__ == "__main__":
    main()
