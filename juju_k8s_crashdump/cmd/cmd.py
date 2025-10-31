# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os
import subprocess
import time
from datetime import timedelta
from typing import Optional

from pydantic import field_validator
from pydantic.dataclasses import dataclass


@dataclass
class CmdArg:
    value: Optional[str] = None
    name: Optional[str] = None

    @field_validator("value", "name", mode="before")
    @staticmethod
    def to_string(value):
        return str(value)


class CmdError(RuntimeError):
    def __init__(self, command: str, return_code: int, stdout: str = "", stderr: str = ""):
        super().__init__(f"Command '{command}' exited with return code '{return_code}', stderr: {stderr}")

        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


class CmdClient:
    retry_count: int
    retry_delay: timedelta

    def __init__(self, retry_count: int = 0, retry_delay: timedelta = timedelta(seconds=1)):
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    def call(self, *args: list[CmdArg], environment: dict[str, str] | None = None) -> str:
        # Copy existing environment if environment is passed
        if environment is not None:
            environment = {**os.environ.copy(), **environment}

        # Parse the arguments
        parsed_args = self.parse_args(*args)

        # Run the command with retries
        for attempt in range(self.retry_count + 1):
            result = subprocess.run(parsed_args, capture_output=True, text=True, env=environment)

            if result.returncode == 0:
                break

            if attempt < self.retry_count:
                time.sleep(self.retry_delay.total_seconds())
            else:
                raise CmdError(" ".join(parsed_args), result.returncode, stdout=result.stdout, stderr=result.stderr)

        return result.stdout

    def parse_args(self, *args: list[CmdArg]) -> list[str]:
        results = []
        for arg in args:
            if arg.name is not None:
                results.append(f"--{arg.name}")
            if arg.value is not None:
                results.append(arg.value)
        return results
