.. _intro:

===============
Getting Started
===============

This is a short introduction to running the Virtual Warehouse program. After this tutorial, you should be able to start the application and load sample data.

You can run the application from :ref:`pre-build package <Installation (pre-build)>` (recommended) or :ref:`build it from source <Installation (from source)>` (good for further development).


Installation (pre-build)
========================

1. First download the latest executable for your OS:

.. tab:: Unix (Linux / macOS)

   :download:`virtual-warehouse_linux.tar.gz <https://drive.google.com/file/d/1ABhmw5eDQxY55qfiys1DiB1bvxh-VTRD/view?usp=sharing>`

.. tab:: Windows

   :download:`virtual-warehouse_win.zip <https://drive.google.com/file/d/1zo_-yG9v8CYGb2lkn22rYTLze-gDO3Z_/view?usp=sharing>`


2. Extract the archive (and enter directory):

.. tab:: Unix (Linux / macOS)

   .. code-block:: bash

      tar xvf virtual-warehouse_linux.tar.gz
      cd "Virtual Warehouse"


.. tab:: Windows

   .. code-block:: console

      Use some archive manager then enter the directory


3. Run the executable:


.. tab:: Unix (Linux / macOS)

   .. code-block:: bash

      ./'Virtual Warehouse'


.. tab:: Windows

   .. code-block:: bash

      # Double-click "Virtual Warehouse.exe" or run in command line:
      start "Virtual Warehouse.exe"

.. warning::

   **Windows:** Application isn't signed right now. That means that you might see window "Winows protected your PC" from Windows Defender SmartScreen. Just click on "More info" and then "Run anyway".



Installation (from source)
==========================

Application requires **Python 3** and following requirements: 

.. literalinclude:: ../../../requirements.txt



It is recommended to use `Makefile <https://github.com/Breta01/virtual-warehouse/blob/master/Makefile>`_ if possible. It installs all requirements (creating a separate virtual environment). There is Windows equivalent of Makefile in form of `make.bat <https://github.com/Breta01/virtual-warehouse/blob/master/make.bat>`_. Build the project using the following command:

.. warning::

   make.bat is not available right now

.. tab:: Unix (Linux / macOS)

   .. code-block:: bash

      make install

.. tab:: Windows

   .. code-block:: bash

      # Install Python 3 (follow instructions at https://www.python.org)
      # Following command creates virtual environment venv with all requirements
      make.bat venv


It is recommended to use Makefile (make.bat) for running the application. Before running the application you have to build resources (Makefile/make.bat does that automatically). After that you can also run the application by running the `main.py <https://github.com/Breta01virtual-warehouse/blob/master/main.py>`_ file in the root directory.

Using Makefile/make.bat as follows:

.. tab:: Unix (Linux / macOS)

   .. code-block:: bash

      make run

.. tab:: Windows

   .. code-block:: bash

      make.bat run


Example Usage
=============

For start download sample data :download:`warehouse_no_1_v2.xlsx <https://github.com/Breta01/virtual-warehouse/raw/master/data/warehouse_no_1_v2.xlsx>` (more about data format: :ref:`guide/data_format`)

1. Run the application.
2. In the main menu click on: ``File > Open`` and select the downloaded file.
3. After short loading you should see a 2D map of a warehouse.

Then you can explore the sidebar with a description of locations, items or orders. You can also display heat map statistics. More about user interface and different functions at :ref:`guide/ui`.
