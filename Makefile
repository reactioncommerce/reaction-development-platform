#gnu makefile
# This Makefile provides macro control of the Reaction Platform microservice
# ecosystem. It performs tasks like:
#
#   * Verify dependencies are present
#   * Clone git projects, checkout a particular reference
#   * Preconfiguration and subproject bootstrapping
#   * Launching subprojects
#   * Teardown tasks with varying destructiveness
#
#
# Exit codes:
#
#   All failures should exit with a detailed code that can be used for
#   troubleshooting. The current exit codes are:
#
#     0: Success!
#   101: Github is not configured correctly.
#   102: Required dependency is not installed.
#

###############################################################################
### Common Configuration
###############################################################################
HOOK_DIR=.reaction/project-hooks

###############################################################################
### Loaded Configuration
### Load configuration from external files. Configuration variables defined in
### later files have precedent and will overwrite those defined in previous
### files. The -include directive ensures that no error is thrown if a file is
### not found, which is the case if config.local.mk does not exist.
###############################################################################
-include config.mk config.local.mk

SUBPROJECTS=$(foreach rr,$(SUBPROJECT_REPOS),$(shell echo $(rr) | cut -d , -f 2))


###############################################################################
### Tasks
###############################################################################
all: init

###############################################################################
### Init-Project
### Initializes a project in production mode.
### Does not do common tasks shared between projects.
###############################################################################
define init-template
init-$(1): $(1) network-create dev-unlink-$(1) prebuild-$(1) build-$(1) post-build-$(1) start-$(1) post-project-start-$(1)
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call init-template,$(p))))

###############################################################################
### Init-Dev-Project
### Initializes a project in development mode.
### Does not do common tasks shared between projects.
###############################################################################
define init-dev-template
init-dev-$(1): $(1) network-create dev-link-$(1) prebuild-$(1) build-$(1) post-build-$(1) start-$(1) post-project-start-$(1)
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call init-dev-template,$(p))))

###############################################################################
### Init-With-System
### Init project and run the post-system hook script. This is useful for
### initializing a single project.
### Assumes dependencies are already started.
###############################################################################
define init-with-system-template
init-with-system-$(1): init-$(1) post-system-start-$(1)
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call init-with-system-template,$(p))))

###############################################################################
### Init-Dev-with-System
### Init project and run the post-system hook script. This is useful for
### initializing a single project in development mode.
### Assumes dependencies are already started.
###############################################################################
define init-dev-with-system-template
init-dev-with-system-$(1): init-dev-$(1) post-system-start-$(1)
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call init-dev-with-system-template,$(p))))

.PHONY: init
init: $(foreach p,$(SUBPROJECTS),init-$(p)) post-system-start

.PHONY: init-dev
init-dev: $(foreach p,$(SUBPROJECTS),init-dev-$(p)) post-system-start

###############################################################################
### Targets to verify Github is configured correctly.
###############################################################################
github-configured: dependencies
	@(ssh -T git@github.com 2>&1 \
	  | grep "successfully authenticated" >/dev/null \
	  && echo "Github login verified.") \
	|| (echo "You need to configure an ssh key with access to github" \
	&& echo "See https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/ for instructions" \
	&& exit 101)


###############################################################################
### Verify prerequisite software is installed.
###############################################################################
is-not-installed=! (command -v $(1) >/dev/null)

define dependency-template
dependency-$(1):
	@if ( $(call is-not-installed,$(1)) ); \
	then \
	  echo "Dependency" $(1) " not found in path." \
	  && exit 102; \
	else \
	  echo "Dependency" $(1) "found."; \
	fi;
endef
$(foreach pkg,$(REQUIRED_SOFTWARE),$(eval $(call dependency-template,$(pkg))))

.PHONY: dependencies
dependencies: $(foreach pkg,$(REQUIRED_SOFTWARE),dependency-$(pkg))

###############################################################################
### Create Docker Networks
### Create all networks defined in the DOCKER_NETWORKS variable.
### Networks provide a way to loosely couple the projects and allow them to
### communicate with each other. We'll use dependencies on external networks
### rather than dependencies on other projects. Networks are lightweight and
### easy to create.
###############################################################################
define network-create-template
network-create-$(1):
	@docker network create "$(1)" || true
endef
$(foreach p,$(DOCKER_NETWORKS),$(eval $(call network-create-template,$(p))))

.PHONY: network-create
network-create: $(foreach p,$(DOCKER_NETWORKS),network-create-$(p))

###############################################################################
### Remove Docker Networks
### Remove all networks defined in the DOCKER_NETWORKS variable.
###############################################################################
define network-remove-template
network-remove-$(1):
	@docker network rm "$(1)" || true
endef
$(foreach p,$(DOCKER_NETWORKS),$(eval $(call network-remove-template,$(p))))

.PHONY: network-remove
network-remove: $(foreach p,$(DOCKER_NETWORKS),network-remove-$(p))

###############################################################################
### Git cloning
###############################################################################
define git-clone-template
$(2):
	if [ ! -d "$(2)" ] ; then \
	  git clone "$(1)" "$(2)"; \
	  cd $(2) && git checkout "$(3)"; \
	fi
endef
$(foreach rr,$(SUBPROJECT_REPOS),$(eval $(call git-clone-template,$(shell echo $(rr) | cut -d , -f 1),$(shell echo $(rr) | cut -d , -f 2),$(shell echo $(rr) | cut -d , -f 3))))

.PHONY: clone
clone: github-configured $(foreach p,$(SUBPROJECTS),$(p))

###############################################################################
### Git clone all API plugins
###############################################################################
.PHONY: clone-api-plugins
clone-api-plugins:
	if [ ! -d api-plugins ] ; then \
	  mkdir api-plugins; \
	fi; \
	cd api-plugins; \
	for repo in $(API_PLUGIN_REPOS); do \
		git clone $$repo || true; \
	done;

###############################################################################
### Git Verify Clean
### Checks that the project has a clean workspace and changes won't be lost.
###############################################################################
define git-ensure-clean-diff-template
git-ensure-clean-diff-$(2): $(2)
	@cd "$(2)" \
	  && git diff --stat --quiet \
	  || (echo "There are uncommitted changes in './$(2)'. Commit or discard changes before performing this operation."; exit 1)
endef
$(foreach rr,$(SUBPROJECT_REPOS),$(eval $(call git-ensure-clean-diff-template,$(shell echo $(rr) | cut -d , -f 1),$(shell echo $(rr) | cut -d , -f 2),$(shell echo $(rr) | cut -d , -f 3))))

.PHONY: git-ensure-clean-diff
git-ensure-clean-diff: $(foreach p,$(SUBPROJECTS),git-ensure-clean-diff-$(p))

###############################################################################
### Git checkout
### Checkout the branch configured in the platform settings.
### Does not gracefully deal with conflicts or other problems.
###############################################################################
define git-checkout-template
checkout-$(2): $(2)
	cd $(2) && git fetch && git checkout "$(3)"
endef
$(foreach rr,$(SUBPROJECT_REPOS),$(eval $(call git-checkout-template,$(shell echo $(rr) | cut -d , -f 1),$(shell echo $(rr) | cut -d , -f 2),$(shell echo $(rr) | cut -d , -f 3))))

.PHONY: checkout
checkout: clone $(foreach p,$(SUBPROJECTS),checkout-$(p))


###############################################################################
### Git Update Checkouts
### Will check out the configured branch for all projects. This can be used to
### get an installation in sync with the configuration file.
### Fails on conflicts so the developer can properly commit or discard work.
###
### It is important to keep the `git-ensure-clean-diff` dependency, else
### WORK WILL BE LOST!!
###############################################################################
define git-update-checkout-template
update-checkout-$(2): git-ensure-clean-diff-$(2)
	cd $(2) \
	  && git fetch --tags \
	  && git checkout $(3) \
	  && git pull origin $(3) --ff-only
endef
$(foreach rr,$(SUBPROJECT_REPOS),$(eval $(call git-update-checkout-template,$(shell echo $(rr) | cut -d , -f 1),$(shell echo $(rr) | cut -d , -f 2),$(shell echo $(rr) | cut -d , -f 3))))

.PHONY: update-checkouts
update-checkouts: $(foreach p,$(SUBPROJECTS),update-checkout-$(p))

###############################################################################
### Pre Build Hook
### Invokes the pre-build hook in the child project directory if it exists.
### Invoked before the Docker Compose build.
###############################################################################
define prebuild-template
prebuild-$(1): $(1)
	@if [ -e "$(1)/$(HOOK_DIR)/pre-build" ]; then \
	  echo "Running pre-build hook script for $(1)." \
	  && "$(1)/$(HOOK_DIR)/pre-build"; \
	else \
	  echo "No pre-build hook script for $(1). Skipping."; \
	fi;
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call prebuild-template,$(p))))

.PHONY: prebuild
prebuild: $(foreach p,$(SUBPROJECTS),prebuild-$(p))


###############################################################################
### Docker Build
### Performs `docker-compose build --no-cache --pull`
### This is a very conservative build strategy to avoid cache related build
### issues.
###############################################################################
define build-template
build-$(1): prebuild-$(1)
	@cd $(1) \
	  && docker-compose build --no-cache --pull
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call build-template,$(p))))

.PHONY: build
build: $(foreach p,$(SUBPROJECTS),build-$(p))


###############################################################################
### Post Build Hook
### Invokes the post-build hook in the child project if existent.
### Invoke after all services in a project have been built.
###############################################################################
define post-build-template
post-build-$(1): build-$(1)
	@if [ -e "$(1)/$(HOOK_DIR)/post-build" ]; then \
	  echo "Running post-build hook script for $(1)." \
	  && "$(1)/$(HOOK_DIR)/post-build"; \
	else \
	  echo "No post-build hook script for $(1). Skipping."; \
	fi;
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call post-build-template,$(p))))

.PHONY: post-build
post-build: $(foreach p,$(SUBPROJECTS),post-build-$(p))

###############################################################################
### dev-unlink
### Removes the symlinks for docker-compose development
###############################################################################
define dev-unlink-template
dev-unlink-$(1):
	@cd $(1) \
	&& rm -f docker-compose.override.yml \
	&& echo "Removed docker development symlink for $(1)"
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call dev-unlink-template,$(p))))

.PHONY: dev-unlink
dev-unlink: $(foreach p,$(SUBPROJECTS),dev-unlink-$(p))

###############################################################################
### dev-link
### Overrides default symlinks for `docker-compose` using `docker-compose.dev.yml`
###############################################################################
define dev-link-template
dev-link-$(1):
	@if [ -e "$(1)/docker-compose.dev.yml" ]; then \
		cd $(1) \
		&& ln -sf docker-compose.dev.yml docker-compose.override.yml \
		&& echo "Created docker development symlink for $(1)"; \
	fi;
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call dev-link-template,$(p))))

.PHONY: dev-link
dev-link: $(foreach p,$(SUBPROJECTS),dev-link-$(p))

###############################################################################
### dev
### Starts services in development mode with
### `ln -s docker-compose.dev.yml docker-compose.override.yml; docker-compose up -d`
###############################################################################
define dev-template
dev-$(1): stop-$(1) dev-link-$(1) start-$(1)
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call dev-template,$(p))))

###############################################################################
### Start
### Starts services with `docker-compose up -d`
###
### Pull the specified image tags every time. Tags are constantly being updated
### to point to different image IDs, and there is less to debug if we can be
### reasonably to make sure that you're always starting the latest image with that tag.
###
### We are purposely running dc up even if dc pull fails. Our Meteor project DC
### config uses `image` as a desired image tag for `build` when in dev mode. But
### `dc pull` seems to have a bug where it doesn't treat it this way and tries
### to pull it.
###############################################################################
define start-template
start-$(1):
	@cd $(1) && docker-compose pull; docker-compose up -d
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call start-template,$(p))))

.PHONY: start
start: $(foreach p,$(SUBPROJECTS),start-$(p))


###############################################################################
### Post Project Start Hook
### Invokes the post-project-start hook in the child project if existent.
### Invoked after all services in a project have been started.
###############################################################################
define post-project-start-template
post-project-start-$(1):
	@if [ -e "$(1)/$(HOOK_DIR)/post-project-start" ]; then \
	  echo "Running post-project-start hook script for $(1)." \
	  && "$(1)/$(HOOK_DIR)/post-project-start"; \
	else \
	  echo "No post-project-start hook script for $(1). Skipping."; \
	fi;
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call post-project-start-template,$(p))))

###############################################################################
### Post System Start Hook
### Invokes the post-system-start hook in the child projects if existent.
### Invoked after all services in the system have been started.
###
### Note: The final echo is required otherwise output of post-system-hook is
###       not output.
###############################################################################
define post-system-start-template
post-system-start-$(1):
	@if [ -e "$(1)/$(HOOK_DIR)/post-system-start" ]; then \
	  echo "Running post-system-start hook script for $(1)." \
	  && "$(1)/$(HOOK_DIR)/post-system-start" \
	  && echo ""; \
	else \
	  echo "No post-system-start hook script for $(1). Skipping."; \
	fi;
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call post-system-start-template,$(p))))

.PHONY: post-system-start
post-system-start: $(foreach p,$(SUBPROJECTS),post-system-start-$(p))


###############################################################################
### Stop
### Stops services with `docker-compose stop`
###############################################################################
define stop-template
stop-$(1):
	@cd $(1) \
	  && docker-compose stop
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call stop-template,$(p))))

.PHONY: stop
stop: $(foreach p,$(SUBPROJECTS),stop-$(p))

###############################################################################
### rm
### Remove containers with `docker-compose rm`
### Does not remove volumes.
###############################################################################
define rm-template
rm-$(1):
	@cd $(1) \
	  && docker-compose rm --stop --force
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call rm-template,$(p))))

.PHONY: rm
rm: $(foreach p,$(SUBPROJECTS),rm-$(p))

###############################################################################
### Clean
### Clean services with `docker-compose rm`
### Removes all containers, volumes and local networks.
###############################################################################
define clean-template
clean-$(1):
	@cd $(1) \
	  && docker-compose down -v --rmi local --remove-orphans
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call clean-template,$(p))))

.PHONY: clean
clean: $(foreach p,$(SUBPROJECTS),clean-$(p)) network-remove

###############################################################################
### Destroy
### Deletes project directories after removing running containers.
### WARNING: This is extremely destructive. It will remove local project
###          directories. Any work that is not pushed to a remote git
###          repository will be lost!
###
###############################################################################
define destroy-template
destroy-$(1): clean
	@rm -Rf $(1)
endef
$(foreach p,$(SUBPROJECTS),$(eval $(call destroy-template,$(p))))

.PHONY: destroy
destroy: network-remove $(foreach p,$(SUBPROJECTS),destroy-$(p))

###############################################################################
### Dynamically list all targets.
### See: https://stackoverflow.com/a/26339924
###############################################################################
.PHONY: list
list:
	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs -n 1
