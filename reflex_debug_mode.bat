@echo off
setlocal enabledelayedexpansion

set CAPSULE_DIR=%cd%
set PYTHON_EXE=python
set REQUIREMENTS=requirements.txt
set VALIDATOR=capsule_auditor.py

echo 🐛 Reflex Debug Mode: Verbose Audit Starting...
echo ==============================================

:: Upgrade and install packages
echo [DEBUG] Installing dependencies...
%PYTHON_EXE% -m pip install --upgrade pip
%PYTHON_EXE% -m pip install -r %REQUIREMENTS%

:: Run validator in dry-run mode to show issues but not overwrite
echo [DEBUG] Performing dry-run audit...
%PYTHON_EXE% %VALIDATOR% --audit-only

:: Show detailed folder contents
echo [DEBUG] Listing extracted capsule folders...
dir /s /b extracted_*

:: Show repair logs, if any
echo [DEBUG] Showing repair logs:
for /r %%f in (repair.log) do (
    echo --- %%f ---
    type "%%f"
)

echo [DEBUG] End of verbose output.
pause
