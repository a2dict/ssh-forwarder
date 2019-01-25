# -*- coding: utf-8 -*-

from dataclasses import dataclass

@dataclass
class Ops:
    host: str
    port: int


@dataclass
class SSHOps(Ops):
    host: str = ''
    username: str = ''
    password: str = ''
    pkey: str = ''
    port: int = 22
