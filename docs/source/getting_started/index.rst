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

   :download:`virtual-warehouse_linux.zip <https://drive.google.com/file/d/1dOpJeUEHHL79EZ7MNEoo-NDB2y56YMjw/view?usp=sharing>`

.. tab:: Windows

   :download:`virtual-warehouse_win.zip <https://drive.google.com/file/d/1zo_-yG9v8CYGb2lkn22rYTLze-gDO3Z_/view?usp=sharing>`


2. Extract the archive (and enter directory):

.. tab:: Unix (Linux / macOS)

   .. code-block:: bash

      unzip virtual-warehouse_linux.zip


.. tab:: Windows

   .. code-block:: console

      Use some archive manager


3. Run the executable:


.. tab:: Unix (Linux / macOS)

   .. code-block:: bash

      ./'Virtual Warehouse'


.. tab:: Windows

   .. code-block:: bash

      # Double-click "Virtual Warehouse.exe" or run in command line:
      start "Virtual Warehouse.exe"


Installation (from source)
==========================

Application requires **Python 3** and following requirements: 

.. literalinclude:: ../../../requirements.txt



It is recommended to use `Makefile <https://github.com/Breta01/virtual-warehouse/blob/master/Makefile>`_ if possible. It installs all requirements (creating a separate virtual environment). Build the project using the following command:

.. warning::

   make.bat is not available right now

.. tab:: Unix (Linux / macOS)

   .. code-block:: bash

      make install

.. tab:: Windows

   .. code-block:: bash

      # Install Python 3 (follow instructions at https://www.python.org)
      make.bat install
      start "Virtual Warehouse.exe"


Run the application by running the `main.py <https://github.com/Breta01/virtual-warehouse/blob/master/main.py>`_ file in the root directory. You can also use Makefile:

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
