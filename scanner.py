# scanner.py — CyberMAP 2.0 Endpoint Security Posture Scanner
# Standalone script. Run separately from the Streamlit app:
#     python scanner.py                    (uses real hostname)
#     python scanner.py "Finance-PC-01"    (uses a custom endpoint label)
#
# Performs 6 read-only checks and writes one JSON evidence report.
# Nothing on the system is changed by this script.
#
# NOTE: All console output uses plain ASCII characters only (no emoji,
# no special symbols). This is required because Windows Task Scheduler
# runs scripts using the system's default console code page (cp1252 on
# most Windows installs), which cannot represent emoji or unicode
# symbols and will crash the script with a UnicodeEncodeError if they
# are printed. Using ASCII-only output makes the scanner run reliably
# both in an interactive terminal and under an unattended scheduled task.

import subprocess
import platform
import json
import hashlib
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None


# ── Utility: run a Windows command safely ──────────────────────
def run_command(cmd_list):
    try:
        result = subprocess.run(
            cmd_list, capture_output=True, text=True,
            shell=False, timeout=20
        )
        return result.stdout
    except Exception as e:
        return f"ERROR running command: {e}"


# ── Check 1 — Firewall Status ──────────────────────────────────
def check_firewall():
    output = run_command(
        ["netsh", "advfirewall", "show", "allprofiles", "state"]
    )
    lines = [l.strip() for l in output.splitlines() if "state" in l.lower()]
    on_count = sum(1 for l in lines if l.lower().endswith("on"))
    all_on = on_count >= 3

    status = "PASS" if all_on else "FAIL"
    return {
        "check": "Firewall Status",
        "nist_ref": "PR.PS-05",
        "iso_ref": "ISO 8.22",
        "status": status,
        "raw_output": output.strip()[:800],
    }


# ── Check 2 — Antivirus / EDR Status ───────────────────────────
def check_antivirus():
    """
    WMI (and the underlying COM library) must have COM explicitly
    initialised on the CURRENT thread before use, and the wmi module
    itself connects to WMI the moment it is imported. Both the import
    and the CoInitialize call are therefore done lazily, inside this
    function, so it works correctly whether called from a plain
    terminal script or from inside Streamlit's managed thread.
    """
    com_initialized = False
    try:
        import pythoncom
        pythoncom.CoInitialize()
        com_initialized = True

        import wmi
        c = wmi.WMI(namespace="root\\SecurityCenter2")
        products = c.AntiVirusProduct()
        names = [p.displayName for p in products]
        status = "PASS" if len(names) > 0 else "FAIL"
        return {
            "check": "Antivirus / EDR Status",
            "nist_ref": "PR.PS-04",
            "iso_ref": "ISO 8.7",
            "status": status,
            "raw_output": ", ".join(names) if names else "No antivirus product registered",
        }
    except Exception as e:
        return {
            "check": "Antivirus / EDR Status",
            "nist_ref": "PR.PS-04",
            "iso_ref": "ISO 8.7",
            "status": "ERROR",
            "raw_output": f"Could not query SecurityCenter2: {e}",
        }
    finally:
        if com_initialized:
            import pythoncom
            pythoncom.CoUninitialize()


# ── Check 3 — Password Policy ──────────────────────────────────
def check_password_policy():
    output = run_command(["net", "accounts"])
    min_len = 0
    for line in output.splitlines():
        if "minimum password length" in line.lower():
            digits = "".join(ch for ch in line if ch.isdigit())
            if digits:
                min_len = int(digits)

    if min_len >= 12:
        status = "PASS"
    elif min_len >= 8:
        status = "PARTIAL"
    else:
        status = "FAIL"

    return {
        "check": "Password Policy",
        "nist_ref": "PR.AA-05",
        "iso_ref": "ISO 8.2",
        "status": status,
        "raw_output": f"Minimum password length detected: {min_len} characters\n\n{output.strip()[:500]}",
    }


# ── Check 4 — Disk Encryption (BitLocker) ──────────────────────
def check_encryption():
    output = run_command(["manage-bde", "-status"])
    encrypted = "Percentage Encrypted: 100%" in output
    status = "PASS" if encrypted else "FAIL"
    return {
        "check": "Disk Encryption",
        "nist_ref": "PR.DS-01",
        "iso_ref": "ISO 8.24",
        "status": status,
        "raw_output": output.strip()[:800],
    }


# ── Check 5 — Patch / Update Status ────────────────────────────
def check_updates():
    output = run_command(["wmic", "qfe", "get", "HotFixID,InstalledOn"])
    lines = [l for l in output.strip().splitlines() if l.strip()]
    has_updates = len(lines) > 1  # header line + at least 1 update
    status = "PASS" if has_updates else "FAIL"
    return {
        "check": "Patch / Update Status",
        "nist_ref": "PR.PS-02",
        "iso_ref": "ISO 8.8",
        "status": status,
        "raw_output": output.strip()[:800],
    }


# ── Check 6 — Unnecessary / Risky Services ─────────────────────
RISKY_SERVICE_KEYWORDS = ["telnet", "remote registry", "ftp"]

def check_risky_services():
    if psutil is None:
        return {
            "check": "Unnecessary Services",
            "nist_ref": "PR.PS-01",
            "iso_ref": "ISO 8.9",
            "status": "ERROR",
            "raw_output": "psutil module not available",
        }
    try:
        running = []
        for s in psutil.win_service_iter():
            try:
                if s.status() == "running":
                    running.append(s.name())
            except Exception:
                continue

        found_risky = [
            svc for svc in running
            if any(keyword in svc.lower() for keyword in RISKY_SERVICE_KEYWORDS)
        ]
        status = "FAIL" if found_risky else "PASS"
        return {
            "check": "Unnecessary Services",
            "nist_ref": "PR.PS-01",
            "iso_ref": "ISO 8.9",
            "status": status,
            "raw_output": (
                f"Risky services found: {found_risky}"
                if found_risky else
                "No risky services (Telnet, Remote Registry, FTP) found running"
            ),
        }
    except Exception as e:
        return {
            "check": "Unnecessary Services",
            "nist_ref": "PR.PS-01",
            "iso_ref": "ISO 8.9",
            "status": "ERROR",
            "raw_output": f"Could not enumerate services: {e}",
        }


# ── Run all checks and build the report ────────────────────────
def run_full_scan(endpoint_label=None):
    display_hostname = endpoint_label if endpoint_label else platform.node()

    print("=" * 55)
    print("  CyberMAP 2.0 - Endpoint Security Posture Scanner")
    print("=" * 55)
    print(f"  Endpoint: {display_hostname}")
    print(f"  OS:       {platform.platform()}")
    print(f"  Time:     {datetime.now().isoformat()}")
    print("=" * 55)
    print()

    checks = [
        ("1/6", check_firewall),
        ("2/6", check_antivirus),
        ("3/6", check_password_policy),
        ("4/6", check_encryption),
        ("5/6", check_updates),
        ("6/6", check_risky_services),
    ]

    results = []
    for step_label, check_fn in checks:
        result = check_fn()
        icon = {
            "PASS": "[OK]",
            "PARTIAL": "[!!]",
            "FAIL": "[XX]",
            "ERROR": "[ERR]",
        }.get(result["status"], "[??]")
        print(f"[{step_label}] {result['check']:<28} {icon} {result['status']}")
        results.append(result)

    print()

    summary = {
        "total": len(results),
        "passed":  sum(1 for r in results if r["status"] == "PASS"),
        "partial": sum(1 for r in results if r["status"] == "PARTIAL"),
        "failed":  sum(1 for r in results if r["status"] == "FAIL"),
        "errors":  sum(1 for r in results if r["status"] == "ERROR"),
    }

    report = {
        "scan_metadata": {
            "hostname": display_hostname,
            "actual_hostname": platform.node(),
            "os": platform.platform(),
            "scan_time": datetime.now().isoformat(),
            "scanner_version": "1.0",
        },
        "results": results,
        "summary": summary,
    }

    # Hash the whole report for integrity reference
    report_bytes = json.dumps(report, sort_keys=True).encode()
    report["report_hash"] = hashlib.sha256(report_bytes).hexdigest()

    # Use the endpoint label in the filename too, so files don't overwrite
    safe_label = display_hostname.replace(" ", "_")
    filename = (
        f"CyberMAP_ScanReport_{safe_label}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=" * 55)
    print(f"  Scan complete: {summary['passed']} Passed, "
          f"{summary['partial']} Partial, {summary['failed']} Failed, "
          f"{summary['errors']} Errors")
    print(f"  Report saved: {filename}")
    print("=" * 55)

    return filename


if __name__ == "__main__":
    import sys
    endpoint_label = None
    if len(sys.argv) > 1:
        endpoint_label = sys.argv[1]
    run_full_scan(endpoint_label=endpoint_label)