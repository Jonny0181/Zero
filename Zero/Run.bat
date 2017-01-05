@ECHO off

CHCP 65001 > NUL
CD /d "%~dp0"

IF EXIST %SYSTEMROOT%\py.exe (
    CMD /k py.exe -3.5 main.py
    EXIT
)

PAUSE