import pystray
import PIL.Image
import tkinter as tk
import os
import threading

class SystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.setup_icon()
    
    def setup_icon(self):
        # 创建一个简单的图标图像
        image = PIL.Image.new('RGB', (64, 64), color = (0, 120, 212))
        
        # 创建系统托盘图标
        self.icon = pystray.Icon(
            "keyboard_clicker",
            image,
            "键盘连点器",
            self.create_menu()
        )
    
    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("显示", self.show_window),
            pystray.MenuItem("退出", self.quit_app)
        )
    
    def show_window(self, icon, item):
        self.app.root.deiconify()  # 显示窗口
        self.app.root.lift()       # 将窗口提升到顶层
        self.app.root.focus_force() # 强制获取焦点
    
    def quit_app(self, icon, item):
        icon.stop()  # 停止图标
        self.app.on_closing()  # 调用应用的关闭方法
    
    def run(self):
        # 在单独的线程中运行图标
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def stop(self):
        if self.icon:
            self.icon.stop()