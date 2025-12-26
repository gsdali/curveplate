# Curveplate

Generate model railway flexible track laying templates as DXF, PDF, and 3D STP files.

## Installation

```bash
pip install curveplate
```

Or install from source:

```bash
git clone https://github.com/gsdali/curveplate.git
cd curveplate
pip install -e .
```

## Usage

### Straight Template

Generate a straight track template:

```bash
curveplate -g 9 -t straight -l 100
```

- `-g 9`: 9mm gauge (N scale)
- `-t straight`: Straight template
- `-l 100`: 100mm length

### Curve Template

Generate a curved track template:

```bash
curveplate -g 16.5 -t curve -r 300 -a 45 --right
```

- `-g 16.5`: 16.5mm gauge (OO/HO scale)
- `-t curve`: Curve template
- `-r 300`: 300mm inner radius
- `-a 45`: 45 degree arc
- `--right`: Curving to the right

### Transition Template

Generate a transition (easement) curve:

```bash
curveplate -g 9 -t transition -r 200 -l 150 --left
```

- `-g 9`: 9mm gauge
- `-t transition`: Transition template
- `-r 200`: End radius 200mm
- `-l 150`: Transition length 150mm
- `--left`: Curving to the left

### 3D STEP Export

Generate a 3D extruded template for CNC milling or 3D printing:

```bash
curveplate -g 9 -t straight -l 100 -3D 3
```

- `-3D 3`: Extrude to 3mm thickness, outputs STP file

For 3D export, install with the `stp` optional dependency:

```bash
pip install curveplate[stp]
```

## Command Reference

```
usage: curveplate [-h] [-v] [-o OUTPUT] [-p] [-d] [-s SIZE] [-b] [-3D THICKNESS]
                  -g GAUGE -t TYPE [-l LENGTH] [-a ARC] [-r RADIUS] [--left | --right]

Generate model railway flexible track laying templates

Output Options:
  -o, --output OUTPUT     Output filename (default: timestamp-based)
  -p, --pdf               Output PDF file
  -d, --dxf               Output DXF file
  -s, --size SIZE         Paper size: A0, A1, A2, A3, A4
  -b, --border            Add title block and drawing boundary
  -3D, --extrude THICKNESS  Extrusion thickness in mm, outputs STP file

Required Template Parameters:
  -g, --gauge GAUGE       Track gauge in mm (distance between rails)
  -t, --type TYPE         Template type: s(traight), c(urve), t(ransition)

Geometry Parameters:
  -l, --length LENGTH     Length in mm along inner rail
  -a, --arc ARC           Arc angle in degrees (for curves)
  -r, --radius RADIUS     Curve radius to inner rail in mm
  --left                  Curve to the left
  --right                 Curve to the right
```

## Common Gauges

| Scale | Prototype Guage | Gauge (mm) |
|-------|-----------------|------------|
| Z     | 1435mm          | 6.5        |
| N     | 1435mm          | 9          |
| 2mm   | 1067mm          | 7.1        |
| 2mm   | 1435mm          | 9.42       |
| 2mm   | 1600mm          | 10.5       |
| TT    | 1435mm          | 12         |
| HO/OO | 1435mm          | 16.5       |
| S     | 1435mm          | 22.5       |
| O     | 1435mm          | 32         |
| G     | 1435mm          | 45         |

## License

MIT License - see [LICENSE](LICENSE) for details.
