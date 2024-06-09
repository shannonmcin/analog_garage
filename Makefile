# MAKEFILE_DIR=$(realpath $(dir $(firstword $(MAKEFILE_LIST))))

# docker:
# 	@ for dir in */ ; do \
# 		if $(MAKE) --no-print-directory -nC $${dir} docker > /dev/null 2>&1 ; then \
# 			$(MAKE) -C $${dir} ; \
# 		fi \
# 	done

DOCKER = DOCKER_BUILDKIT=1 docker
WORKDIR = /usr/src/analog
HOST_IP := $(shell hostname -I | cut -d ' ' -f 1)
define DOCKER_MOUNTS
--mount type=bind,source=$(CURDIR)/src,dst=$(WORKDIR)/src \
--mount type=bind,source=$(CURDIR)/tests,dst=$(WORKDIR)/tests \
--mount type=bind,source=/var/run/docker.sock,dst=/var/run/docker.sock
endef
define DOCKER_ENV
-e "HOST_IP_ADDRESS=$(HOST_IP)"
endef

#################### Targets to build docker images ####################
docker-build:
	$(DOCKER) rmi analog_garage_build:latest || true
	$(DOCKER) build --target build -t analog_garage_build:latest .

docker-test:
	$(DOCKER) rmi analog_garage_test:latest || true
	$(DOCKER) build --target test -t analog_garage_test:latest .

docker-prod:
	$(DOCKER) rmi analog_garage_prod:latest || true
	$(DOCKER) build --target prod -t analog_garage_prod:latest .

#################### Targets to generate requirements.txt files ####################
pip-compile-prod: docker-build
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/requirements,dst=/requirements -w /requirements analog_garage_build pip-compile --strip-extras -q requirements.in

pip-compile-dev: docker-build
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/requirements,dst=/requirements -w /requirements analog_garage_build pip-compile --strip-extras -q requirements-dev.in

requirements: pip-compile-prod pip-compile-dev

#################### Targets for public consumption ####################
develop: docker-test
	$(DOCKER) run -it $(DOCKER_MOUNTS) $(DOCKER_ENV) \
		analog_garage_test:latest sh

generate-compose: config.json
	bin/generate_docker_compose

run: generate-compose docker-prod
	docker compose up

stop:
	docker compose down

clean:
	docker rmi -f $$(docker images --filter=reference="analog_garage_*" -q)

# Test/linting targets
test: docker-test
	$(DOCKER) run $(DOCKER_MOUNTS) $(DOCKER_ENV) \
		analog_garage_test:latest sh -c "coverage run -m pytest tests/ && coverage report"

black: docker-test
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/src,dst=$(WORKDIR)/src \
		analog_garage_test:latest black src

isort: docker-test
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/src,dst=$(WORKDIR)/src \
		analog_garage_test:latest isort src

mypy: docker-test
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/src,dst=$(WORKDIR)/src \
		analog_garage_test:latest mypy src

lint: isort black mypy
