
import os

from .utils.access import AccessHub
from .utils.logging import logger
from .utils.parameters import (ARG_CONSOLE, ARG_DEBUG, ARG_DEV_CHANNEL,
                               ARG_EXECUTABLE_TOOLS, ARG_LOCAL_DRIVE, ARG_OUT_OF_SERVICE,
                               ARG_QUEUE_WORKER_NUM, ARG_RESOURCE,
                               ARG_SUBPROCESS_NUM)
from .utils.singleton import ThreadSafeSingleton


class ClassProperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class Environment(metaclass=ThreadSafeSingleton):
    def __init__(self, *args, console_mode=False, **kwargs):
        self.param = {key: value.lower() if isinstance(value, str) else value for key, value in kwargs.items()}
        self.param.update({
            ARG_CONSOLE: console_mode
        })
        # update server config to Environment
        # local mode: Local_server_config.json
        # cloud: IBM cloud runtime env
        # self.update(AccessHub().server_configs)

    @classmethod
    def register_credentials(cls, key_dict: dict = {}):
        AccessHub().keys.update(key_dict)

    @classmethod
    def append_server_config(cls, payload: dict = {}):
        """add customized server config. It could represent some simple parameters and application paths. 

        Payload Example:
        {
            "win32": {
                "queue_worker_num": 1,
                "subprocess_num": 2,
                "dev_channel": "T015BP2HUU9#G015P1L6L7J",
                "oos": false,
                "debug": true,
                "executable_tools": {
                    "blender": "P:\\Editors\\Blender\\blender-2.93.3-windows-x64",
                    "cyclicgen": "P:\\Editors\\CyclicGen",
                    "unity": "C:\\Dev\\Editors\\Unity\\2020.3.24f1\\Editor"
                },
                "dnn_models": {
                    "swinir_denoising_15": "D:\\Trained_Models\\SwinIR\\Model\\004_grayDN_DFWB_s128w8_SwinIR-M_noise15.pth",
                    "swinir_denoising_25": "D:\\Trained_Models\\SwinIR\\Model\\004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth",
                    "swinir_denoising_50": "D:\\Trained_Models\\SwinIR\\Model\\004_grayDN_DFWB_s128w8_SwinIR-M_noise50.pth"
                },
                "mars_dicom_data_root": "G:\\Shared drives"
            },
            "linux": {
                "queue_worker_num": 4,
                "subprocess_num": 5,
                "dev_channel": "T015BP2HUU9#G015P1L6L7J",
                "oos": false,
                "debug": false,
                "executable_tools": {
                    "unreal_engine": "",
                    "blender": ""
                },
                "mars_dicom_data_root": "/gd"
            }
        }
        """
        Environment().param.update(payload)

        # add executable application path to sys environment
        for key, path in Environment().param.get(ARG_EXECUTABLE_TOOLS, {}).items():
            if not path:
                logger.debug(f'Executable Tool [{key}] path is invalid!')
            else:
                logger.debug(f'Executable Tool [{key}] : added path [{path}] to system env.')
                os.environ["PATH"] += os.pathsep + path

    def get(self, key: str):
        # retrieve customized key / value from server runtime configuration dict.
        return self.param.get(key, None)

    @ClassProperty
    def console_mode(cls):
        # check the running mode
        return Environment().param.get(ARG_CONSOLE, True)

    @ClassProperty
    def debug_mode(cls):
        # check the running mode
        return Environment().param.get(ARG_DEBUG, False)

    @ClassProperty
    def resource(cls):
        return Environment().param.get(ARG_RESOURCE, None)

    @ClassProperty
    def dev_channel(cls):
        # set 'bot-compipe-debug' to be the default channel for posting error logs
        return Environment().param.get(ARG_DEV_CHANNEL, None)

    @ClassProperty
    def out_of_service(cls):
        # set hkg to be the default space for PROTP
        return Environment().param.get(ARG_OUT_OF_SERVICE, False)

    @ClassProperty
    def worker_num(cls):
        # check the running mode
        return Environment().param.get(ARG_QUEUE_WORKER_NUM, 1)

    @ClassProperty
    def subprocess_num(cls):
        # check the running mode
        return Environment().param.get(ARG_SUBPROCESS_NUM, 5)

    @ClassProperty
    def local_drive(cls):
        # check the running mode
        return Environment().param.get(ARG_LOCAL_DRIVE, None)

    def __str__(self):
        return '{0}\n{1}\n{2}\n{0}'.format('==========ENV==========',
                                           '|'.join(['dev_channel']),
                                           '|'.join([Environment.dev_channel]))
