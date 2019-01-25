#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ssh_forwarder import MaybeForwarder, SSHOps, Ops

MaybeForwarder.unit(SSHOps(host="xxx.net", port=22, username="xxx", password="XXXXX")) \
    .forward(SSHOps(host="xxx.net", port=22, username="root", password="XXXXX")) \
    .exec('ls /usr/')