# Copyright (c) 2020 - The Procedural Generation for Gazebo authors
# For information on the respective copyright owner see the NOTICE file
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from ._collection_manager import _CollectionManager
from ..simulation.properties import Mesh


class MeshManager(_CollectionManager):
    def __init__(self):
        super(MeshManager, self).__init__()

    @staticmethod
    def get_instance():
        if MeshManager._INSTANCE is None:
            MeshManager._INSTANCE = MeshManager()
        return MeshManager._INSTANCE

    def add(self, tag, filename, scale=[1, 1, 1]):
        self._collection[tag] = Mesh(filename=filename, scale=scale)