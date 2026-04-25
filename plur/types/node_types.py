import sys
from typing import Union, Literal
from pydantic import BaseModel, Field, RootModel, ValidationError, computed_field
from plur.types import lib

class WorkerTarget(BaseModel):
    hostname: str = Field(..., title='hostname is needed.')
    username: str = Field(..., title='username is needed.')
    password: str = Field(..., title='password is needed.')
    login_method: str = 'ssh'
    platform: str = 'almalinux8'
    access_ip: lib.ValidIpv4


def create_worker_target(may_worker_target, may_worker_account):
    try:
        for attr in [
            'username'
            , 'password'
        ]:
            if attr not in may_worker_target:
                if attr in may_worker_account:
                    may_worker_target[attr] = may_worker_account[attr]

        worker_target = WorkerTarget(**may_worker_target)
        return worker_target.model_dump()
    except ValidationError as e:
        print('err in create_xos_target by ValidationError')
        print('target dict:', may_worker_target)
        print('account dict:', may_worker_account)
        print(e)
        sys.exit(1)
    except Exception as e:
        print('err in create_xos_target by Exception')
        print('target dict:', may_worker_target)
        print('account dict:', may_worker_account)
        print(e)
        sys.exit(1)

class BashConfig(BaseModel):
    connection_type: Literal["bash"] = "bash"  # 判定用のラベル
    hostname: str = Field(..., title='hostname is needed.')
    username: str = Field(..., title='username is needed.')
    password: str = Field(default="", title='password is needed.')
    platform: str = Field(..., title='platform is needed.')

    @computed_field
    @property
    def waitprompt(self) -> str:
        return lib.get_linux_waitprompt(self.platform, self.hostname, self.username)

class SSHConfig(BaseModel):
    connection_type: Literal["ssh"] = "ssh"   # 判定用のラベル
    hostname: str = Field(..., title='hostname is needed.')
    username: str = Field(..., title='username is needed.')
    password: str = Field(default="", title='password is needed.')
    access_ip: lib.ValidIpv4
    platform: str = Field(..., title='platform is needed.')

    @computed_field
    @property
    def waitprompt(self) -> str:
        return lib.get_linux_waitprompt(self.platform, self.hostname, self.username)

Config = Union[BashConfig, SSHConfig]

# --- 判定と分岐の処理 ---

# def run_process(config: Config):
#     # connection_type の値によって Pydantic が自動でインスタンス化し分ける
#     if isinstance(config, BashConfig):
#         print(f"Bash実行: user={config.username}")
#     elif isinstance(config, SSHConfig):
#         print(f"SSH実行: host={config.hostname}, ip={config.access_ip}")
#
# # --- 実行例 ---
#
# # 例1: Bashとしての入力
# data_bash = {"connection_type": "bash", "username": "admin", "password": "pw1"}
# config1 = RootModel[Config](data_bash).root
# run_process(config1)
#
# # 例2: SSHとしての入力
# data_ssh = {
#     "connection_type": "ssh", 
#     "username": "root", 
#     "hostname": "my-server", 
#     "access_ip": "192.168.1.1", 
#     "password": "pw2"
# }
# config2 = RootModel[Config](data_ssh).root
# run_process(config2)

