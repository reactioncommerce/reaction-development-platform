# v2.0.0
This is our first release of Reaction Platform.

Reaction is API-first, real-time commerce engine built using Node.js, React, and GraphQL. It’s the second major release of our open source commerce software.

This release is coordinated with [Reaction](https://github.com/reactioncommerce/reaction), our [Example Storefront](https://github.com/reactioncommerce/example-storefront) (previously Storefront Starter Kit) and [reaction-hydra](https://github.com/reactioncommerce/reaction-hydra).

Reaction v2.0.0 is built as a truly headless commerce platform that decouples the Reaction backend services from the frontend. We’ve decoupled the storefront application from the API. Reaction platform now consists of the `reaction` project, which is now primarily our GraphQL API, along with our [Example Storefront](https://github.com/reactioncommerce/example-storefront), which integrates with the Reaction application via GraphQL API to provide a customer-facing storefront.

### New documentation
See [this page](https://github.com/reactioncommerce/reaction-docs/releases/tag/v2.0.0) for a non-comprehensive list of new and updated docs.

Some highlights:
- A [Storefront UI Development guide](https://docs.reactioncommerce.com/docs/next/storefront-intro) answering "How do I build a storefront for Reaction or adapt my storefront to get its data from Reaction, without starting from an example app"
- Helpful info about [GraphQL Resolvers](https://docs.reactioncommerce.com/docs/graphql-resolvers-file-structure) and [extending GraphQL to add a field](https://docs.reactioncommerce.com/docs/how-to-extend-graphql-to-add-field)
- A guide for [“How To Extend the Product Schema”](https://docs.reactioncommerce.com/docs/how-to-extend-product)


### OS notes
**Support for Windows.**
`[reaction-platform](https://github.com/reactioncommerce/reaction-platform)` is not compatible with Windows and has not been fully tested on Windows at this time.

**MacOS and Linux are supported.**
Reaction will support development in a dockerized environment and will focus on tooling and documentation for installation and configuration on the macOS and Linux OSes.

### We've adopted the DCO
We've adopted the [Developer Certificate of Origin (DCO)](https://developercertificate.org/) in lieu of a Contributor License Agreement for all contributions to Reaction Commerce open source projects. We request that contributors agree to the terms of the DCO and indicate that agreement by signing all commits made to Reaction Commerce projects by adding a line with your name and email address to every Git commit message contributed:
```
Signed-off-by: Jane Doe <jane.doe@example.com>
```

You can sign your commit automatically with Git by using `git commit -s` if you have your `user.name` and `user.email` set as part of your Git configuration.

We ask that you use your real name (please no anonymous contributions or pseudonyms). By signing your commit you are certifying that you have the right have the right to submit it under the open source license used by that particular Reaction Commerce project. You must use your real name (no pseudonyms or anonymous contributions are allowed.)

We use the [Probot DCO GitHub app](https://github.com/apps/dco) to check for DCO signoffs of every commit. If you forget to sign your commits, the DCO bot will remind you and give you detailed instructions for how to amend your commits to add a signature.

We're following in the footsteps of several other open source projects in adopting the DCO such as [Chef](https://blog.chef.io/2016/09/19/introducing-developer-certificate-of-origin/), [Docker](https://blog.docker.com/2014/01/docker-code-contributions-require-developer-certificate-of-origin/), and [GitLab](https://about.gitlab.com/2017/11/01/gitlab-switches-to-dco-license/)

### Share your feedback
We want to hear from you! Here are some good ways to get in touch.
- Want to request a new feature for Reaction? There’s now a Reaction repo just for [new feature requests](https://github.com/reactioncommerce/reaction-feature-requests).
- Reaction engineers and community engineers and developers are always collaborating in our [Gitter chat channel](https://gitter.im/reactioncommerce/reaction)
- Ask Us Anything! Watch this space for details about an upcoming Community Q&A session with the Reaction team.


# v2.0.0-rc.12
This is our fourth official release candidate for this project. This project should be considered pre-release until we've released the final 2.0.0 version.

# v2.0.0-rc.11
This is our third official release candidate for this project. This project should be considered pre-release until we've released the final 2.0.0 version.

# v2.0.0-rc.10
This is our second official release candidate for this project. This project should be considered pre-release until we've released the final 2.0.0 version.

# v2.0.0-rc.9
This is our first official release candidate for this project - we're going to be synchronizing releases across the differents parts of the Reaction Commerce ecosystem, so that's why we're starting with rc.9. This project should be considered pre-release until we've released the final 2.0.0 version.
