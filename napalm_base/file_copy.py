#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# Python3 support
from __future__ import print_function
from __future__ import unicode_literals


class BaseFileCopy(object):

    def __init__(self, napalm_conn, source_file, dest_file, direction='put', file_system=None):
        """
        This is the base class you will inherit from when writing your own FileCopy class. The
        FileCopy class must support put_file() and get_file() methods. Additionally, a context
        manager must be supported. File transfer failures should result in a FileTransferException.
    
        :param napalm_conn: (NAPALM object) NAPALM-driver connection used as a control-channel.
        :param source_file: (str) Source file for transfer.
        :param dest_file: (str) Destination file for transfer.
        :param direction: (str) 'put' or 'get'; defaults to 'put'.
        :param file_system: (str) Name of remote file-system, if needed.
        """
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self):
        raise NotImplementedError

    def _connect(self):
        raise NotImplementedError

    def _disconnect(self):
        raise NotImplementedError

    def get_file(self):
        """
        Transfer file from remote network device to control system

        Idempotent - verify whether file already exists and has correct MD5 hash.
        Verify sufficient space exists on local device.

        :raise FileTransferException: If file transfer fails.
        """
        raise NotImplementedError

    def put_file(self):
        """
        Transfer file from control system to remote network device.

        Idempotent - verify whether file already exists and has correct MD5 hash.
        Verify sufficient space exists on remote device.

        :raise FileTransferException: If file transfer fails.
        """
        raise NotImplementedError

    def _remote_md5(self):
        raise NotImplementedError

    def _local_md5(self):
        raise NotImplementedError

    def _compare_md5(self):
        raise NotImplementedError

    def _remote_space_available(self):
        raise NotImplementedError

    def _local_space_available(self):
        raise NotImplementedError

    def _verify_space_available(self):
        raise NotImplementedError

    def _check_file_exists(self):
        raise NotImplementedError

    def _remote_file_size(self):
        raise NotImplementedError

    def _local_file_size(self):
        raise NotImplementedError
