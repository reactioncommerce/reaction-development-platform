#gnu makefile
# This Makefile provides macro control of the Reaction Platform microservice
# ecosystem. It performs tasks like:
#
#   * Verify dependencies are present
#   * Clone git projects
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

# List of tools that must be installed.
# A simple check to determine the tool is available. No version check, etc.
REQUIRED_SOFTWARE=docker docker-compose git node yarn

# List of projects that will be cloned and integrated into the system.
# The project name must be in the ReactionCommerce Github org and the name must
# match the Github project name.
# Projects are started in order of this list.
REACTION_PROJECTS=reaction-hydra \
		  reaction \
		  reaction-next-starterkit

# List of user defined networks that should be created.
REACTION_NETWORKS=auth.reaction.localhost \
		  api.reaction.localhost

HOOK_DIR=.reaction/project-hooks

all: init

###############################################################################
### Init-Project
### Initializes a project. Does not do common tasks shared between projects.
###############################################################################
define init-template
init-$(1): $(1) network-create prebuild-$(1) build-$(1) post-build-$(1) start-$(1) post-project-start-$(1)
endef
$(foreach p,$(REACTION_PROJECTS),$(eval $(call init-template,$(p))))

###############################################################################
### Init Project with System
### Init project and run the post-system hook script.
### Assumes dependencies are already started.
###############################################################################
define init-with-system-template
init-with-system-$(1): init-$(1) post-system-start-$(1)
endef
$(foreach p,$(REACTION_PROJECTS),$(eval $(call init-with-system-template,$(p))))

.PHONY: init
init: $(foreach p,$(REACTION_PROJECTS),init-$(p)) post-system-start


###############################################################################
### Targets to verify Github is configured correctly.
###############################################################################
ssh-public-key: ~/.ssh/id_rsa.pub
	@echo "SSH public key verified at ~/.ssh/id_rsa.pub"

~/.ssh/id_rsa.pub:
	@ssh-keygen

github-configured: dependencies ssh-public-key
	@(ssh -T git@github.com 2>&1 \
	  | grep "successfully authenticated" >/dev/null \
	  && echo "Github login verified.") \
	|| (echo "You need to add your public key to Github" \
	&& echo "Github settings URL: https://github.com/settings/keys" \
	&& echo "== Start copy at next line ===" \
	&& cat ~/.ssh/id_rsa.pub \
	&& echo "== End copy at above line ===" \
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
### Create all networks defined in the REACTION_NETWORKS variable.
### Networks provide a way to loosely couple the projects and allow them to
### communicate with each other. We'll use dependencies on external networks
### rather than dependencies on other projects. Networks are lightweight and
### easy to create.
###############################################################################
define network-create-template
network-create-$(1):
	@docker network create "$(1)" || true
endef
$(foreach p,$(REACTION_NETWORKS),$(eval $(call network-create-template,$(p))))

.PHONY: network-create
network-create: $(foreach p,$(REACTION_NETWORKS),network-create-$(p))

###############################################################################
### Remove Docker Networks
### Remove all networks defined in the REACTION_NETWORKS variable.
###############################################################################
define network-remove-template
network-remove-$(1):
	@docker network rm "$(1)" || true
endef
$(foreach p,$(REACTION_NETWORKS),$(eval $(call network-remove-template,$(p))))

.PHONY: network-remove
network-remove: $(foreach p,$(REACTION_NETWORKS),network-remove-$(p))

###############################################################################
### Github cloning
###############################################################################
define git-clone-template
$(1):
	@git clone "git@github.com:reactioncommerce/$(1).git"
endef
$(foreach p,$(REACTION_PROJECTS),$(eval $(call git-clone-template,$(p))))

.PHONY: clone
clone: github-configured $(foreach p,$(REACTION_PROJECTS),$(p))


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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call prebuild-template,$(p))))

.PHONY: prebuild
prebuild: $(foreach p,$(REACTION_PROJECTS),prebuild-$(p))


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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call build-template,$(p))))

.PHONY: build
build: $(foreach p,$(REACTION_PROJECTS),build-$(p))


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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call post-build-template,$(p))))

.PHONY: post-build
post-build: $(foreach p,$(REACTION_PROJECTS),post-build-$(p))


###############################################################################
### Start
### Starts services with `docker-compose up -d`
###############################################################################
define start-template
start-$(1):
	@cd $(1) \
	  && docker-compose up -d
endef
$(foreach p,$(REACTION_PROJECTS),$(eval $(call start-template,$(p))))

.PHONY: start
start: $(foreach p,$(REACTION_PROJECTS),start-$(p))


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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call post-project-start-template,$(p))))

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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call post-system-start-template,$(p))))

.PHONY: post-system-start
post-system-start: $(foreach p,$(REACTION_PROJECTS),post-system-start-$(p))


###############################################################################
### Stop
### Stops services with `docker-compose stop`
###############################################################################
define stop-template
stop-$(1):
	@cd $(1) \
	  && docker-compose stop
endef
$(foreach p,$(REACTION_PROJECTS),$(eval $(call stop-template,$(p))))

.PHONY: stop
stop: $(foreach p,$(REACTION_PROJECTS),stop-$(p))

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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call rm-template,$(p))))

.PHONY: rm
rm: $(foreach p,$(REACTION_PROJECTS),rm-$(p))

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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call clean-template,$(p))))

.PHONY: clean
clean: $(foreach p,$(REACTION_PROJECTS),clean-$(p)) network-remove

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
$(foreach p,$(REACTION_PROJECTS),$(eval $(call destroy-template,$(p))))

.PHONY: destroy
destroy: network-remove $(foreach p,$(REACTION_PROJECTS),destroy-$(p))

###############################################################################
### Dynamically list all targets.
### See: https://stackoverflow.com/a/26339924
###############################################################################
.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs -n 1
