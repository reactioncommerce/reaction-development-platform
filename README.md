## Overview

Reaction Platform is a customizable, real-time, reactive commerce solution.
This repository is the quickest way to get started with [Reaction][10] and its
supporting services.

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
* [NodeJS][3]
* [Yarn][4]
* A [Github][6] account with a [configured SSH key][7]

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
* cloning the sub projects from Github
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

(Please use this convention for all networks created in the future. We do have
some existing networks that are not named like this and should work to transition
them.)

### Network List

| Network                    | Description                                    |
| -------------------------- | ---------------------------------------------- |
| reaction-api               | GraphQL and API traffic between services.      |
| auth.reaction.localhost    | Authentication and authorization services.     |

## Services

These services will be running when the initial `make` command is complete:

| Service                                           | Description                                                                                  |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| [GraphiQL](http://localhost:3030/graphiql)        | The [GraphiQL](https://github.com/graphql/graphiql) interface for GraphQL interaction.       |
| [OAuth2 Server (Hydra)](http://localhost:4444)    | [ORY Hydra][11] OAuth2 token server.                                                         |
| [Reaction Devserver](http://localhost:3030)       | Development server for the Reaction [GraphQL](https://graphql.org/) backend.                 |
| [Reaction Meteor](http://localhost:3000)          | The Reaction Meteor application.                                                             |
| [Reaction Next Starterkit](http://localhost:4000) | Reaction UI built with [Next.JS](https://github.com/zeit/next.js/).                          |

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

You may refer to each sub-project's README for additonal operation details.

## License

Copyright © [GNU General Public License v3.0](./LICENSE.md)

[0]: https://www.docker.com/get-docker "Docker"
[1]: https://www.docker.com/docker-mac "Docker for Mac"
[2]: https://www.docker.com/docker-windows "Docker for Windows"
[3]: https://nodejs.org "NodeJS"
[4]: https://yarnpkg.com/en/docs/install "Yarn"
[5]: https://git-scm.com/ "Git"
[6]: https://github.com/ "Github"
[7]: https://github.com/settings/keys "Github SSH Keys"
[8]: https://github.com/reactioncommerce/reaction-platform "Reaction Platform"
[9]: https://github.com/graphcool/graphql-playground "GraphQL Playground"
[10]: https://github.com/reactioncommerce/reaction "Reaction"
[11]: https://github.com/ory/hydra "ORY Hydra"
