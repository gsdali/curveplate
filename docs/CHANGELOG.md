# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-26

### Added
- CLI tool with argparse for generating model railway track templates
- Support for straight, curve, and transition (clothoid) templates
- DXF export using ezdxf library
- PDF export using reportlab library
- 3D STEP export using cadquery (optional dependency)
- ISO paper sizes (A0-A4) with optional title block and border
- GitHub Actions CI workflow for testing and linting
- GitHub Actions workflow for syncing issues to local TASKS.md
- Issue templates for bugs, features, and tasks
- GitHub Projects integration with custom fields
- Comprehensive test suite (35 tests)

### Features
- **Straight templates**: Simple rectangles with specified gauge and length
- **Curve templates**: Arc segments with configurable radius and angle
- **Transition templates**: Clothoid/Euler spiral curves with perpendicular end caps
- **3D export**: Extruded templates for CNC milling or 3D printing

[0.1.0]: https://github.com/gsdali/curveplate/releases/tag/v0.1.0
