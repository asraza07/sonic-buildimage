#
# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import json

from unittest.mock import patch
from unittest.mock import mock_open
from unittest.mock import MagicMock

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.chassis import Chassis
from .utils import platform_sample_bf3, smartctl_output


@patch('sonic_py_common.device_info.get_platform', MagicMock(return_value=""))
@patch('sonic_py_common.device_info.get_path_to_platform_dir', MagicMock(return_value=""))
@patch('builtins.open', new_callable=mock_open, read_data=platform_sample_bf3)
@patch('os.path.isfile', MagicMock(return_value=True))
@patch('os.listdir', MagicMock(return_value=['mt41692_pciconf0.1'])) 
class TestThermal:

    def test_chassis_thermal(self, *args):
        chassis = Chassis()
        thermal_list = chassis.get_all_thermals()
        assert thermal_list


    def test_hwmon_read(self, *args):
        from sonic_platform import thermal_bf3 as thermal
        from sonic_platform.thermal_bf3 import Thermal, ThermalType

        thermal.read_fs = MagicMock(return_value=83123)
        t = Thermal(name='test', thermal_type=ThermalType.SFP, hwmon_path='/tmp/', ht=95, cht=100)
        assert t.get_temperature() == 83.123
        assert t.get_high_critical_threshold() == 83.123


    def test_ssd(self, *args):
        from sonic_platform import thermal_bf3 as thermal
        from sonic_platform.thermal_bf3 import initialize_ssd_thermals
        thermal.read_smartctl = MagicMock(return_value=json.loads(smartctl_output))
        t = initialize_ssd_thermals()
        assert len(t) == 1
        assert t[0].get_temperature() == 42
        assert t[0].get_high_threshold() == 90
        assert t[0].get_high_critical_threshold() == 100


    def test_thermal_get(self, *args):
        from sonic_platform import thermal_bf3 as thermal
        from sonic_platform.thermal_bf3 import Thermal, ThermalType

        temp_test_mocked_vals = [123, 10.5, -1, None]

        for tv in temp_test_mocked_vals:
            thermal.read_temp_mlxbf = MagicMock(return_value=tv)
            t = Thermal(name='test', thermal_type=ThermalType.MLXBF, mlxbf_sensor_name='test', ht=95, cht=100)
            assert t.get_temperature() == tv
            assert t.get_high_threshold() == 95

            assert t.get_high_critical_threshold() == 100
            assert t.get_low_threshold() == 'N/A'
            assert t.get_low_critical_threshold() == 'N/A'

        for tv in temp_test_mocked_vals:
            thermal.read_temp_hwmon = MagicMock(return_value=tv)
            t = Thermal(name='test', thermal_type=ThermalType.SFP, hwmon_path='/tmp/', ht=95)
            assert t.get_temperature() == tv
            assert t.get_high_threshold() == 95
            assert t.get_high_critical_threshold() == tv
            assert t.get_low_threshold() == 'N/A'
            assert t.get_low_critical_threshold() == 'N/A'
