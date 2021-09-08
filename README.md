## Overview

Reaction Platform is a customizable, real-time, reactive commerce solution. This repository is the quickest way to get started with the [Reaction API][10] and its supporting services in a local development environment.

## Features

- A modern, enterprise-ready, real-time commerce platform.
- A microservices based architecture.
- Docker based development environment.
- Launched and configured with a single CLI command.

## Prerequisites

- [GNU Make](https://www.gnu.org/software/make/)
  - MacOS and Linux users will have a suitable version bundled with the OS
- Bourne Shell and POSIX tools (sh, grep, sed, awk, etc)
  - MacOS and Linux users will have a suitable version bundled with the OS
- [Git][5]
- [Docker][0] | [Docker for Mac][1] | [Docker for Windows][2]
- A [GitHub][6] account with a [configured SSH key][7] is not required by
  default, but necessary when using custom, private Github repositories.

## Getting started

Clone this repository, and then run `make` in the `reaction-development-platform` directory. If all goes well, it will take some time to download and start all of the components, but when it's done you'll have the entire Reaction application running on your computer through Docker. Individual services are cloned as child directories within this project.

```sh
git clone git@github.com:reactioncommerce/reaction-development-platform.git
cd reaction-development-platform
make
```

Behind the scenes `make` is

- checking that dependencies are present
- cloning sub-projects from GitHub
- downloading Docker images
- starting services

These services will be running when the initial `make` command is complete:

| Service                                          | Description                                                                                                                                                                                    |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Reaction API][10] (http://localhost:3000)       | The Reaction API, which includes [a GraphQL endpoint](http://localhost:3000/graphql). See [GraphQL Playground](https://www.apollographql.com/docs/apollo-server/features/graphql-playground/). |
| [Reaction Admin][19] (http://localhost:4080)     | A user interface for administrators and shop managers to configure shops, manage products, and process orders.                                                                                 |
| [Example Storefront][13] (http://localhost:4000) | An example Reaction storefront UI built with [Next.JS](https://github.com/zeit/next.js/).                                                                                                      |

If the `make` command fails at some point, you can run or rerun it for specific services with:

```sh
make init-<project-name>
```

Example:

```sh
make init-example-storefront
```

## Migrating from v3.x.x to v4.x.x

Look at the detailed guide [here](docs/migration-guide-v4.md)

## Ongoing Support for v3.x

We'll continue to provide v3.x support for 6 months from the v4.0 release. That marks 3/1/2022 as the date when we officially end support to 3.x versions and below. Beyond that date we'll be fully dedicated to the new version and will not be taking any v3.x issues into discussion/development.

## Project Commands

These are the available `make` commands in the `reaction-platform` root directory.

| Command                                                 | Description                                                                                                                                                                    |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `make`                                                  | Bootstraps the entire Reaction development environment in Docker. Projects will use production Docker images and code.                                                         |
| `make init-<project-name>`                              | Example: `make init-example-storefront`. Does clone/setup for a single project.                                                                                                |
| `make init-dev`                                         | Bootstraps the entire Reaction development environment in Docker. Projects will use development configuration.                                                                 |
| `make init-dev-<project-name>`                          | Example: `make init-dev-example-storefront`. Does clone/setup for a single project and configures it with a development configuration.                                         |
| `make stop`                                             | Stops all containers.                                                                                                                                                          |
| `make stop-<project-name>`                              | Example: `make stop-example-storefront`. Stops all containers for a single project.                                                                                            |
| `make start`                                            | Starts all containers.                                                                                                                                                         |
| `make start-<project-name>`                             | Example: `make start-example-storefront`. Starts all containers for a single project.                                                                                          |
| `make dev-<project-name>`                               | Example: `make dev-example-storefront`. Starts all containers for a single project in development mode.                                                                        |
| `make dev-link`                                         | Creates `docker-compose.override.yml` symlinks for development in all projects.                                                                                                |
| `make dev-link-<project-name>`                          | Example: `make dev-link-example-storefront`. Creates development symlinks for a single project.                                                                                |
| `make dev-unlink`                                       | Removes `docker-compose.override.yml` symlinks from all projects.                                                                                                              |
| `make dev-unlink-<project-name>`                        | Example: `make dev-unlink-example-storefront`. Removes the `docker-compose.override.yml` symlink for a single project.                                                         |
| `make rm`                                               | Removes all containers. Volumes are not removed.                                                                                                                               |
| `make rm-<project-name>`                                | Example: `make rm-example-storefront`. Removes all containers for a single project. Volumes are not removed.                                                                   |
| `make checkout-<project-name> <git-tag-or-branch-name>` | Example: `make checkout-example-storefront release-v3.0.0`. Does `git checkout` for a sub-project. See "Running Particular Git Branches" below.                                |
| `make clean`                                            | Removes all containers, networks, and volumes. Any volume data will be lost.                                                                                                   |
| `make clean-<project-name>`                             | Example: `make clean-example-storefront`. Removes all containers, networks, and volumes for a single project. Any volume data will be lost.                                    |
| `make update-checkouts`                                 | Example: `make update-checkouts`. Updates git checkouts on all projects. Useful for syncing dev env to config file. Safe, fails on uncommitted changes.                        |
| `make update-checkout-<project-name>`                   | Example: `make update-checkout-example-storefront`. Checks out branch in config file and pulls. Useful for syncing dev env to config file. Safe, fails on uncommitted changes. |
| `make clone-api-plugins`                                | If you are going to make changes to the default plugins, this is a quick way to clone them all into an `api-plugins` subdirectory of this project.                             |

## Customizing Configuration

The development platform runs the latest version of Reaction by default, but
it's possible to select a specific version, or to customize an existing release
version.

### How Configuration Works

The Reaction development platform uses `make` to run tasks. `make` is aware of
the task dependency tree and ensures that all required dependencies are met
when running a task. The main tasks and functionality for `make` are
configured in `Makefile`.

Configurations that may change are extracted into `config.mk`. This file is
checked in to source control and should not be modified. It is always configured
for the latest Reaction release.

If a file named `config.local.mk` exists then it will be loaded after
`config.mk`. Settings in `config.local.mk` will override those set in
`config.mk`. It is ignored by source control.

### Running a Specific Reaction Release Version

Configurations for specific Reaction releases (since v3.0.0) are located in
`config/reaction-oss`. You may symlink or copy any release configuration to
`config.local.mk`.

For example, this command will configure the platform to run `v3.0.4`:

```sh
ln -s config/reaction-oss/reaction-v3.0.4.mk config.local.mk
make
```

### Running A Customized Installation

You may customize your Reaction installation by modifying `config.local.mk`.
It's easiest to start with an existing release configuration file and modify it
as needed. In this way you can:

- Add new sub-projects
- Remove sub-projects
- Update the git origin for a sub-project
- Change the default branch for a sub-project
- Customize the lifecycle hooks directory to run custom scripts for automation

Configuration files store in `config/local` are ignored by git. It's a
convenient place to store local files for quick development. If you are sharing
files with a team then you may want to keep your configuration files in a
separate git repository or in shared network storage.

The only requirement to override configuration is that you need to put a file
into place at `config.local.mk`, so it is possible to copy or symlink a file
from anywhere in your system.

Examples:

```sh
# Use a file in the config/local directory
ln -s config/local/my-custom-config.mk config.local.mk
make
```

```sh
# Use a file in the config/local directory
ln -s /path/on/my/system/reactionconfig.mk config.local.mk
make
```

### Updating Local Branches to Match Config

If you are using the Reaction development platform for development, then you
will need to update your local branch to get the latest at some point. The
`update-checkouts` command will perform this operation.

```
make update-checkouts
```

The command is safe. It will halt if there are uncommitted changes in
git before doing anything. You may commit, stash or drop those changes.

## Running Particular Git Branches

After you've done the "Getting Started" steps and have the latest Reaction system running, you may need to switch to and run a certain branch/tag in one or more of the sub-projects.

To check out and run a certain branch or tag for a project, stop the project, run `make checkout-<project-name> <git-tag-or-branch-name>`, and then init the project again.

Example:

```sh
make stop-example-storefront
make checkout-example-storefront release-v3.0.0
make init-example-storefront
```

If you're getting unexpected results, `cd` into the sub-project directory and do a `git pull` to verify you're on the latest commit from that branch. If you're changing code files, see the "Running From Code For Development" section below.

### Running From Code For Development

To ensure they start quickly, all Reaction projects are configured (in their `docker-compose.yml` file) to run from the latest published Docker image. This means that if you change code files, you will not see your changes reflected in the running application.

##### To install the whole platform in development mode:

Run `make init-dev` (instead of `make`).

Doing this takes time to install and will consume more resources.

##### To switch over to development mode for a single project:

```sh
make stop-<project-name>
make dev-link-<project-name>
make <start-project-name>
```

If you run into trouble with the above command, run `make clean-<project-name>` and then `make init-dev-<project-name>`.

##### To switch back to production mode for a single project:

```sh
make stop-<project-name>
make dev-unlink-<project-name>
make <start-project-name>
```

If you run into trouble with the above command, run `make clean-<project-name>` and then `make init-<project-name>`.

## Networked Services

User-defined Docker networks are used to connect the Reaction services that run
as separate Docker Compose projects. With this configuration, each of the
projects can be launched independently using Docker Compose.

While the projects can be launched independently they may have network
dependencies that are required to function correctly. The platform Makefile
will launch services for you if you start it all together. You are free to
manually start a single service but you will need to ensure dependencies are
running.

### Network Naming Strategy

All projects must list `reaction.localhost` as an external network in their docker-compose configuration. The `make` commands will ensure that this network exists. Choose a unique enough name for your service that you can be reasonably sure it won't conflict with another Reaction service.

When you need to communicate with one service from another over the internal Docker network, use `<service-name>.reaction.localhost` as the hostname.

## Documentation

You may refer to each sub-project's README for additional operation details.

| Sub-project                | Description        | Documentation                    |
| -------------------------- | ------------------ | -------------------------------- |
| [`reaction`][10]           | GraphQL API        | [Reaction API Documentation][14] |
| [`reaction-admin`][19]     | Classic Admin UI   | [Reaction Admin Readme][20]      |
| [`example-storefront`][13] | Example Storefront | [Example Storefront docs][15]    |

For tips on developing with Docker, read our [Docker docs](https://docs.reactioncommerce.com/docs/installation-docker-development).

## Latest Releases

The following table provides the most current version of each project used by this platform:

| Project                             | Latest release / tag                                                                     |
| ----------------------------------- | ---------------------------------------------------------------------------------------- |
| [reaction-development-platform][10] | [`4.0.1`](https://github.com/reactioncommerce/reaction-development-platform/tree/v4.0.1) |
| [reaction][10]                      | [`4.0.0`](https://github.com/reactioncommerce/reaction/tree/v4.0.0)                      |
| [example-storefront][13]            | [`5.0.3`](https://github.com/reactioncommerce/example-storefront/tree/v5.0.3)            |
| [reaction-admin (beta)][19]         | [`4.0.0-beta.5`](https://github.com/reactioncommerce/reaction-admin/tree/v4.0.0-beta.5)  |

### [Release Process](docs/release-guide.md)

### Developer Certificate of Origin

We use the [Developer Certificate of Origin (DCO)](https://developercertificate.org/) in lieu of a Contributor License Agreement for all contributions to Reaction Commerce open source projects. We request that contributors agree to the terms of the DCO and indicate that agreement by signing-off all commits made to Reaction Commerce projects by adding a line with your name and email address to every Git commit message contributed:

```
Signed-off-by: Jane Doe <jane.doe@example.com>
```

You can sign-off your commit automatically with Git by using `git commit -s` if you have your `user.name` and `user.email` set as part of your Git configuration.

We ask that you use your real full name (please no anonymous contributions or pseudonyms) and a real email address. By signing-off your commit you are certifying that you have the right to submit it under the [GNU GPLv3 Licensed](./LICENSE.md).

We use the [Probot DCO GitHub app](https://github.com/apps/dco) to check for DCO sign-offs of every commit.

If you forget to sign-off your commits, the DCO bot will remind you and give you detailed instructions for how to amend your commits to add a signature.

## License

Copyright © [GNU General Public License v3.0](./LICENSE.md)

[0]: https://www.docker.com/get-docker "Docker"
[1]: https://www.docker.com/docker-mac "Docker for Mac"
[2]: https://www.docker.com/docker-windows "Docker for Windows"
[5]: https://git-scm.com/ "Git"
[6]: https://github.com/ "GitHub"
[7]: https://github.com/settings/keys "GitHub SSH Keys"
[8]: https://github.com/reactioncommerce/reaction-platform "Reaction Platform"
[9]: https://github.com/graphcool/graphql-playground "GraphQL Playground"
[10]: https://github.com/reactioncommerce/reaction "Reaction API"
[13]: https://github.com/reactioncommerce/example-storefront "Example Storefront"
[14]: https://docs.reactioncommerce.com "Reaction Documentation"
[15]: https://github.com/reactioncommerce/example-storefront/tree/master/docs "Example Storefront docs"
[19]: https://github.com/reactioncommerce/reaction-admin "Reaction Admin"
[20]: https://github.com/reactioncommerce/reaction-admin/blob/trunk/README.md "Reaction Admin Readme"
[20]: https://github.com/reactioncommerce/api-migrations "API Migrations"
