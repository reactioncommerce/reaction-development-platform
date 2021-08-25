###############################################################################
### Reaction OSS v3.14.1
###
### See: `/config.mk` for documentation.
###############################################################################

# List of tools that must be installed.
# A simple check to determine the tool is available. No version check, etc.
define REQUIRED_SOFTWARE
docker \
docker-compose \
git \
node \
yarn
endef

# Defined here are the subprojects in a comma-separated format
# GIT_REPO_URL,SUBDIR_NAME,TAG
# GIT_REPO_URL is the URL of the git repository
# SUBDIR_NAME is just the directory name itself
# TAG is the git tag or branch to checkout
# Projects will be started in this order
define SUBPROJECT_REPOS
https://github.com/reactioncommerce/reaction-hydra.git,reaction-hydra,v3.0.0 \
https://github.com/reactioncommerce/reaction.git,reaction,v3.13.2 \
https://github.com/reactioncommerce/reaction-identity.git,reaction-identity,v3.3.1 \
https://github.com/reactioncommerce/reaction-admin.git,reaction-admin,v3.0.0-beta.19 \
https://github.com/reactioncommerce/example-storefront.git,example-storefront,v4.1.0
endef

# List of user defined networks that should be created.
define DOCKER_NETWORKS
reaction.localhost
endef
