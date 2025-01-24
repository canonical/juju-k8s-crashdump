# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod


class JujuClient(ABC):
    @abstractmethod
    def models(self, controller: str) -> list[str]:
        raise NotImplementedError
