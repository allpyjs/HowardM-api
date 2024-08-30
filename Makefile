.PHONY: all logs fast up-build docker-build docker-stats compose-build site ps big nginx black test consul_backup shell work work_gevent conf pg_dumpall pip

VERSION=$(shell git tag | sort --version-sort -r | head -1)
GIT_COMMIT=$(shell git rev-parse --short HEAD)
GIT_DIRTY=$(shell test -n "`git status --porcelain`" && echo "+CHANGES" || true)
IMAGE_NAME=docker.pkg.github.com/nicksherron/hm_api/hm_api
DOCKER_COMPOSE_FILES = -f docker-compose.yml
DOCKER_COMPOSE_FILES += -f docker-compose-celery.yml
DOCKER_COMPOSE_FILES += -f docker-compose-flower.yml
DOCKER_COMPOSE_FILES += -f docker-compose-rabbit.yml

fast: build up logs

all: test-headless build logs

build: docker-build docker-push

update-env:
	sed -i.bak 's/GIT_COMMIT=\(.*\)/GIT_COMMIT="$(GIT_COMMIT)"/' hm_api/version.py && rm -f hm_api/version.py.bak
	sed -i.bak 's/__version__=\(.*\)/__version__="$(VERSION)"/' hm_api/version.py && rm -f hm_api/version.py.bak

docker-stats:
	docker stats --all --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"  | grep -v 0B

docker-build:
	DOCKER_HOST='' docker build --build-arg GIT_COMMIT=${GIT_COMMIT} -t $(IMAGE_NAME):latest -t $(IMAGE_NAME):$(GIT_COMMIT) .

docker-push:
	DOCKER_HOST='' docker push $(IMAGE_NAME):latest
	DOCKER_HOST='' docker push $(IMAGE_NAME):$(GIT_COMMIT)
compose-build:
	docker pull $(IMAGE_NAME):latest
	docker-compose ${DOCKER_COMPOSE_FILES} up -d --build

up:
	docker pull $(IMAGE_NAME):latest
	docker-compose ${DOCKER_COMPOSE_FILES} up -d

down:
	docker-compose ${DOCKER_COMPOSE_FILES} down

pause:
	docker-compose ${DOCKER_COMPOSE_FILES} pause

unpause:
	docker-compose ${DOCKER_COMPOSE_FILES} unpause


restart:
	docker-compose ${DOCKER_COMPOSE_FILES} restart

logs:
	docker-compose ${DOCKER_COMPOSE_FILES} logs -f --tail 100

ps:
	docker-compose ${DOCKER_COMPOSE_FILES} ps -a

backup: pg_dumpall consul_backup

pg_dumpall:
	pg_dumpall  --exclude-database=template1  \
		--exclude-database=map_violations \
		--exclude-database=reporting_orders | gzip > data/dump/hm_pgdumpall.sql.gz

consul_backup:
	consulate --api-host $$CONSUL_HOST --token $$CONSUL_HTTP_TOKEN kv backup > data/consul_kv_backup.json

site:
	open "http://jhan.s4011@howardmiller.co:Gv0lVaJ5@services.howardmiller.com/cgi-bin/sy7000e?keysls="

big:
	open "https://console.cloud.google.com/bigquery?project=bigquery-284723&authuser=2"

nginx:
	sudo nginx -t || true
	rsync -avz --progress /etc/nginx /tmp || true
	rsync -avz --progress nginx /etc
	sudo nginx -t
	sudo systemctl reload nginx

black:
	black .

test:
	pytest --driver Firefox -W ignore::DeprecationWarning

test-headless:
	pytest --driver Firefox --headless  -W ignore::DeprecationWarning

work:
	celery -A hm_api.jobs.celery.app worker --loglevel=info -E -B  -Q db,celery,orders

work_gevent:
	celery -A hm_api.jobs.celery.app worker --loglevel=info -E   -Q="requests"   -P eventlet -c 1000

shell:
	celery -A hm_api.jobs.celery.app shell
conf:
	celery -A hm_api.jobs.celery.app inspect conf
stats:
	celery -A hm_api.jobs.celery.app inspect stats
queues:
	celery -A hm_api.jobs.celery.app inspect active_queues

list-queues:
	docker exec -it hm_api_rabbit_1  rabbitmqctl list_queues

purge-requests:
	docker-compose -f docker-compose-celery.yml down
	celery -A  hm_api.jobs.celery.app amqp queue.purge requests
	docker-compose -f docker-compose-celery.yml up -d

pip:
	pip install --upgrade -e '.[dev]'

models: models_postgres models_postgres_5433 models_ebay models_orders

models_postgres:
	flask-sqlacodegen --notables  --outfile hm_api/models/postgres_autogen.py "postgresql://postgres:hmbot@hmg:5432"
	flask-sqlacodegen --noclasses  --outfile hm_api/models/postgres_autogen_tables.py "postgresql://postgres:hmbot@hmg:5432"

models_postgres_5433:
	flask-sqlacodegen --notables  --outfile hm_api/models/postgres_5433_autogen.py "postgresql://postgres:hmbot@hmg:5433"
	flask-sqlacodegen --noclasses  --outfile hm_api/models/postgres_5433_autogen_tables.py "postgresql://postgres:hmbot@hmg:5433"

models_orders:
	flask-sqlacodegen --notables  --outfile hm_api/models/orders_autogen.py "postgresql://postgres:hmbot@hmg:5432/orders"
	flask-sqlacodegen --noclasses --outfile hm_api/models/orders_autogen_tables.py "postgresql://postgres:hmbot@hmg:5432/orders"

models_ebay:
	flask-sqlacodegen --notables  --outfile hm_api/models/ebay_autogen.py "postgresql://postgres:hmbot@hmg:5432/ebay"
	flask-sqlacodegen --noclasses  --outfile hm_api/models/ebay_autogen_tables.py "postgresql://postgres:hmbot@hmg:5432/ebay"

models_target:
	flask-sqlacodegen --notables  --outfile hm_api/models/target_autogen.py "postgresql://postgres:hmbot@hmg:5432/target"
	flask-sqlacodegen --noclasses  --outfile hm_api/models/target_autogen_tables.py "postgresql://postgres:hmbot@hmg:5432/target"


mac2-sync:
	rsync -r --exclude='*/.git' --filter=':- .gitignore' --progress -v -e ssh  $$PWD mac2:/Users/nicksherron/.go/src/github.com/nicksherron

