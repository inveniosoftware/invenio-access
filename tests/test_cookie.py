# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for Access Mail Cookies."""

from invenio_testing import InvenioTestCase


class TestAccMailCookie(InvenioTestCase):

    """Test Mail cookie."""

    def test_mail_cookie(self):
        """Test mail cookie creation."""
        from invenio_access.models import AccMAILCOOKIE
        cookie = AccMAILCOOKIE.create(kind='mail_activation',
                                      params='test@fuu.it', onetime=True)
        ret = AccMAILCOOKIE.get(cookie=cookie)
        self.assertEqual(ret.data[0], 'mail_activation')
        self.assertEqual(ret.data[1], 'test@fuu.it')
        self.assertEqual(ret.data[3], True)
        self.assertEqual(ret.data[0], 'mail_activation')

        self.data = [ret]

        self.delete_objects(self.data)

    def test_cookie_record_id_is_long(self):
        """Test if cookie id is a long."""
        from invenio_access.models import AccMAILCOOKIE

        cookie = AccMAILCOOKIE(
            kind='mail_activation',
            onetime=0,
            _data="test",
            status="W"
        )
        self.create_objects([cookie])
        load_cookie = AccMAILCOOKIE.query.get(cookie.id)

        assert isinstance(load_cookie.id, long)

        self.delete_objects([cookie])
