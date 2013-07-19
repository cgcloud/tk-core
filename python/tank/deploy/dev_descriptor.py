# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Descriptor that let's you work with local, unversioned files.
This is handy when doing development.

"""

import os
import sys

from ..errors import TankError
from .descriptor import AppDescriptor

class TankDevDescriptor(AppDescriptor):
    """
    Represents a local item. This item is never downloaded
    into the local storage, you interact with it directly.
    """

    def __init__(self, pipeline_config, location_dict):
        super(TankDevDescriptor, self).__init__(pipeline_config, location_dict)

        # platform specific location support
        system = sys.platform
        platform_keys = {"linux2": "linux_path", "darwin": "mac_path", "win32": "windows_path"}
        platform_key = platform_keys.get(system, "unsupported_os")

        if platform_key not in location_dict and "path" in location_dict:
            self._path = location_dict.get("path", "")
        elif platform_key and platform_key in location_dict:
            self._path = location_dict.get(platform_key, "")
        else:
            raise TankError("Invalid dev descriptor! Could not find a path or a %s entry in the "
                            "location dict %s." % (platform_key, location_dict))

        # replace magic token {PIPELINE_CONFIG} with path to pipeline configuration
        self._path = self._path.replace("{PIPELINE_CONFIG}", pipeline_config.get_path()) 
        
        # lastly, resolve environment variables
        self._path = os.path.expandvars(self._path)
        
        # and normalise:
        self._path = os.path.normpath(self._path)
        
        # if there is a version defined in the location dict
        # (this is handy when doing framework development, but totally
        #  non-required for finding the code) 
        self._version = "Undefined"
        if "version" in location_dict:
            self._version = location_dict.get("version")

    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk
        """
        # use folder name
        bn = os.path.basename(self._path)
        (name, ext) = os.path.splitext(bn)
        return name

    def get_version(self):
        """
        Returns the version number string for this item
        """
        return self._version

    def get_path(self):
        """
        returns the path to the folder where this item resides
        """
        return self._path

    def exists_local(self):
        """
        Returns true if this item exists in a local repo
        """
        return os.path.exists(self._path)

    def download_local(self):
        """
        Retrieves this version to local repo
        """
        # do nothing!

    def find_latest_version(self):
        """
        Returns a descriptor object that represents the latest version
        """
        # we are always the latest version :)
        return self


