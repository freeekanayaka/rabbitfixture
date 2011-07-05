# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for the Rabbit fixture."""

__metaclass__ = type

import socket
from socket import gethostname

from amqplib import client_0_8 as amqp
from fixtures import EnvironmentVariableFixture
from rabbitfixture.server import (
    RabbitServer,
    RabbitServerResources,
    )
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


class TestRabbitServerResources(TestCase):

    def test_defaults(self):
        with RabbitServerResources() as resources:
            self.assertEqual("localhost", resources.hostname)
            self.assertIsInstance(resources.port, int)
            self.assertIsInstance(resources.homedir, (str, unicode))
            self.assertIsInstance(resources.mnesiadir, (str, unicode))
            self.assertIsInstance(resources.logfile, (str, unicode))
            self.assertIsInstance(resources.nodename, (str, unicode))

    def test_passed_to_init(self):
        args = dict(
            hostname="hostname", port=1234,
            homedir="homedir", mnesiadir="mnesiadir",
            logfile="logfile", nodename="nodename")
        with RabbitServerResources(**args) as resources:
            for key, value in args.iteritems():
                self.assertEqual(value, getattr(resources, key))

    def test_fq_nodename(self):
        with RabbitServerResources(nodename="nibbles") as resources:
            self.assertEqual(
                "nibbles@%s" % gethostname(),
                resources.fq_nodename)
