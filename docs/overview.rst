..
    This file is part of Invenio.
    Copyright (C) 2017-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

.. _concepts:

Overview
========
The following is a walk-through of the important concepts in the access control
system.

Users & roles
-------------
First we have **subjects** which can be granted access to a protected resource.

- **User**: Represents an authenticated account in the system.
- **Role**: Represents a job function. Roles are created by e.g. system
  administrators and defined by a name. Users can be assigned zero or more
  roles.
- **System role**: Represents special roles that are created and defined by the
  system and automatically assigned to users (i.e. system roles cannot be
  created and defined by system administrators).

Permissions and needs
---------------------
Second, we have two entities to describe access control:

- **Need**: A need represents the smallest level of access control. It is very
  generic and can express statements such as *"has admin role"* and
  *"has read access to record 42"*.
- **Permission**: Represents a set of required *needs*, any of which should
  be fulfilled to access a resouce. E.g. a permission can combine the two
  statements above into **"has admin role or has read access to record 42"**.

The concept of a *need* can be somewhat hard to grasp at first, so let's
dive in to describe how a need is used. Essentially *needs* are used to express
a) what a permission require and b) what a user provides, i.e.:

- A permission **requires** a set of needs.
- A user **provides** a set of needs.

Thus, checking if a user can access a resource protected by a permission
amounts to checking for a non-empty **intersection** between the above sets.

Types of needs
--------------
Needs can have different types. For instance the statement *"has admin role"*
can be expressed as a *role need type* with the argument ``admin``. This means
that a permission can require the admin role need and that a user can provide
the admin role need. Some basic need types include:

Actions
-------
**Action need** are a special *type of need* that represents actions
(surprise!). Action needs can have zero or more **parameters**. For instance
the statement *"has read access to record 42"* can be decomposed into *read
record action need* with the parameter *42*.

Action needs has the advantage that they do not tie a permission to a specific
role/user name and are much easier to compose and re-use.

Protecting resources
--------------------
In order to protect a resource, you will usually create a new permission which
will require one or more action needs. This new permission and the action needs
are usually expressed explicitly in the source code. In particular note that
Invenio usually always protects resources via action needs instead of user and
role needs.

Granting access
---------------
Subjects (users, roles and system roles) are assigned actions. E.g. a user or
a role can be assigned the action "read record". If the action has parameters,
then it can be assigned to the subject for *any* parameters or
for a *specific* parameter (e.g. read *any* record vs read record *42*).

Identity
--------
The last entity to cover is an identity. During request handling any user
(authenticated or unauthenticated) is represented as an **identity**.
The identity is used to express the *set of needs* that the *current user*
provides. It is solely an abstraction layer on top of users and roles such
that we do not have to care if actions are assigned directly to a user or
indirectly to a user via a role.
