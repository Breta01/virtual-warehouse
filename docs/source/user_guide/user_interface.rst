.. _guide/ui:


==============
User Interface
==============

This is description of individual UI components and theirs usage.

.. figure:: /_static/ui.png

   Application screenshot (heatmap view)


Main Menu
=========

Main menu is located at the top of the application. It provides basic functions:

- Opening data files
- Closing application
- Information about application and link to documentation


Main View
=========

Main view displays visualisation of loaded warehouse. In bottom left corner there is option to switch between 2D (top-down) view and 3D view. For 2D view there is also option of displaying heatmap based on order frequencies.

Heatmap
-------

Calculates order frequencies for individual items. Location frequencies are then estimated based on item frequencies at the location. For visual separation of different frequencies, `viridis color scale <https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html>`_ is being used.

There are two different modes of the heatmap. Selection between these modes is controlled by toggle button and value slider at right side of main view.

- **All levels** - calculating the freqency as sum of all levels at the location.
- **Separate level** - calculating the freqency based on selected level.

Side View
---------

For 2D view, side view can be displayed. Side view shows vertical separation (individual levels) of location under the mouse cursor. If now location is hovered, selected location is displayed in side view. Levels are colored based on heatmap calculated for individual levels.


SideBar
========

Sidebar is located at the right side of the application. It is made out of 3 tabs:

- Locations
- Items
- Order

Each tab displays list of coresponding elements. There is also option of filtering the elements by status of their checkbox or search using search bar. Search bar looks for substring match in elemnt ID.

