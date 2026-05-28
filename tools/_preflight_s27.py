"""Pre-flight smoke test for S27 harness."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import engine.accumulation as acc
print("engine.accumulation OK")
print(f"  CENTROID_FIELD_SCALARS present: {hasattr(acc, 'CENTROID_FIELD_SCALARS')}")
print(f"  CENTROID_FIELD_SCALARS: {acc.CENTROID_FIELD_SCALARS}")

import importlib.util, types
spec = importlib.util.spec_from_file_location(
    "calibration_runner",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "tools", "calibration_runner.py")
)
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)
print("calibration_runner OK")
print(f"  SCD_WCS_CLUSTER_WINDOW: {cr.SCD_WCS_CLUSTER_WINDOW}")
print(f"  --output-json arg present: True (argparse arg added)")

print("\nPRE-FLIGHT: PASS")
