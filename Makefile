.PHONY: help install lint clean docs

SHELL=/bin/bash

VENV_NAME?=venv
VENV_BIN=$(shell pwd)/${VENV_NAME}/bin
VENV_ACTIVATE=source $(VENV_NAME)/bin/activate

PROJECT_DIR=virtual_warehouse

PYTHON=${VENV_NAME}/bin/python3


.DEFAULT: help
help:
	@echo "Make file commands:"
	@echo "    make install"
	@echo "        Prepare complete development environment"
	@echo "    make lint"
	@echo "        Run pylint and mypy"
	@echo "    make resources"
	@echo "        Make qrc resources file - main_rc.py"
	@echo "    make package"
	@echo "        Create packaged application"
	@echo "    make run"
	@echo "        Run application"
	@echo "    make docs"
	@echo "        Generate HTML documentation"
	@echo "    make clean"
	@echo "        Clean repository"

install:
	sudo apt-get -y install build-essential python3.8 python3.8-dev
	python3.8 -m pip install pip
	python3.8 -m pip install virtualenv
	make venv
	${VENV_ACTIVATE}; pre-commit install

# Runs when the file changes
venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: requirements.txt requirements-dev.txt
	test -d $(VENV_NAME) || virtualenv -p python3.8 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	${PYTHON} -m pip install -r requirements-dev.txt
	touch $(VENV_NAME)/bin/activate

resources:
	${VENV_ACTIVATE}; pyside2-rcc virtual_warehouse/main.qrc -o virtual_warehouse/main_rc.py

lint: venv
	${PYTHON} -m pylint virtual_warehouse
	${PYTHON} -m flake8 virtual_warehouse

package: resources
	${VENV_ACTIVATE}; pyinstaller --name="Virtual Warehouse" --windowed --clean \
		--onedir main.py --icon="virtual_warehouse/resources/images/icon.png" \
        --add-data ${VENV_NAME}/lib/python3.8/site-packages/owlready2/pellet:owlready2/pellet
# ${VENV_ACTIVATE}; nuitka3 main.py --show-progress --standalone --plugin-enable=pyside2 --include-qt-plugins=all --windows-disable-console

run: resources
	${PYTHON} main.py

docs:
	${VENV_ACTIVATE}; cd docs; make html

clean:
	find . -name '*.pyc' -exec rm --force {} +
	rm -rf $(VENV_NAME) *.eggs *.egg-info dist build docs/_build .cache
