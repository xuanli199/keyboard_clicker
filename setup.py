import sys
from cx_Freeze import setup, Executable

# 依赖项
build_exe_options = {
    "packages": ["os", "tkinter", "json", "keyboard", "threading", "time", "pynput", "pystray", "PIL"],
    "include_files": [],
    "excludes": []
}

# 基本信息
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 使用Windows GUI应用

# 可执行文件设置
executables = [
    Executable(
        "main.py",
        base=base,
        target_name="键盘连点器.exe",
        icon=None,  # 可以添加图标文件
        shortcut_name="键盘连点器",
        shortcut_dir="DesktopFolder"
    )
]

# 设置
setup(
    name="键盘连点器",
    version="1.0.0",
    description="键盘连点器 - 自动模拟键盘按键",
    options={"build_exe": build_exe_options},
    executables=executables
)