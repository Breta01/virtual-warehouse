@echo off

SET 
SHELL=\bin\bash
SET 
VENV_NAME?=venv
SET VENV_BIN=$(shell pwd)\${VENV_NAME}\bin
SET VENV_ACTIVATE=source $(VENV_NAME)\bin\activate
SET 
PROJECT_DIR=virtual_warehouse
SET 
PYTHON=${VENV_NAME}\bin\python3

IF /I "%1"==".DEFAULT" GOTO .DEFAULT
IF /I "%1"=="help" GOTO help
IF /I "%1"=="install" GOTO install
IF /I "%1"=="venv" GOTO venv
IF /I "%1"=="$(VENV_NAME)/bin/activate" GOTO $(VENV_NAME)/bin/activate
IF /I "%1"=="resources" GOTO resources
IF /I "%1"=="lint" GOTO lint
IF /I "%1"=="package" GOTO package
IF /I "%1"=="run" GOTO run
IF /I "%1"=="docs" GOTO docs
IF /I "%1"=="clean" GOTO clean
GOTO error

:.DEFAULT
	CALL make.bat help
	GOTO :EOF

:help
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
	GOTO :EOF

:install
	sudo apt-get -y install build-essential python3.8 python3.8-dev
	python3.8 -m pip install pip
	python3.8 -m pip install virtualenv
	make venv
	%VENV_ACTIVATE%; pre-commit install
	GOTO :EOF

:venv
	CALL make.bat $(VENV_NAME)/bin/activate
	GOTO :EOF

:$(VENV_NAME)/bin/activate
	CALL make.bat requirements.txt
	CALL make.bat requirements-dev.txt
	test -d %VENV_NAME% || virtualenv -p python3.8 %VENV_NAME%
	%PYTHON% -m pip install -U pip
	%PYTHON% -m pip install -r requirements.txt
	%PYTHON% -m pip install -r requirements-dev.txt
	touch %VENV_NAME%/bin/activate
	GOTO :EOF

:resources
	%VENV_ACTIVATE%; pyside2-rcc virtual_warehouse/main.qrc -o virtual_warehouse/main_rc.py
	GOTO :EOF

:lint
	CALL make.bat venv
	%PYTHON% -m pylint virtual_warehouse
	%PYTHON% -m flake8 virtual_warehouse
	GOTO :EOF

:package
	CALL make.bat resources
	%VENV_ACTIVATE%; pyinstaller --name="Virtual Warehouse" --windowed --clean --onedir main.py --icon="virtual_warehouse/resources/images/icon.ico" --add-data %VENV_NAME%/lib/python3.8/site-packages/owlready2/pellet:owlready2/pellet
	GOTO :EOF

:run
	CALL make.bat resources
	%PYTHON% main.py
	GOTO :EOF

:docs
	%VENV_ACTIVATE%; cd docs; make html
	GOTO :EOF

:clean
	find . -name '*.pyc' -exec rm --force {} +
	DEL /Q %VENV_NAME% *.eggs *.egg-info dist build docs/_build .cache -rf
	GOTO :EOF

:error
    IF "%1"=="" (
        ECHO make: *** No targets specified and no makefile found.  Stop.
    ) ELSE (
        ECHO make: *** No rule to make target '%1%'. Stop.
    )
    GOTO :EOF
