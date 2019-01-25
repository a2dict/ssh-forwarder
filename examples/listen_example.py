#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ssh_forwarder import MaybeForwarder, SSHOps, Ops

MaybeForwarder.unit(SSHOps(host="xxx.com", port=22, username="xxx", password="XXXXX")) \
    .forward(SSHOps(host="xxx.com", port=22, username="root", password="XXXXX")) \
    .forward(Ops(host="localhost", port=3306)) \
    .listen()
