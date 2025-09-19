APP=quizcon
JS_FILES=media/js/src

all: jenkins cypress-headless

include *.mk

SYS_PYTHON=python3

integrationserver: $(PY_SENTINAL)
	$(MANAGE) integrationserver --noinput

cypress: $(JS_SENTINAL)
	npm run cypress:test

cypress-headless: $(JS_SENTINAL)
	npm run cypress:test-headless

.PHONY: integrationserver cypress cypress-headless
