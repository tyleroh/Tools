#!/bin/bash
# 弹出 Finder 选择目录，调用 nfo_cleaner.py 脚本处理

cd "$(dirname "$0")"

# 使用 AppleScript 弹出 Finder 选择器
CHOOSEN_PATH=$(osascript <<EOT
tell application "Finder"
    activate
    set theFolder to choose folder with prompt "请选择要清理的目录："
    return POSIX path of theFolder
end tell
EOT
)

# 用户取消选择时退出
if [ -z "$CHOOSEN_PATH" ]; then
    echo "❌ 未选择目录，退出。"
    exit 1
fi

echo "📂 选择的目录：$CHOOSEN_PATH"
echo

# 调用 Python 脚本处理
python3 nfo_cleaner.py "$CHOOSEN_PATH"

echo
echo "✅ 脚本运行完毕。按任意键退出……"
read -n 1
