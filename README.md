# ssh多层穿透

### 一、环境要求

- python 3.7+

### 二、安装方法

```bash
pip3 install git+https://github.com/a2dict/ssh-forwarder.git
```

### 三、使用方法法

```python
from ssh_forwarder import MaybeForwarder, SSHOps, Ops

if __name__ == '__main__':
    # 将远程端口bind到本地
    MaybeForwarder.unit(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .forward(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .forward(Ops(host="localhost", port=5432)) \
        .listen()

    # 登录远程主机
    MaybeForwarder.unit(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .forward(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .ssh()

    # 将dump文件scp到远程
    MaybeForwarder.unit(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .forward(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .scp('dump', ':/tmp/')

    # scp到本地
    MaybeForwarder.unit(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .forward(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .scp(':/tmp/dump', './')
        
    # 远程执行命令
    MaybeForwarder.unit(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .forward(SSHOps(host="xxx.com", port=22, username="root", password="XXXXXX")) \
        .exec('ls /usr')

```