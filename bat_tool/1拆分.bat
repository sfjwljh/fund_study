@echo off
setlocal enabledelayedexpansion

rem 创建10个目录
for /l %%i in (1,1,10) do (
    mkdir "part%%i"
)

rem 移动MP3文件到10个目录中
set count=1
for %%F in (*.mp3) do (
    move "%%F" "part!count!"
    set /a count=!count!+1
    if !count! gtr 10 set count=1
)

echo 所有MP3文件已经移动到part1到part10目录中。
pause