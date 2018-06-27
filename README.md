## Overview

This project is the foundation for the next generation of Reaction Commerce
software.

## Features

* A microservices based architecture.
* Docker based development environment.
* Services are pre-wired and ready to run locally with a single CLI command.

### Project Structure

Reaction NEXT is build upon a microservices architecture. The
[reaction-next][8] project is a shell that contains build tools to bootstrap
the environment.

Each microservice will be cloned as a child directory within this project.

## Prerequisites

* [Git][5]
* [Docker][0] | [Docker for Mac][1] | [Docker for Windows][2]
* [NodeJS][3]
* [Yarn][4]
* A [Github][6] account with a [configured SSH key][7]

## Getting started

First, clone this repository.

```sh
git clone git@github.com:reactioncommerce/reaction-next.git

cd reaction-next
```

#### Bootstrapping

From within the project directory run:

```sh
make
```

This process may take some time. Behind the scenes `make` is

* checking that dependencies are present
* cloning the sub projects
* downloading Docker images
* building custom, project Docker images
* starting services

## Networks

User-defined Docker networks are used to connect the Reaction services that run
as separate Docker Compose projects. With this configuration, each of the
project Docker Compose files should be able to launch independently though
errors are possible if a service dependency is not available.

### Strategy

The Docker environment should run as `*.reaction.localhost`. The `localhost`
TLD is reserved and guaranteed to not conflict with a real TLD.

Please use this convention for all networks created in the future. We do have
some existing networks that are named like this and should work to transition
them.

### Network List

| Network                    | Description                                    |
| -------------------------- | ---------------------------------------------- |
| reaction-api               | GraphQL and API traffic between services.      |
| reaction-auth              | Access to identity and authorization services. |
| streams.reaction.localhost | Network for Confluent and Kafka communication. |

## Services

When the initial `make` command is complete you can use these services:

| Service                                             | Description                                                                                                                  |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| [GraphiQL](http://localhost:3030/graphiql)          | The [GraphiQL](https://github.com/graphql/graphiql) interface for GraphQL interaction.                                       |
| [Confluent Control Center](http://localhost:9021)   | [Confluent Control Center](https://docs.confluent.io/current/control-center/docs/index.html)                                 |
| Confluent Kafka                                     | Confluent Kafka - Confluent's distribution of the Kafka streaming platform.                                                  |
| Confluent Schema Registry                           | Confluent Schema Registry - helps with storage and evolution of schemas.                                                     |
| Confluent Zookeeper                                 | Confluent's distribute of Zookeeper.                                                                                         |
| [Identity & Auth (Keycloak)](http://localhost:8080) | Administration interface for the Identity and Authorization service. Implemented with [Keycloak](https://www.keycloak.org/). |
| [Identity Demo Console](http://localhost:8000)      | A custom Keycloak console that demonstrates integration with a client-side app.                                              |
| [Reaction Devserver](http://localhost:3030)         | Development server for the Reaction [GraphQL](https://graphql.org/) backend.                                                 |
| [Reaction Meteor](http://localhost:3000)            | The Reaction Meteor application.                                                                                             |
| [Reaction Next Starterkit](http://localhost:4000)   | Reaction UI build on [Next.JS](https://github.com/zeit/next.js/).                                                            |

## Project Commands

These commands are used to control the system as a whole. Please refer to each
project README for details on that service.

Run these commands from the `reaction-next` project root directory.

| Command      | Description                                                                  |
| ------------ | ---------------------------------------------------------------------------- |
| `make`       | Boostraps the entire Reaction development environment in Docker.             |
| `make stop`  | Stops all containers.                                                        |
| `make start` | Starts all containers.                                                       |
| `make rm`    | Removes all containers. Volumes are not removed.                             |
| `make clean` | Removes all containers, networks, and volumes. Any volume data will be lost. |

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
[8]: https://github.com/reactioncommerce/reaction-next "Reaction NEXT"
[9]: https://github.com/graphcool/graphql-playground "GraphQL Playground"
