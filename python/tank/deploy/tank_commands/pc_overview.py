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
Methods for handling of the tank command

"""

from ... import pipelineconfig


from ...util import shotgun
from ...platform import constants
from ...errors import TankError

from .action_base import Action

import sys
import os


class PCBreakdownAction(Action):
    
    def __init__(self):
        Action.__init__(self, 
                        "configurations", 
                        Action.PC_LOCAL, 
                        ("Shows an overview of the different configurations registered with this project."), 
                        "Admin")
    
    def run(self, log, args):
        if len(args) != 0:
            raise TankError("This command takes no arguments!")
        
        log.info("Fetching data from Shotgun...")
        project_id = self.tk.pipeline_configuration.get_project_id()
        
        sg = shotgun.create_sg_connection()
        
        proj_data = sg.find_one("Project", [["id", "is", project_id]], ["name"])
        log.info("")
        log.info("")
        log.info("=" * 70)
        log.info("Available Configurations for Project '%s'" % proj_data.get("name"))
        log.info("=" * 70)
        log.info("")
        
        data = sg.find(constants.PIPELINE_CONFIGURATION_ENTITY, 
                       [["project", "is", {"type": "Project", "id": project_id}]],
                       ["code", "users", "mac_path", "windows_path", "linux_path"])
        for d in data:
            
            if len(d.get("users")) == 0:
                log.info("Configuration '%s' (Public)" % d.get("code"))
            else:
                log.info("Configuration '%s' (Private)" % d.get("code"))
                
            log.info("-------------------------------------------------------")
            log.info("")
            
            if d.get("code") == constants.PRIMARY_PIPELINE_CONFIG_NAME:
                log.info("This is the Project Master Configuration. It will be used whenever "
                         "this project is accessed from a studio level tank command or API "
                         "constructor.")
            
            log.info("")
            lp = d.get("linux_path")
            mp = d.get("mac_path")
            wp = d.get("windows_path")
            if lp is None:
                lp = "[Not defined]"
            if wp is None:
                wp = "[Not defined]"
            if mp is None:
                mp = "[Not defined]"
            
            log.info("Linux Location:  %s" % lp )
            log.info("Winows Location: %s" % wp )
            log.info("Mac Location:    %s" % mp )
            log.info("")
            
            
            # check for core API etc. 
            storage_map = {"linux2": "linux_path", "win32": "windows_path", "darwin": "mac_path" }
            local_path = d.get(storage_map[sys.platform])
            if local_path is None:
                log.info("The Configuration is not accessible from this computer!")
                
            elif not os.path.exists(local_path):
                log.info("The Configuration cannot be found on disk!")
                
            else:
                # yay, exists on disk
                local_tank_command = os.path.join(local_path, "tank")
                
                if os.path.exists(os.path.join(local_path, "install", "core", "_core_upgrader.py")):
                    api_version = pipelineconfig.get_core_api_version_for_pc(local_path)
                    log.info("This configuration is running its own version (%s)"
                             " of the Sgtk API." % api_version)
                    log.info("If you want to check for core API updates you can run:")
                    log.info("> %s core" % local_tank_command)
                    log.info("")
                    
                else:
                    
                    log.info("This configuration is using a shared version of the Sgtk API."
                             "If you want it to run its own independent version "
                             "of the Sgtk Core API, you can run:")
                    log.info("> %s localize" % local_tank_command)
                    log.info("")
                
                log.info("If you want to check for app or engine updates, you can run:")
                log.info("> %s updates" % local_tank_command)
                log.info("")
            
                log.info("If you want to change the location of this configuration, you can run:")
                log.info("> %s move_configuration" % local_tank_command)
                log.info("")
            
            if len(d.get("users")) == 0:
                log.info("This is a public configuration. In Shotgun, the actions defined in this "
                         "configuration will be on all users' menus.")
            
            elif len(d.get("users")) == 1:
                log.info("This is a private configuration. In Shotgun, only %s will see the actions "
                         "defined in this config. If you want to add additional members to this "
                         "configuration, navigate to the Shotgun Pipeline Configuration Page "
                         "and add them to the Users field." % d.get("users")[0]["name"])
            
            elif len(d.get("users")) > 1:
                users = ", ".join( [u.get("name") for u in d.get("users")] )
                log.info("This is a private configuration. In Shotgun, the following users will see "
                         "the actions defined in this config: %s. If you want to add additional "
                         "members to this configuration, navigate to the Shotgun Pipeline "
                         "Configuration Page and add them to the Users field." % users)
            
            log.info("")
            log.info("")
        
        
