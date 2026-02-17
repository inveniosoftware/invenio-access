..
    This file is part of Invenio.
    Copyright (C) 2015-2022 CERN.
    Copyright (C) 2024-2026 Graz University of Technology.
    Copyright (C) 2025 KTH Royal Institute of Technology.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version v5.1.0 (released 2026-02-17)

- feat: change role.name to role.id for identity.provides RoleNeed

Version v5.0.0 (released 2026-01-27)

- chore(black): update formatting to >= 26.0
- chore(setup): bump dependencies

Version v4.2.1 (released 2025-10-17)

- i18n: pulled translations

Version v4.2.0 (released 2025-07-17)

- i18n: pulled translations

Version 4.1.0 (released 2025-07-03)

- fix(tests): m.entry_points returns a list if group
- tmp(fix): for python3.9
- fix: pkg_resources DeprecationWarning
- refactor(cli): introduce readable commands
- fix: setuptools require underscores instead of dashes
- i18n: removed obsolete translations

Version 4.0.0 (released 2024-12-04)

- setup: bump major dependencies

Version 3.0.2 (released 2024-12-04)

- fix: add translation flag for publishing

Version 3.0.1 (released 2024-11-28)

- setup: pin dependencies

Version 3.0.0 (released 2024-11-13)

- i18n:push translations
- i18n:pulled translations
- setup: move invenio-admin to optional
- model: make forward compatible to sqlalchemy >= 2
- permissions: add system permisssion
- test: make redis configurable

Version 2.0.0 (released 2022-06-14)

- upgrade invenio-accounts dependency
- models: change role_id FK of ActionRoles to string

Version 1.4.4 (released 2022-04-01)

- fix compat issue with Werkzeug 2.1

Version 1.4.3 (released 2022-03-30)

- add support for Flask 2.1, Werkzeug 2.1 and Click 8.1
- bump dependency on invenio-base, invenio-accounts and invenio-i18n

Version 1.4.2 (released 2021-02-16)

- adds a new system role "system_process".
- adds a new identity providing the system process role.

Version 1.4.1 (released 2020-05-07)

- set Sphinx ``<3`` because of errors related to application context
- stop using example app

Version 1.4.0 (released 2020-03-12)

- drop Python 2.7 support
- change Flask dependency management to centralised by invenio-base

Version 1.3.2 (released TBD)

- set Sphinx ``<3`` because of errors related to application context
- stop using example app

Version 1.3.1 (released 2020-01-22)

- increase minimal six version

Version 1.3.0 (released 2019-11-15)

- Adds explicit excludes of needs feature to load permission

Version 1.2.0 (released 2019-08-02)

- Removes DynamicPermission

Version 1.1.0 (released 2018-12-14)

Version 1.0.2 (released 2018-10-31)

- Additional test for AnyonymousIdentity loaded on request

Version 1.0.1 (released 2018-05-18)

- Removal of Click warning messages.


Version 1.0.0 (released 2018-03-23)

- Initial public release.
