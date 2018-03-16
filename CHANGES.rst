Changes
=======

Version 1.0.0b1 (released 2017-08-10)
-------------------------------------

- Major incompatible rewrite.

Version 0.2.0 (released 2015-10-02)
-----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Changes function name of `AclFactory` function to `act_factory`.
- Removes legacy admin interface. (#3233)
- Removes legacy WebUser module.

Improved features
~~~~~~~~~~~~~~~~~

- Makes upgrade recipe resilient to missing primary key in
  accROLE_accACTION_accARGUMENT table.  (#10)

Bug fixes
~~~~~~~~~

- Removes dependencies to invenio.utils and replaces them with
  invenio_utils.
- Removes dependencies to invenio.testsuite and replaces them with
  invenio_testing.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.
- Adds missing invenio_ext dependency and fixes its imports.
- Adds missing `invenio_base` dependency.


Version 0.1.0 (released 2015-09-04)
-----------------------------------

- Initial public release.
