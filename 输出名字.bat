@echo off
setlocal enabledelayedexpansion

rem 设置要搜索的文件类型和目录路径
set "fileType=*.mp3"
set "directory=tmp_ignore_sync"

rem 清空或创建 output.txt 文件
type nul > output.txt

rem 遍历指定目录下的所有符合条件的文件并将文件名写入 output.txt
for %%i in ("%directory%\%fileType%") do (
    echo %%~nxi >> output.txt
)

echo "tmp_ignore_sync 目录中的 MP3 文件名已经写入到 output.txt 中"
