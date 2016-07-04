..
    This file is part of Invenio.
    Copyright (C) 2015, 2016 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Changes
=======

Version 1.0.0a8 (released 2016-07-04)
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
