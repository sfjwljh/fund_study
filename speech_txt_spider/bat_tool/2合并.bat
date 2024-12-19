@echo off
setlocal enabledelayedexpansion

REM 创建 total 目录
mkdir total 2>nul

REM 将非 total 目录里的其他目录里的所有文件移动到 total 目录下
for /d %%d in (*) do (
    if /i not "%%~nxd"=="total" (
        echo Moving files from %%d to total\ ...
        move "%%d\*" total\
    )
)

@echo off
for /f "delims=" %%d in ('dir /ad /b') do (
    rd "%%d" 2>nul
)


pause