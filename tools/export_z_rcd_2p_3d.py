#!/usr/bin/env python3
import sys
from tools.export_z_rcd_3d import main

if __name__ == "__main__":
    sys.argv.extend(["--poles", "2"])
    raise SystemExit(main())
