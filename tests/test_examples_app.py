# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test example app."""

import os
import signal
import subprocess
import time

import pytest


@pytest.yield_fixture
def example_app():
    """Example app fixture."""
    current_dir = os.getcwd()

    # Go to example directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exampleappdir = os.path.join(project_dir, 'examples')
    os.chdir(exampleappdir)

    # Setup example
    cmd = './app-setup.sh'
    exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

    # Setup example
    cmd = './app-fixtures.sh'
    exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

    # Starting example web app
    cmd = 'FLASK_APP=app.py FLASK_DEBUG=1 flask run'
    webapp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              preexec_fn=os.setsid, shell=True)
    time.sleep(20)
    # Return webapp
    yield webapp

    # Stop server
    os.killpg(webapp.pid, signal.SIGTERM)

    # Tear down example app
    cmd = './app-teardown.sh'
    subprocess.call(cmd, shell=True)

    # Return to the original directory
    os.chdir(current_dir)


def test_example_app_role_admin(example_app):
    """Test example app."""
    cmd = 'curl http://0.0.0.0:5000/'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    assert '<!DOCTYPE html>' in output
    cmd = 'curl http://0.0.0.0:5000/role_admin'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    assert 'Not Permitted' in output
    cmd = 'curl http://0.0.0.0:5000/action_open'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    assert 'Not Permitted' in output
    cmd = 'curl http://0.0.0.0:5000/action_read'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    assert 'Not Permitted' in output
