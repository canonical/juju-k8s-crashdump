# Overview

A tool for dumping pod logs and describing k8s resources owned or created by a juju controller and
its models.

## Getting Started

This package can be installed via pip and then called as a command line tool

```
pipx install .

$ juju-k8s-crashdump --help
usage: juju-k8s-crashdump [-h] [-o OUTPUT_PATH] kubeconf controller

Collect logs for standard resources juju creates in kubernetes.

positional arguments:
  kubeconf              Path to a kubeconf with permissions to reach the
                        resources juju creatres.
  controller            Name of the controller to get logs for.

options:
  -h, --help            show this help message and exit
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        full name and path for the output tar.gz, otherwise
                        current directory and datetime will be used.
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information about development best practices.

## TODO

- [ ] Snap this project
- [ ] Adjust log tar to not have /var/tmpXXXXXX in the pathing
- [ ] Add unittests
- [ ] Add linting actions
- [ ] Use [COG](https://github.com/nedbat/cog) for readme formatting
