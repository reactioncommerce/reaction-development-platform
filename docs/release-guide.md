# Release Guide

This guide assumes that you have the write access to the repositories and that you are using macOS.

## Prerequisite

1. Clone the repository in a separate folder using `git clone git@github.com:reactioncommerce/reaction-development-platform.git release-reaction-development-platform`
2. Use python3 to install the following libraries `semantic_version`, `gitpython`, `PyGithub`
3. Install [github command line](https://cli.github.com/) and [login](https://cli.github.com/manual/gh_auth_login)
4. Make sure all the remote links in the repos are of the format `git@github.com:reactioncommerce/...`. To check this:
   - `cd reaction`
   - `git remote -v`
   - To update use, `git remote set-url origin git@github.com:reactioncommerce/reaction.git`

## Release Process

1. Make sure you are on the trunk branch and have pulled the latest changes.
2. Run the script using `python3 release.py`.
3. Wait for the QA team to approve the PR.
4. Once approved, [create a new release](https://github.com/reactioncommerce/reaction-development-platform/releases/new) using the version and changelog from the PR in the above step.
5. Publish the release
