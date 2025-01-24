#!/bin/env/python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
import os
import tarfile
from datetime import datetime
from tempfile import TemporaryDirectory

from .juju_cmd import JujuCmdClient
from .k8s_cmd import KubectlCmdClient


def create_parser():
    parser = argparse.ArgumentParser(description="Collect logs for standard resources juju creates in kubernetes")
    parser.add_argument("kubeconf", help="Path to a kubeconf with permissions to reach the resources juju creatres")
    parser.add_argument("controller", help="Name of the controller to get logs for")
    return parser


def get_namespaces(juju_client: JujuCmdClient, controller: str) -> list[str]:
    namespaces = [f"controller-{controller}"]
    for model in juju_client.models(controller):
        if "controller" in model:
            continue
        namespaces.append(model)
    return namespaces


def write_resource_info_to_file(kubectl_client: KubectlCmdClient, namespace: str, resource_type: str, path: str):
    for name in kubectl_client.get_resources(namespace, resource_type):
        with open(f"{path}/describe-{name}.txt", "w+") as f:
            f.write(kubectl_client.describe_resource(namespace, resource_type, name))
        if resource_type == "pod":
            with open(f"{path}/{name}.log", "w+") as f:
                f.write(kubectl_client.pod_logs(namespace, name))


def main():
    parser = create_parser()
    args = parser.parse_args()
    output_tar = f"{os.getcwd()}/{datetime.now().strftime('%Y-%m-%d-%H.%M.%S')}.tar.gz"

    juju_client = JujuCmdClient()
    kubectl_client = KubectlCmdClient(args.kubeconf)
    with TemporaryDirectory() as tempdir:
        for namespace in get_namespaces(juju_client, args.controller):
            namespace_dir = f"{tempdir}/{namespace}"
            os.mkdir(namespace_dir)
            for resource_type in ["pod", "replicaset", "deployment", "statefulset", "pvc", "service"]:
                resource_dir = f"{namespace_dir}/{resource_type}"
                os.mkdir(resource_dir)
                write_resource_info_to_file(kubectl_client, namespace, resource_type, resource_dir)
        with tarfile.open(output_tar, "w:gz") as tar:
            tar.add(tempdir)
    print(f"Log tarfile written to {output_tar}")


if __name__ == "__main__":
    main()
