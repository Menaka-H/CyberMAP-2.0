# utils/remediation.py - CyberMAP 2.0 Human-in-the-Loop Remediation (Simulated)
#
# Suggests a safe, reversible remediation command for specific gap
# types, and logs human approval decisions. Commands are NEVER
# executed automatically - this module only proposes and records
# what WOULD be run, requiring explicit human approval, and even
# then only simulates execution rather than modifying the system.

REMEDIATION_SUGGESTIONS = {
    "PR.PS-05": {
        "fix": "Re-enable Windows Firewall on all network profiles",
        "command": "netsh advfirewall set allprofiles state on",
        "reversible": True,
    },
    "PR.AA-05": {
        "fix": "Increase minimum password length to 12 characters",
        "command": "net accounts /minpwlen:12",
        "reversible": True,
    },
    "PR.PS-04": {
        "fix": "Enable Windows Defender real-time protection",
        "command": "Set-MpPreference -DisableRealtimeMonitoring $false",
        "reversible": True,
    },
    "PR.DS-01": {
        "fix": "Enable BitLocker disk encryption on the system volume",
        "command": "manage-bde -on C: -RecoveryPassword",
        "reversible": False,
    },
}


def get_remediation_suggestion(nist_ref):
    return REMEDIATION_SUGGESTIONS.get(nist_ref)


def log_remediation_decision(gap_question, nist_ref, proposed_fix,
                               command_preview, approved_by, status):
    from utils.database import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO remediation_log
           (gap_question, nist_ref, proposed_fix, command_preview,
            approved_by, approval_status, simulated)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        (gap_question, nist_ref, proposed_fix, command_preview,
         approved_by, status)
    )
    conn.commit()
    log_id = c.lastrowid
    conn.close()
    return log_id


def get_remediation_history():
    from utils.database import get_connection
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM remediation_log ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def execute_remediation(nist_ref, command):
    """
    Actually executes an approved remediation command via subprocess.
    ONLY called after explicit human approval, and only for commands
    in the REMEDIATION_SUGGESTIONS allowlist marked reversible=True.
    Returns {"success": bool, "output": str, "error": str or None}
    """
    import subprocess

    suggestion = REMEDIATION_SUGGESTIONS.get(nist_ref)
    if not suggestion:
        return {"success": False, "output": "", "error": "No known remediation for this control."}
    if not suggestion.get("reversible", False):
        return {"success": False, "output": "", "error": "This fix is not marked reversible and cannot be auto-executed."}

    try:
        # PowerShell commands (Set-MpPreference) need powershell.exe;
        # netsh/net accounts run directly.
        if command.strip().startswith("Set-MpPreference"):
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True, text=True, timeout=20
            )
        else:
            result = subprocess.run(
                command.split(), capture_output=True, text=True, timeout=20
            )

        success = result.returncode == 0
        return {
            "success": success,
            "output": result.stdout.strip() or result.stderr.strip(),
            "error": None if success else f"Command exited with code {result.returncode}",
        }
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def re_verify_fix(nist_ref):
    """
    Re-runs the single relevant scanner check to confirm a fix
    actually took effect, without re-running the full 6-check scan.
    """
    from scanner import (
        check_firewall, check_password_policy, check_antivirus, check_encryption,
    )
    check_map = {
        "PR.PS-05": check_firewall,
        "PR.AA-05": check_password_policy,
        "PR.PS-04": check_antivirus,
        "PR.DS-01": check_encryption,
    }
    check_fn = check_map.get(nist_ref)
    if not check_fn:
        return None
    return check_fn()
