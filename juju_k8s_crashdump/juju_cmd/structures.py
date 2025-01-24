# Copyright 2024-2025 Canonical Ltd.
# See LICENSE file for licensing details.

from juju_k8s_crashdump.serializeable_dataclass import serializeable_dataclass
from pydantic import Field


@serializeable_dataclass
class JujuStatus:
    @serializeable_dataclass
    class Application:
        @serializeable_dataclass
        class ApplicationStatus:
            current: str

        @serializeable_dataclass
        class Unit:
            @serializeable_dataclass
            class WorkloadStatus:
                current: str

            @serializeable_dataclass
            class JujuStatus:
                current: str

            workload_status: WorkloadStatus
            juju_status: JujuStatus

        charm: str
        application_status: ApplicationStatus
        units: dict[str, Unit] = Field(default_factory=dict)

    applications: dict[str, Application]
