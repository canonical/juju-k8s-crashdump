# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod


class JujuClient(ABC):
    @abstractmethod
    def models(self, controller: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def status_string(self, controller: str, model: str, format: str = "tabular") -> str:
        raise NotImplementedError

    @abstractmethod
    def debug_log(self, controller: str, model: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def bundle_string(self, controller: str, model: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def dump_db(self, controller: str, model: str, format: str = "yaml") -> str:
        raise NotImplementedError

    @abstractmethod
    def status_log(
        self, controller: str, model: str, entity_type: str, entity_name: str, format: str = "tabular"
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def storage_string(self, controller: str, model: str, format: str = "tabular") -> str:
        raise NotImplementedError
