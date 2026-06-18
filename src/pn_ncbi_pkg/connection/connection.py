import ftplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Generic, Self, TypeVar

import paramiko
import yaml

from .errors import (
    ConnectionConfigError,
    MissingConnectionSettingError,
    NCBIConnectionError,
    UnsupportedProtocolError,
)


@dataclass(frozen=True)
class ConnectionConfig:
    host: str
    username: str
    password: str

ConnectionT = TypeVar("ConnectionT")

class Connection(ABC, Generic[ConnectionT]):
    """Base class defining the API of FTP and SFTP connections"""
    def __init__(self, connection: ConnectionT):
        self._connection = connection

    @classmethod
    @abstractmethod
    def connect(cls, host: str, username: str, password: str) -> Self:
        ...

    @abstractmethod
    def change_directory(self, directory: str) -> None:
        ...

    @abstractmethod
    def file_exists(self, file: str) -> bool:
        """Check if file or directory exists in current dir"""
        ...

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> None:
        ...

    @abstractmethod
    def close_connection(self) -> None:
        ...

    @abstractmethod
    def make_directory(self, directory: str) -> None:
        ...

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> None:
        ...

    @abstractmethod
    def read_file(self, remote_path: str) -> str:
        ...


class FTPConnection(Connection[ftplib.FTP]):
    _connection: ftplib.FTP

    @classmethod
    def connect(cls, host: str, username: str, password: str):
        c = cls(ftplib.FTP(host))
        c._connection.login(user=username, passwd=password)
        return c


    def change_directory(self, directory: str) -> None:
        self._connection.cwd(directory)

    def file_exists(self, file: str) -> bool:
        return file in self._connection.nlst()


    def download_file(self, remote_path: str, local_path: str) -> None:
        lp = Path(local_path)
        if not self.file_exists(remote_path):
            raise FileNotFoundError(f"{remote_path} does not exist")

        if not lp.parent.exists():
            Path.mkdir(lp.parent, parents=True)

        with open(lp, "wb") as f:
            self._connection.retrbinary(f'RETR {remote_path}', f.write, 262144)

        if not lp.exists():
            raise ConnectionError("File was found but download failed.")


    def close_connection(self) -> None:
        self._connection.quit()


    def make_directory(self, directory: str) -> None:
        self._connection.mkd(directory)


    def upload_file(self, local_path: str, remote_path: str) -> None:
        try:
            with open(local_path, 'rb') as file:
                self._connection.storbinary(f'STOR {remote_path}', file)
        except Exception as e:
            raise OSError(f"Failed to upload {local_path} to {remote_path}: {e}") from None

    def read_file(self, remote_path: str) -> str:
        if not self.file_exists(remote_path):
            raise FileNotFoundError(f"{remote_path} does not exist")

        fobj = BytesIO()
        self._connection.retrbinary(f'RETR {remote_path}', fobj.write)
        return fobj.getvalue().decode('utf-8')




class SFTPConnection(Connection[paramiko.SFTPClient]):
    _connection: paramiko.SFTPClient

    @classmethod
    def connect(cls, host: str, username: str, password: str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, port=22)
        c = cls(ssh.open_sftp())
        return c


    def change_directory(self, directory: str) -> None:
        self._connection.chdir(directory)

    def file_exists(self, file: str) -> bool:
        try:
            self._connection.stat(file)
        except OSError:
            return False

        except Exception as e:
            raise OSError(f"Issue encountered checking if {file} exists on server: {e}") from None

        else:
            return True


    def download_file(self, remote_path: str, local_path: str) -> None:
        lp = Path(local_path)
        if not self.file_exists(remote_path):
            raise FileNotFoundError(f"{remote_path} does not exist")

        if not lp.parent.exists():
            Path.mkdir(lp.parent, parents=True)

        self._connection.get(remotepath=remote_path, localpath=lp)

        if not lp.exists():
            raise ConnectionError("File was found but download failed.")


    def close_connection(self):
        self._connection.close()


    def make_directory(self, directory: str) -> None:
        self._connection.mkdir(directory)


    def upload_file(self, local_path: str, remote_path: str) -> None:
        try:
            self._connection.put(local_path, remote_path)
        except Exception as e:
            raise OSError(f"Failed to upload {local_path} to {remote_path}: {e}") from None


    def read_file(self, remote_path: str) -> str:
        if not self.file_exists(remote_path):
            raise FileNotFoundError(f"{remote_path} does not exist")

        with self._connection.open(remote_path, 'r') as f:
            return f.read().decode('utf-8')


def connect(protocol: str, host: str, username: str, password: str) -> FTPConnection|SFTPConnection:
    try:
        match protocol.lower():
            case "ftp":
                return FTPConnection.connect(host, username, password)

            case "sftp":
                return SFTPConnection.connect(host, username, password)

            case _:
                raise UnsupportedProtocolError(f"Unrecognised connection protocol: {protocol}. Expected 'ftp' or 'sftp'.")

    except (*ftplib.all_errors, paramiko.AuthenticationException, paramiko.SSHException, OSError, TimeoutError) as error:
        raise NCBIConnectionError(f"Could not connect to NCBI via {protocol}: {error}") from error


def load_connection_config(protocol: str, submission_yaml: str):
    try:
        with open(submission_yaml) as fin:
            config = yaml.safe_load(fin)
    except OSError as error:
        raise ConnectionConfigError(f"Could not read submission YAML: {submission_yaml}") from error
    except yaml.YAMLError as error:
        raise ConnectionConfigError(f"Invalid YAML: {submission_yaml}") from error

    match protocol.lower():
        case "sftp":
            host_key = "NCBI_sftp_host"
        case "ftp":
            host_key = "NCBI_ftp_host"
        case _:
            raise UnsupportedProtocolError(f"Unsupported protocol: {protocol}")

    missing = [key for key in [host_key, "NCBI_username", "NCBI_password"] if not config.get(key)]
    if missing:
        raise MissingConnectionSettingError(f"Missing connection settings: {', '.join(missing)}")

    return ConnectionConfig(
        host=config[host_key],
        username=config["NCBI_username"],
        password=config["NCBI_password"],
    )

def get_connection(protocol: str, submission_yaml: str) -> FTPConnection | SFTPConnection:
    config = load_connection_config(protocol, submission_yaml)
    return connect(
        protocol=protocol,
        host=config.host,
        username=config.username,
        password=config.password,
    )
