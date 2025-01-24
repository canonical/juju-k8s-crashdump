# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod


class KubectlClient(ABC):

    @abstractmethod
    def get_resources(self, namespace: str, resource: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def describe_resource(self, namespace: str, resource: str, name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def pod_logs(self, namespace: str, name: str) -> str:
        raise NotImplementedError
