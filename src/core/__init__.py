# -*- coding: utf-8 -*-
"""Core module - Interface principal com DWSIM Automation."""

from .automation import DWSIMAutomation
from .flowsheet import FlowsheetManager
from .incremental import IncrementalSimulationWorkflow

__all__ = ["DWSIMAutomation", "FlowsheetManager", "IncrementalSimulationWorkflow"]
