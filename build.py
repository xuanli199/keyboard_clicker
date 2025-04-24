import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 设置PyInstaller参数
PyInstaller.__main__.run([
    'main.py',                          # 主脚本
    '--name=键盘连点器',                 # 应用名称
    '--onefile',                       # 打包成单个文件
    '--windowed',                      # 使用窗口模式（不显示控制台）
    '--add-data=config.json;.',        # 添加配置文件（如果存在）
    '--hidden-import=pynput.keyboard._win32',  # 隐藏导入
    '--hidden-import=pynput.mouse._win32',
    '--clean',                         # 清理临时文件
])

print("打包完成！可执行文件位于 dist 目录中。")