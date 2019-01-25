# -*- coding: utf-8 -*-

import sys
import warnings
from dataclasses import dataclass
import paramiko
from scp import SCPClient
from sshtunnel import SSHTunnelForwarder

from .interactive import interactive_shell
from .model import Ops, SSHOps


@dataclass
class MaybeForwarder:
    o: Ops
    fw: SSHTunnelForwarder = None
    pre = None

    @classmethod
    def unit(cls, ops: Ops):
        m = MaybeForwarder(ops)
        print("{} {}".format(ops.host, ops.port), end=' ')
        return m

    def bind(self, fn):
        [o, fw] = self.get_value()
        mn = fn(o, fw)

        if mn is Nothing:
            self.fail()
        else:
            mn.pre = self
        return mn

    def get_value(self):
        return self.o, self.fw

    def fail(self):
        if self.fw:
            self.fw.close()

        if self.pre:
            self.pre.fail()
        pass

    #
    def forward(self, fwops: Ops):
        """
        跳转
        :param fwops:
        :return:
        """

        def forward_m(o, fw) -> MaybeForwarder:
            if not (type(o) is SSHOps):
                print("o must be SSHOps", o)
                return Nothing

            bind_addr = ('127.0.0.1', fw.local_bind_port) if fw else (o.host, o.port)
            fww = SSHTunnelForwarder(bind_addr, ssh_username=o.username,
                                     ssh_password=o.password,
                                     local_bind_address=('127.0.0.1', 0),
                                     remote_bind_address=(fwops.host, fwops.port))
            print(' >> {} {}'.format(fwops.host, fwops.port), end="")
            try:
                fww.start()
            except Exception as e:
                warn('{} 认证错误。'.format(o.host))
                return Nothing
            return MaybeForwarder(fwops, fww)

        return self.bind(forward_m)

    def listen(self):
        """
        监听
        :return:
        """

        def listen_m(o, fw) -> Nothing:
            print(' >> listen')
            print('bind {} {} on {}'.format(o.host, o.port, fw.local_bind_address))
            try:
                input('press Enter to stop\n')
            except KeyboardInterrupt:
                pass
            return Nothing

        return self.bind(listen_m)

    def ssh(self):
        """
        开发ssh交互窗口
        :return:
        """

        def ssh_m(o, fw) -> Nothing:
            print(' >> ssh')
            if not (type(o) is SSHOps):
                print("o must be SSHOps", o)
                return Nothing

            sh = paramiko.SSHClient()
            sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                sh.connect('127.0.0.1', port=fw.local_bind_port, username=o.username, password=o.password)
                chan = sh.invoke_shell()
                interactive_shell(chan)
                chan.close()
            except Exception as e:
                print(e)
            finally:
                if sh:
                    sh.close()

            return Nothing

        return self.bind(ssh_m)

    def scp(self, f, t):
        """
        与远程机器拷贝文件
        :param f: from_path 远程机器以 ":"开头
        :param t: to_path 远程机器以 ":"开头 。 f, t必须有且只有一个为远程机器路径
        :return:
        """

        def scp_m(o, fw) -> Nothing:
            print(' >> scp')
            if not (type(o) is SSHOps):
                print("o must be SSHOps", o)
                return Nothing

            if not valid_scp_params(f, t):
                return Nothing

            sh = paramiko.SSHClient()
            sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                sh.connect('127.0.0.1', port=fw.local_bind_port, username=o.username, password=o.password)
                with get_scp_client(sh) as cp:
                    if f.startswith(':'):
                        cp.get(f[1:], t)
                    elif t.startswith(':'):
                        cp.put(f, t[1:])

            except Exception as e:
                print(e)
            finally:
                if sh:
                    sh.close()

            return Nothing

        return self.bind(scp_m)

    def exec(self, cmd):
        def exec_m(o, fw):
            print(' >> exec `{}`'.format(cmd))
            if not (type(o) is SSHOps):
                print("o must be SSHOps", o)
                return Nothing

            sh = paramiko.SSHClient()
            sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                sh.connect('127.0.0.1', port=fw.local_bind_port, username=o.username, password=o.password)
                stdin, stdout, stderr = sh.exec_command(cmd)
                for l in stdout:
                    sys.stdout.write(l)
            except Exception as e:
                warn(e)
            finally:
                if sh:
                    sh.close()

            return Nothing

        return self.bind(exec_m)


class _Nothing(MaybeForwarder):

    def __init__(self, ops=None):
        super().__init__(ops)

    def bind(self, fn):
        return self

    def get_value(self):
        return None


Nothing = _Nothing()


def valid_scp_params(f, t):
    remote_path_count = len([1 for n in [f, t] if n.startswith(':')])
    if remote_path_count != 1:
        warn('参数错误，scp必须有一个参数为远程地址（以":"开头）\n')

    return True


def get_scp_client(sh):
    def progress(filename, size, sent):
        sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent) / float(size) * 100))

    cp = SCPClient(sh.get_transport(), progress=progress)
    return cp


def warn(msg):
    warnings.warn(msg, RuntimeWarning, stacklevel=2)
