## Overview

Reaction Platform is a customizable, real-time, reactive commerce solution.
This repository is the quickest way to get started with [Reaction][10] and its
supporting services in a local development environment.

## Features

* An ultra modern, enterprise-ready, real-time commerce platform.
* A microservices based architecture.
* Docker based development environment.
* Launched and configured with a single CLI command.

## Prerequisites

* [GNU Make](https://www.gnu.org/software/make/)
  * MacOS and linux users will have a suitable version bundled with the OS
* Bourne Shell and POSIX tools (sh, grep, sed, awk, etc)
  * MacOS and linux users will have a suitable version bundled with the OS
* [Git][5]
* [Docker][0] | [Docker for Mac][1] | [Docker for Windows][2]
* [Node.js][3]
* [Yarn][4]
* A [GitHub][6] account with a [configured SSH key][7]

## Getting started

Clone this repository, and then run `make` in the `reaction-platform` directory. If all goes well, it will take some time to download and start all of the components, but when it's done you'll have the entire Reaction application running on your computer through Docker. Individual services are cloned as child directories within this project.

```sh
git clone git@github.com:reactioncommerce/reaction-platform.git
cd reaction-platform
make
```

Behind the scenes `make` is

* checking that dependencies are present
* cloning sub-projects from GitHub
* downloading Docker images
* starting services

These services will be running when the initial `make` command is complete:

| Service                                             | Description                                                                                                                                                                                         |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [OAuth2 Server (Hydra)][12] (http://localhost:4444) | [ORY Hydra][11] OAuth2 token server.                                                                                                                                                                |
| [Reaction Identity][16] (http://localhost:4100)     | The OAuth2-compatible user interface for Reaction identity, such as login and registration.                                                                                                         |
| [Reaction API][10] (http://localhost:3000)          | The Reaction API, which includes [a GraphQL endpoint](http://localhost:3000/graphql-beta). See [GraphQL Playground](https://www.apollographql.com/docs/apollo-server/features/graphql-playground/). |
| [Reaction Admin][17] (http://localhost:4080)        | A user interface for administrators and shop managers to configure shops, manage products, and process orders.                                                                                      |
| [Example Storefront][13] (http://localhost:4000)    | An example Reaction storefront UI built with [Next.JS](https://github.com/zeit/next.js/).                                                                                                           |

If the `make` command fails at some point, you can run or rerun it for specific services with:

```sh
make init-<project-name>
```

Example:

```sh
make init-example-storefront
```

## Project Commands

These are the available `make` commands in the `reaction-platform` root directory.

| Command                                                 | Description                                                                                                                                     |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| `make`                                                  | Bootstraps the entire Reaction development environment in Docker.                                                                               |
| `make init-<project-name>`                              | Example: `make init-example-storefront`. Does clone/setup for a single project.                                                                 |
| `make stop`                                             | Stops all containers.                                                                                                                           |
| `make stop-<project-name>`                              | Example: `make stop-example-storefront`. Stops all containers for a single project.                                                             |
| `make start`                                            | Starts all containers.                                                                                                                          |
| `make start-<project-name>`                             | Example: `make start-example-storefront`. Starts all containers for a single project.                                                           |
| `make rm`                                               | Removes all containers. Volumes are not removed.                                                                                                |
| `make rm-<project-name>`                                | Example: `make rm-example-storefront`. Removes all containers for a single project. Volumes are not removed.                                    |
| `make checkout-<project-name> <git-tag-or-branch-name>` | Example: `make checkout-example-storefront release-v3.0.0`. Does `git checkout` for a sub-project. See "Running Particular Git Branches" below. |
| `make clean`                                            | Removes all containers, networks, and volumes. Any volume data will be lost.                                                                    |
| `make clean-<project-name>`                             | Example: `make clean-example-storefront`. Removes all containers, networks, and volumes for a single project. Any volume data will be lost.     |

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

To ensure they start quickly, all Reaction projects are configured (in their `docker-compose.yml` file) to run from the latest published Docker image. This means that if you change code files, you will not see your changes reflected in the running application. To switch over to development mode for a single project:

```sh
# Stop the project
make stop-<project-name>

# Create a Docker Compose override file for the project
ln -s ./<project-name>/docker-compose.dev.yml ./<project-name>/docker-compose.override.yml

# Start the project
make start-<project-name>
```

If you run into trouble with the above steps, `make clean-<project-name>` and then `make init-<project-name>`.

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

Platform networks in the Docker environment should be named as
`*.reaction.localhost`. The `localhost` TLD is reserved and guaranteed to not
conflict with a real TLD.

### Network List

| Network                    | Description                                                         |
|----------------------------|---------------------------------------------------------------------|
| api.reaction.localhost     | GraphQL and API traffic between services                            |
| auth.reaction.localhost    | Authentication and authorization services                           |
| streams.reaction.localhost | Streams and databases                                               |
| reaction.localhost         | General purpose. We are moving toward having only this one network. |

## Documentation

You may refer to each sub-project's README for additional operation details.

| Sub-project          | Documentation                             |
|----------------------|-------------------------------------------|
| `reaction`           | [Reaction Documentation][14]              |
| `reaction-hydra`     | [`reaction-hydra`][12], [`ory/hydra`][11] |
| `example-storefront` | [Example Storefront docs][15]             |

For tips on developing on Docker, read our [Docker docs](https://docs.reactioncommerce.com/docs/installation-docker-development).

## License

Copyright © [GNU General Public License v3.0](./LICENSE.md)

[0]: https://www.docker.com/get-docker "Docker"
[1]: https://www.docker.com/docker-mac "Docker for Mac"
[2]: https://www.docker.com/docker-windows "Docker for Windows"
[3]: https://nodejs.org "NodeJS"
[4]: https://yarnpkg.com/en/docs/install "Yarn"
[5]: https://git-scm.com/ "Git"
[6]: https://github.com/ "GitHub"
[7]: https://github.com/settings/keys "GitHub SSH Keys"
[8]: https://github.com/reactioncommerce/reaction-platform "Reaction Platform"
[9]: https://github.com/graphcool/graphql-playground "GraphQL Playground"
[10]: https://github.com/reactioncommerce/reaction "Reaction API"
[11]: https://github.com/ory/hydra "ORY Hydra"
[12]: https://github.com/reactioncommerce/reaction-hydra "Reaction Hydra"
[13]: https://github.com/reactioncommerce/example-storefront "Example Storefront"
[14]: https://docs.reactioncommerce.com "Reaction Documentation"
[15]: https://github.com/reactioncommerce/example-storefront/tree/master/docs "Example Storefront docs"
[16]: https://github.com/reactioncommerce/reaction-identity "Reaction Identity"
[17]: https://github.com/reactioncommerce/reaction-admin "Reaction Admin"
