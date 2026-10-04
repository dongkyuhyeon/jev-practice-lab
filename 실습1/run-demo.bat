@echo off
setlocal
cd /d "%~dp0"
echo === Jev Decision Lab - mock structure demo ===
echo.
python decision_lab.py --backend mock --scenario agent-gate "git status"
echo.
python decision_lab.py --backend mock --scenario agent-gate "rm -rf project"
echo.
python decision_lab.py --backend mock --scenario ticket "결제가 두 번 됐고 서비스가 500 오류입니다"
echo.
echo NOTE: These are rule mocks, not actual Jev decisions.
pause
