# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for the Rabbit fixture."""

__metaclass__ = type

import socket

from amqplib import client_0_8 as amqp
from fixtures import EnvironmentVariableFixture
from rabbitfixture.server import RabbitServer
from testtools import TestCase


class TestRabbitFixture(TestCase):

    def test_start_check_shutdown(self):
        # Rabbit needs to fully isolate itself: an existing per user
        # .erlange.cookie has to be ignored, and ditto bogus HOME if other
        # tests fail to cleanup.
        self.useFixture(EnvironmentVariableFixture('HOME', '/nonsense/value'))

        fixture = self.useFixture(RabbitServer())

        # We can connect.
        connect_arguments = {
            "host": 'localhost:%s' % fixture.config.port,
            "userid": "guest", "password": "guest",
            "virtual_host": "/", "insist": False,
            }
        amqp.Connection(**connect_arguments).close()
        # And get a log file.
        log = fixture.runner.getDetails()["server.log"]
        # Which shouldn't blow up on iteration.
        list(log.iter_text())

        fixture.cleanUp()

        # The daemon should be closed now.
        self.assertRaises(socket.error, amqp.Connection, **connect_arguments)
