=======================
 Invenio-Access v0.2.0
=======================

Invenio-Access v0.2.0 was released on October 2, 2015.

About
-----

Invenio module for common role based access control.

*This is an experimental developer preview release.*

Incompatible changes
--------------------

- Changes function name of `AclFactory` function to `act_factory`.
- Removes legacy admin interface. (#3233)
- Removes legacy WebUser module.

Improved features
-----------------

- Makes upgrade recipe resilient to missing primary key in
  accROLE_accACTION_accARGUMENT table.  (#10)

Bug fixes
---------

- Removes dependencies to invenio.utils and replaces them with
  invenio_utils.
- Removes dependencies to invenio.testsuite and replaces them with
  invenio_testing.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.
- Adds missing invenio_ext dependency and fixes its imports.
- Adds missing `invenio_base` dependency.

Installation
------------

   $ pip install invenio-access==0.2.0

Documentation
-------------

   http://invenio-access.readthedocs.org/en/v0.2.0

Happy hacking and thanks for flying Invenio-Access.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-access
|   URL: http://invenio-software.org
