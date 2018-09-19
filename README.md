## Overview

Reaction Platform is a customizable, real-time, reactive commerce solution.
This repository is the quickest way to get started with [Reaction][10] and its
supporting services in a local development environment.

## Features

* An ultra modern, enterprise-ready, real-time commerce platform.
* A microservices based architecture.
* Docker based development environment.
* Launched and configured with a single CLI command.

### Project Structure

Reaction Platform is built with a microservices architecture. This project
provides the tooling to easily orchestrate the services in a local development
environment.

Platform services will be cloned as child directories within this project.

## Prerequisites

* [Git][5]
* [Docker][0] | [Docker for Mac][1] | [Docker for Windows][2]
* [Node.js][3]
* [Yarn][4]
* A [GitHub][6] account with a [configured SSH key][7]

## Getting started

First, clone this repository.

```sh
git clone git@github.com:reactioncommerce/reaction-platform.git

cd reaction-platform
```

#### Bootstrapping

From within the project directory run:

```sh
make
```

This process may take some time. Behind the scenes `make` is

* checking that dependencies are present
* cloning the sub projects from GitHub: [`reaction`][10], [`reaction-hydra`][12], and [`reaction-next-starterkit`][13]
* downloading Docker images
* building custom, project Docker images
* starting services

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

| Network                    | Description                                    |
| -------------------------- | ---------------------------------------------- |
| api.reaction.localhost     | GraphQL and API traffic between services.      |
| auth.reaction.localhost    | Authentication and authorization services.     |

## Services

These services will be running when the initial `make` command is complete:

| Service                                           | Description                                                                                  |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| [OAuth2 Server (Hydra)][12] (http://localhost:4444)    | [ORY Hydra][11] OAuth2 token server.                                                         |
| [Reaction Meteor][10] (http://localhost:3000)          | The Reaction Meteor application, which includes the server API and the Meteor UI client.                                                             |
| [Reaction NextJS Storefront][13] (http://localhost:4000) | A starter Reaction storefront UI built with [Next.JS](https://github.com/zeit/next.js/).                          |

### GraphQL Interface
After running `make start`, you should be able to explore the GraphQL API at http://localhost:3000/graphiql. See [GraphiQL docs](https://github.com/graphql/graphiql)

## Project Commands

These commands are used to control the system as a whole.

Run these commands from the `reaction-platform` project root directory.

| Command      | Description                                                                  |
| ------------ | ---------------------------------------------------------------------------- |
| `make`       | Boostraps the entire Reaction development environment in Docker.             |
| `make stop`  | Stops all containers.                                                        |
| `make start` | Starts all containers.                                                       |
| `make rm`    | Removes all containers. Volumes are not removed.                             |
| `make clean` | Removes all containers, networks, and volumes. Any volume data will be lost. |

## Documentation

You may refer to each sub-project's README for additonal operation details.

| Sub-project      | Documentation                                                                  |
| ------------ | ---------------------------------------------------------------------------- |
| `reaction`       | [Reaction Documentation][14]             |
| `reaction-hydra`  | [`reaction-hydra`][12], [`ory/hydra`][11]                                                        |
| `reaction-next-starterkit` | [Starterkit docs][15]

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
[10]: https://github.com/reactioncommerce/reaction "Reaction"
[11]: https://github.com/ory/hydra "ORY Hydra"
[12]: https://github.com/reactioncommerce/reaction-hydra "Reaction Hydra"
[13]: https://github.com/reactioncommerce/reaction-next-starterkit "Reaction Next.js Starterkit"
[14]: https://docs.reactioncommerce.com "Reaction Documentation"
[15]: https://github.com/reactioncommerce/reaction-next-starterkit/tree/master/docs "Starterkit docs"
