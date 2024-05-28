# MAKEFILE_DIR=$(realpath $(dir $(firstword $(MAKEFILE_LIST))))

# docker:
# 	@ for dir in */ ; do \
# 		if $(MAKE) --no-print-directory -nC $${dir} docker > /dev/null 2>&1 ; then \
# 			$(MAKE) -C $${dir} ; \
# 		fi \
# 	done

DOCKER=DOCKER_BUILDKIT=1 docker
WORKDIR=/usr/src/analog

docker-build:
	$(DOCKER) build --target build -t analog_garage_build:latest .

docker-test:
	$(DOCKER) build --target test -t analog_garage_test:latest .

pip-compile-prod: docker-build
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/requirements,dst=/requirements -w /requirements analog_garage_build pip-compile --strip-extras -q requirements.in

pip-compile-dev: docker-build
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/requirements,dst=/requirements -w /requirements analog_garage_build pip-compile --strip-extras -q requirements-dev.in

requirements: pip-compile-prod pip-compile-dev

dev: docker-test
	$(DOCKER) run -it --mount type=bind,source=$(CURDIR)/src,dst=$(WORKDIR)/src \
		--mount type=bind,source=$(CURDIR)/test,dst=$(WORKDIR)/test \
		analog_garage_test:latest sh

test: docker-test
	$(DOCKER) run --mount type=bind,source=$(CURDIR)/src,dst=$(WORKDIR)/src \
		--mount type=bind,source=$(CURDIR)/test,dst=$(WORKDIR)/test \
		analog_garage_test:latest coverage run -m pytest test

docker-prod:
	$(DOCKER) build --target prod -t analog_garage_prod:latest .

run: docker-prod
	docker compose up

stop:
	docker compose down

