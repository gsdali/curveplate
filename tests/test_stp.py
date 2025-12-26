"""Tests for STP export module."""

import tempfile
from pathlib import Path

import pytest

from curveplate.geometry import create_straight_template, create_curve_template
from curveplate.stp_export import export_stp


class TestStpExport:
    def test_straight_template_export(self):
        """Test exporting a straight template to STEP."""
        template = create_straight_template(gauge=9.0, length=100.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_straight"
            result = export_stp(template, output_path, thickness=3.0)

            assert result.exists()
            assert result.suffix == ".stp"

            # Check file has content
            content = result.read_text()
            assert "ISO-10303-21" in content
            assert "HEADER" in content
            assert "DATA" in content

    def test_curve_template_export(self):
        """Test exporting a curve template to STEP."""
        template = create_curve_template(gauge=9.0, radius=200.0, arc_degrees=45.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_curve"
            result = export_stp(template, output_path, thickness=2.0)

            assert result.exists()
            assert result.suffix == ".stp"

    def test_extension_handling(self):
        """Test that .stp extension is added correctly."""
        template = create_straight_template(gauge=9.0, length=50.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Without extension
            output_path = Path(tmpdir) / "no_ext"
            result = export_stp(template, output_path, thickness=1.0)
            assert result.name == "no_ext.stp"

            # With .stp extension
            output_path = Path(tmpdir) / "with_ext.stp"
            result = export_stp(template, output_path, thickness=1.0)
            assert result.name == "with_ext.stp"

            # With .step extension
            output_path = Path(tmpdir) / "step_ext.step"
            result = export_stp(template, output_path, thickness=1.0)
            assert result.name == "step_ext.step"
