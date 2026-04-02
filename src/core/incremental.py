# -*- coding: utf-8 -*-
"""Incremental unit-operation workflow helpers for DWSIM automation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from .automation import DWSIMAutomation
from .flowsheet import FlowsheetManager
from ..visualization.reports import ReportGenerator

logger = logging.getLogger(__name__)


class IncrementalSimulationWorkflow:
    """Execute and persist a flowsheet one unit operation at a time.

    This helper is intentionally conservative: each new unit operation should be
    added only after the previous state converges. After every successful step,
    artifacts can be exported:

    - Flowsheet snapshot (`.dwxmz`)
    - Excel workbook (`.xlsx`) with stream/equipment tables
    - Python script (`.py`) that generated or modified the flowsheet
    """

    def __init__(
        self,
        dwsim: DWSIMAutomation,
        flowsheet: Any,
        manager: FlowsheetManager,
    ):
        self.dwsim = dwsim
        self.flowsheet = flowsheet
        self.manager = manager
        self.reports = ReportGenerator()

    @classmethod
    def create_new(
        cls,
        dwsim: Optional[DWSIMAutomation] = None,
    ) -> "IncrementalSimulationWorkflow":
        """Create a workflow with a fresh flowsheet and manager."""
        dwsim = dwsim or DWSIMAutomation()
        dwsim.initialize()
        flowsheet = dwsim.create_flowsheet()
        manager = FlowsheetManager(flowsheet, dwsim)
        return cls(dwsim=dwsim, flowsheet=flowsheet, manager=manager)

    def run_step(self, step_name: str) -> dict:
        """Run a solver pass for the current flowsheet state."""
        result = self.dwsim.calculate(self.flowsheet)
        if result["success"]:
            logger.info("Step '%s' converged successfully.", step_name)
        else:
            logger.warning("Step '%s' failed: %s", step_name, result["errors"])
        return result

    def persist_step_artifacts(
        self,
        step_name: str,
        output_dir: str,
        python_code: Optional[str] = None,
        include_streams: bool = True,
        include_equipment: bool = True,
    ) -> dict[str, Path]:
        """Persist all artifacts generated for a successful step."""
        safe_step = self._slugify(step_name)
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        flowsheet_path = out_dir / f"{safe_step}.dwxmz"
        excel_path = out_dir / f"{safe_step}.xlsx"
        script_path = out_dir / f"{safe_step}.py"

        self.dwsim.save_flowsheet(self.flowsheet, str(flowsheet_path))
        self.reports.export_to_excel(
            self.flowsheet,
            str(excel_path),
            include_streams=include_streams,
            include_equipment=include_equipment,
        )

        if python_code:
            script_path.write_text(python_code, encoding="utf-8")
            logger.info("Saved Python automation script: %s", script_path)

        artifacts = {
            "flowsheet": flowsheet_path,
            "excel": excel_path,
        }
        if python_code:
            artifacts["python"] = script_path

        return artifacts

    def run_step_and_persist(
        self,
        step_name: str,
        output_dir: str,
        python_code: Optional[str] = None,
        include_streams: bool = True,
        include_equipment: bool = True,
    ) -> dict:
        """Run one incremental step and persist artifacts only on success."""
        result = self.run_step(step_name)
        artifacts: dict[str, Any] = {}
        if result["success"]:
            artifacts = self.persist_step_artifacts(
                step_name=step_name,
                output_dir=output_dir,
                python_code=python_code,
                include_streams=include_streams,
                include_equipment=include_equipment,
            )

        return {
            "step_name": step_name,
            "result": result,
            "artifacts": artifacts,
        }

    @staticmethod
    def _slugify(name: str) -> str:
        token = "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
        return token or "step"
