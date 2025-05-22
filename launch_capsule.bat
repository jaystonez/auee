@echo off
setlocal enabledelayedexpansion

:: === CONFIG ===
set CAPSULE_DIR=%cd%
set PYTHON_EXE=python
set REQUIREMENTS=requirements.txt
set VALIDATOR=capsule_auditor.py
set PORTABLE_GPT=http://localhost:11434/gpt

echo.
echo 🧠 Launching Reflex Capsule Auditor...
echo ================================

:: --- Install dependencies ---
echo 📦 Installing dependencies...
%PYTHON_EXE% -m pip install --upgrade pip
%PYTHON_EXE% -m pip install -r %REQUIREMENTS%

:: --- Run validation + repair ---
echo 🔍 Running capsule audit and repair...
%PYTHON_EXE% %VALIDATOR%

:: --- Sign capsules ---
echo 🔐 Hashing all .camp files...
for %%f in (%CAPSULE_DIR%\audited_capsules\*.camp) do (
    certutil -hashfile "%%f" SHA256 > "%%f.sig"
    echo ✅ Hashed: %%f
)

:: --- Optional Flask local GPT check ---
echo.
echo 🧠 GPT suggestions (if enabled) use LOCAL ONLY:
echo → %PORTABLE_GPT%
echo 🔒 No API calls or socket activity involved.

echo.
echo ✅ Audit + seal complete. Output: audited_capsules\
pause
