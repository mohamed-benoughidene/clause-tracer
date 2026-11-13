"""Check the RESULT= line of a trial run. Usage: check-result.py run.log"""
import json
import sys

with open(sys.argv[1], errors="replace") as fh:
    line = next((ln for ln in fh if ln.startswith("RESULT=")), None)
if not line:
    print("FAIL: no RESULT= line")
    sys.exit(1)
data = json.loads(line[len("RESULT="):])
checks = {
    "frozen_matches_expectation": data.get("frozen") is (len(sys.argv) < 3 or sys.argv[2] != "unfrozen"),
    "page_a_exists": data.get("page_a_exists") is True,
    "a_api_ready": data.get("a_api_ready") is True,
    "roundtrip_before": data.get("a_roundtrip", {}).get("before", {}).get("theme") == "light",
    "roundtrip_after": data.get("a_roundtrip", {}).get("read_back", {}).get("theme") == "dark",
    "reached_b": data.get("c_reached_b") is True,
    "api_ready_on_b": data.get("c_api_ready_on_b") is True,
}
print(json.dumps(checks, indent=2))
if not all(checks.values()):
    print("FAIL: one or more checks false")
    sys.exit(1)
print("PASS: js_api round trip and page A->B navigation confirmed")
