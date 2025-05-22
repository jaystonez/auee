import os, zipfile, json, shutil, yaml, hashlib
from pathlib import Path

AUDITOR_OUTPUT_DIR = "/mnt/data/audited_capsules"
os.makedirs(AUDITOR_OUTPUT_DIR, exist_ok=True)

KNOWN_PERMISSIONS = {
    "tabs", "activeTab", "storage", "scripting", "microphone", "camera",
    "clipboardRead", "clipboardWrite", "webRequest", "webNavigation",
    "notifications", "contextMenus", "idle", "windows", "debugger", "offscreen", "power"
}

DEFAULT_PERSONALITY = {
    "agent_personality": {
        "mode": "reflexive",
        "memory_hooks": True,
        "dashboard_ui": True
    }
}

DEFAULT_GPT_HOOK = {
    "endpoint": "http://localhost:11434/gpt",
    "persona_file": "aura-persona.json",
    "fallback_prompt": "Describe any problems in this capsule."
}

def gpt_assist(prompt, url="http://localhost:11434/gpt"):
    try:
        import requests
        res = requests.post(url, json={"prompt": prompt})
        return res.json().get("response", "No reply.")
    except Exception as e:
        return f"[GPT Error] {e}"

def scan_and_repair_capsules(base_dir="/mnt/data", dry_run=False):
    repaired_files, summaries = [], {}
    for fname in os.listdir(base_dir):
        if fname.endswith((".zip", ".camp")):
            full_path = os.path.join(base_dir, fname)
            capsule_name = Path(fname).stem
            extract_dir = os.path.join(base_dir, f"extracted_{capsule_name}")
            shutil.rmtree(extract_dir, ignore_errors=True)
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(full_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            manifest_path = find_file(extract_dir, "manifest.json")
            reflect_path = find_file(extract_dir, "reflect.yaml")
            assist_path = find_file(extract_dir, "agent_assist.yaml")
            personality_path = find_file(extract_dir, "agent_personality.yaml")
            audit_log = os.path.join(extract_dir, "repair.log")

            with open(audit_log, "w") as log:
                log.write("Capsule Repair Summary:\n")
                score, unknown_perms = {"manifest_integrity": 100, "permission_risk": "low", "total": 100}, []

                if manifest_path:
                    score, unknown_perms = repair_and_validate_manifest(manifest_path, extract_dir, log, dry_run)
                if not reflect_path:
                    reflect_path = os.path.join(extract_dir, "reflect.yaml")
                    write_reflect_yaml(reflect_path, extract_dir, dry_run, score)
                else:
                    regenerate_reflect_yaml(reflect_path, extract_dir, dry_run, score)

                if not personality_path:
                    with open(os.path.join(extract_dir, "agent_personality.yaml"), "w") as pfile:
                        yaml.dump(DEFAULT_PERSONALITY, pfile)
                    log.write("🧠 Injected default agent_personality.yaml\n")

                # 🤖 GPT Suggestion via agent_assist.yaml
                if assist_path:
                    with open(assist_path) as f:
                        assist = yaml.safe_load(f).get("agent_assist", {})
                        if assist.get("enabled") and "gpt_id" in assist:
                            note = gpt_assist("Why did this capsule fail validation?", assist.get("help_url", "http://localhost:11434/gpt"))
                            log.write(f"\n🧠 GPT Suggestion ({assist['gpt_id']}): {note}\n")

                summary = {
                    "score": score["total"],
                    "unknown_permissions": unknown_perms,
                    "files": count_files(extract_dir),
                    "repaired": not dry_run
                }

                summaries[f"{capsule_name}_REPAIRED.camp"] = summary
                with open(os.path.join(extract_dir, "audit_summary.json"), "w") as f:
                    json.dump(summary, f, indent=2)

                log.write(f"\n⭐ Score: {score['total']}/100\n")

            if not dry_run:
                repaired_path = os.path.join(AUDITOR_OUTPUT_DIR, f"{capsule_name}_REPAIRED.camp")
                with zipfile.ZipFile(repaired_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(extract_dir):
                        for file in files:
                            full_file = os.path.join(root, file)
                            arcname = os.path.relpath(full_file, start=extract_dir)
                            zipf.write(full_file, arcname=arcname)
                repaired_files.append(repaired_path)

                # Hash it
                with open(repaired_path, "rb") as f, open(repaired_path + ".sig", "w") as sig:
                    sha = hashlib.sha256(f.read()).hexdigest()
                    sig.write(f"{sha}  {os.path.basename(repaired_path)}")

            shutil.rmtree(extract_dir)
    return repaired_files, summaries

def count_files(root_dir):
    return sum(len(files) for _, _, files in os.walk(root_dir))

def find_file(root_dir, filename):
    for root, _, files in os.walk(root_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def repair_and_validate_manifest(manifest_path, base_dir, log, dry_run):
    unknown_perms, score = [], {"manifest_integrity": 100, "permission_risk": "low", "total": 100}
    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError as e:
            log.write(f"❌ JSON error: {e}\n")
            score["manifest_integrity"] = 0
            score["total"] -= 30
            return score, unknown_perms

    required_fields = ["name", "version", "manifest_version"]
    defaults = {
        "name": "Operator Extension",
        "version": "1.0",
        "manifest_version": 3,
        "permissions": [],
        "background": {"service_worker": "background.js"}
    }

    for key in required_fields:
        if key not in manifest:
            manifest[key] = defaults[key]
            log.write(f"⚠️ Missing key '{key}' filled.\n")
            score["manifest_integrity"] -= 10
            score["total"] -= 10

    permissions = manifest.get("permissions", [])
    for perm in permissions:
        if perm not in KNOWN_PERMISSIONS:
            unknown_perms.append(perm)
            score["permission_risk"] = "medium"
            score["total"] -= 5

    def validate_file(relpath, label):
        full = os.path.join(base_dir, relpath)
        if not os.path.exists(full):
            log.write(f"❌ {label} missing: {relpath}\n")
            score["total"] -= 5
        else:
            log.write(f"✅ {label} found: {relpath}\n")

    if "content_scripts" in manifest:
        for cs in manifest["content_scripts"]:
            for js in cs.get("js", []):
                validate_file(js, "Content Script")

    if "background" in manifest and "service_worker" in manifest["background"]:
        validate_file(manifest["background"]["service_worker"], "Service Worker")

    if "action" in manifest and "default_popup" in manifest["action"]:
        validate_file(manifest["action"]["default_popup"], "Popup HTML")

    manifest["repaired_by"] = "Agent0 Auditor v1.0"

    if not dry_run:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    return score, unknown_perms

def regenerate_reflect_yaml(reflect_path, root_dir, dry_run, score):
    discovered = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith((".js", ".html", ".py")):
                rel = os.path.relpath(os.path.join(root, file), start=root_dir)
                discovered.append(rel)

    data = {
        "capsule": "Auto-Repaired Reflex Capsule",
        "files": discovered,
        "repaired": True,
        "repaired_by": "Agent0 Auditor v1.0",
        "score": score,
        "gpt_hook": DEFAULT_GPT_HOOK
    }

    if not dry_run:
        with open(reflect_path, "w") as f:
            yaml.dump(data, f)

def write_reflect_yaml(reflect_path, root_dir, dry_run, score):
    regenerate_reflect_yaml(reflect_path, root_dir, dry_run, score)

