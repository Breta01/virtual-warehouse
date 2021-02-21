{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. 
   Autoclass generates the methods at the end of documentation might need some changing
   Adding :toctree: after autosummary will generate separate file/page for each method or attribute:


.. autoclass:: {{ objname }}

   :INIT DESCRIPTION:
   

   {% block methods %}
   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
   {% for item in methods %}
   {%- if item not in inherited_members %}
      ~{{ name }}.{{ item }}
   {%- endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}
   

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
   {% for item in attributes %}
   {%- if item not in inherited_members %}
      ~{{ name }}.{{ item }}
   {%- endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}
   
   .. rubric:: {{ _('Full Description') }}



