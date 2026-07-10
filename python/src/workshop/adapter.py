"""Demo adapter for ODIN control workshop

This class implements a simple adapter used for demonstration purposes in a

Tim Nicholls, STFC Application Engineering
"""
import logging
import sys

from tornado.escape import json_decode

from odin_control.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from odin_control.adapters.parameter_tree import ParameterTreeError

from workshop._version import __version__
from workshop.controller import WorkshopController, WorkshopError


class WorkshopAdapter(ApiAdapter):
    """System info adapter class for the ODIN server.

    This adapter provides ODIN clients with information about the server and the system that it is
    running on.
    """

    version = __version__
    controller_cls = WorkshopController
    error_cls = WorkshopError
    
