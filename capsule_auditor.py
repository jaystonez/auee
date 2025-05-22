import argparse
import json
import os
from capsule_audit_utils import scan_and_repair_capsules, AUDITOR_OUTPUT_DIR

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and repair AI capsules.")
    parser.add_argument("--audit-only", action="store_true", help="Dry run: only audit, don't modify or repackage.")
    args = parser.parse_args()

    repaired, summary = scan_and_repair_capsules(dry_run=args.audit_only)

    if not args.audit_only:
        import ace_tools as tools
        tools.display_dataframe_to_user(name="Repaired Capsules", dataframe={"Repaired Capsules": repaired})

        with open(os.path.join(AUDITOR_OUTPUT_DIR, "audit_summary_all.json"), "w") as f:
            json.dump(summary, f, indent=2)
