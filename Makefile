.PHONY: help install lint clean docs

SHELL=/bin/bash

# You can specify exact version of python3 or venv name as environment variable
PYTHON_VERSION?=python3.8
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
	sudo apt-get -y install build-essential $(PYTHON_VERSION) $(PYTHON_VERSION)-dev
	python3 -m pip install pip
	python3 -m pip install virtualenv
	make venv
	${VENV_ACTIVATE}; pre-commit install

# Runs when the file changes
venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: requirements.txt requirements-dev.txt
	test -d $(VENV_NAME) || virtualenv -p $(PYTHON_VERSION) $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt -r requirements-dev.txt
	touch $(VENV_NAME)/bin/activate

resources:
	${VENV_ACTIVATE}; pyside2-rcc virtual_warehouse/main.qrc -o virtual_warehouse/main_rc.py

lint: venv
	${PYTHON} -m pylint virtual_warehouse
	${PYTHON} -m flake8 virtual_warehouse

package: resources
	${VENV_ACTIVATE}; pyinstaller --name="Virtual Warehouse" --windowed --clean \
		--onedir main.py --icon="virtual_warehouse/resources/images/icon.png" \
		--add-data $(shell $(PYTHON) -c "import owlready2 as _; print(_.__file__[:-11])")/pellet:owlready2/pellet
	cd dist; tar -zcvf virtual-warehouse.tar.gz "Virtual Warehouse"
# ${VENV_ACTIVATE}; nuitka3 main.py --show-progress --standalone --plugin-enable=pyside2 --include-qt-plugins=all --windows-disable-console

run: resources
	${PYTHON} main.py

docs:
	${VENV_ACTIVATE}; cd docs; make html

clean:
	find . -name '*.pyc' -exec rm --force {} +
	rm -rf $(VENV_NAME) *.eggs *.egg-info dist build docs/_build .cache
