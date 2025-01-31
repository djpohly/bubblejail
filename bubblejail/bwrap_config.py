# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright 2019-2022 igo95862

# This file is part of bubblejail.
# bubblejail is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# bubblejail is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with bubblejail.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

from dataclasses import dataclass
from os import environ
from collections.abc import Generator
from typing import List, Optional


class BwrapConfigBase:
    arg_word: str

    def to_args(self) -> Generator[str, None, None]:
        yield self.arg_word


class ShareNetwork(BwrapConfigBase):
    arg_word = "--share-net"


class BwrapOptionWithPermissions(BwrapConfigBase):
    def __init__(self, permissions: Optional[int] = None):
        super().__init__()
        self.permissions = permissions

    def to_args(self) -> Generator[str, None, None]:
        if self.permissions is not None:
            yield '--perms'
            yield oct(self.permissions).lstrip('0o')

        yield from super().to_args()


class DirCreate(BwrapOptionWithPermissions):
    arg_word = '--dir'

    def __init__(self, dest: str, permissions: Optional[int] = None):
        super().__init__(permissions)
        self.dest = dest

    def to_args(self) -> Generator[str, None, None]:
        yield from super().to_args()
        yield self.dest


class Symlink(BwrapConfigBase):
    arg_word = '--symlink'

    def __init__(self, source: str, dest: str):
        super().__init__()
        self.source = source
        self.dest = dest

    def to_args(self) -> Generator[str, None, None]:
        yield from super().to_args()
        yield self.source
        yield self.dest


class EnvrimentalVar(BwrapConfigBase):
    arg_word = '--setenv'

    def __init__(self, var_name: str, var_value: Optional[str] = None):
        super().__init__()
        self.var_name = var_name
        self.var_value = var_value

    def to_args(self) -> Generator[str, None, None]:
        yield from super().to_args()

        yield self.var_name
        yield (self.var_value if self.var_value is not None
               else environ[self.var_name])


class ReadOnlyBind(BwrapConfigBase):
    arg_word = '--ro-bind'

    def __init__(self, source: str, dest: Optional[str] = None):
        super().__init__()
        self.source = source
        self.dest = dest

    def to_args(self) -> Generator[str, None, None]:
        yield from super().to_args()

        yield self.source
        yield self.dest if self.dest is not None else self.source


class ReadOnlyBindTry(ReadOnlyBind):
    arg_word = '--ro-bind-try'


class Bind(ReadOnlyBind):
    arg_word = '--bind'


class BindTry(ReadOnlyBind):
    arg_word = '--bind-try'


class DevBind(ReadOnlyBind):
    arg_word = '--dev-bind'


class DevBindTry(ReadOnlyBind):
    arg_word = '--dev-bind-try'


@dataclass
class FileTransfer:
    content: bytes
    dest: str


class DbusCommon:
    arg_word: str = 'ERROR'

    def __init__(self, bus_name: str):
        self.bus_name = bus_name

    def to_args(self) -> str:
        return f"{self.arg_word}={self.bus_name}"


class DbusSessionArgs(DbusCommon):
    ...


class DbusSystemArgs(DbusCommon):
    ...


class DbusSessionTalkTo(DbusSessionArgs):
    arg_word = '--talk'


class DbusSessionOwn(DbusSessionArgs):
    arg_word = '--own'


class SeccompDirective:
    ...


class SeccompSyscallErrno(SeccompDirective):
    def __init__(self, syscall_name: str, errno: int):
        self.syscall_name = syscall_name
        self.errno = errno


class LaunchArguments:
    def __init__(
            self,
            launch_args: List[str],
            priority: int = 0,) -> None:
        self.launch_args = launch_args
        self.priority = priority
