@echo off

SET PYTHON_VERSION=python3
SET VENV_NAME=venv

SET VENV_ACTIVATE=%VENV_NAME%\Scripts\activate.bat
SET PYTHON=python3

IF /I "%1"==".DEFAULT" GOTO .DEFAULT
IF /I "%1"=="help" GOTO help
IF /I "%1"=="venv" GOTO venv
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
	ECHO "Make file commands:"
	ECHO "    make venv"
	ECHO "        Prepare complete development environment"
	ECHO "    make lint"
	ECHO "        Run pylint and mypy"
	ECHO "    make resources"
	ECHO "        Make qrc resources file - main_rc.py"
	ECHO "    make package"
	ECHO "        Create packaged application"
	ECHO "    make run"
	ECHO "        Run application"
	ECHO "    make docs"
	ECHO "        Generate HTML documentation"
	ECHO "    make clean"
	ECHO "        Clean repository"
	GOTO :EOF

:venv
	virtualenv -p %PYTHON_VERSION% %VENV_NAME%
	%VENV_ACTIVATE%
	%PYTHON% -m pip install -U pip
	%PYTHON% -m pip install -r requirements.txt -r requirements-dev.txt
	GOTO :EOF

:resources
	%VENV_ACTIVATE%
  pyside2-rcc virtual_warehouse/main.qrc -o virtual_warehouse/main_rc.py
	GOTO :EOF

:lint
	CALL make.bat venv
	%VENV_ACTIVATE%
	%PYTHON% -m pylint virtual_warehouse
	%PYTHON% -m flake8 virtual_warehouse
	GOTO :EOF

:package
	CALL make.bat resources

	%VENV_ACTIVATE%

  for /f "tokens=* delims=" %%a in (
    '"python3 -c ""import owlready2 as _; print(_.__file__[:-11])"""'
  ) do (
    pyinstaller --name="Virtual Warehouse" --windowed --clean --onedir main.py --icon="virtual_warehouse/resources/images/icon.ico" --add-data "%%a"/pellet:owlready2/pellet
  )

	PUSHD dist; tar.exe -caf virtual-warehouse.zip "Virtual Warehouse" && POPD
	GOTO :EOF

:run
	CALL make.bat resources
	%PYTHON% main.py
	GOTO :EOF

:docs
	%VENV_ACTIVATE%; PUSHD docs; make.bat html && POPD
	GOTO :EOF

:clean
	DEL /Q %VENV_NAME% *.eggs *.egg-info dist build docs/_build .cache -rf
	GOTO :EOF

:error
    IF "%1"=="" (
        ECHO make: *** No targets specified and no makefile found.  Stop.
    ) ELSE (
        ECHO make: *** No rule to make target '%1%'. Stop.
    )
    GOTO :EOF
