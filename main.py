import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import keyboard
import threading
import time
from pynput.keyboard import Controller
from system_tray import SystemTray

class KeyboardClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("键盘连点器")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # 控制变量
        self.is_running = False
        self.keyboard_controller = Controller()
        self.click_thread = None
        self.stop_event = threading.Event()
        
        # 配置文件路径
        # 在打包环境中，__file__可能指向临时目录，需要使用不同的方法获取应用程序路径
        try:
            # 尝试获取打包后的可执行文件路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的环境
                application_path = os.path.dirname(sys.executable)
            else:
                # 如果是开发环境
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            self.config_file = os.path.join(application_path, "config.json")
            print(f"配置文件路径: {self.config_file}")
        except Exception as e:
            print(f"设置配置文件路径时出错: {e}")
            # 使用用户文档目录作为备选
            self.config_file = os.path.join(os.path.expanduser("~"), "Documents", "键盘连点器", "config.json")
        
        # 默认配置
        self.config = {
            "key_sequence": [],
            "hotkey": "f8",
            "interval": 0.1
        }
        
        # 加载配置
        self.load_config()
        
        # 创建UI
        self.create_ui()
        
        # 注册全局热键
        self.register_hotkey()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # 创建系统托盘
        self.system_tray = SystemTray(self)
        self.system_tray.run()
        
    def create_ui(self):
        # 标题标签
        title_label = tk.Label(self.root, text="键盘连点器", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 按键序列框架
        key_frame = tk.LabelFrame(self.root, text="按键序列设置", padx=10, pady=10)
        key_frame.pack(fill="both", expand="yes", padx=10, pady=10)
        
        # 按键输入
        self.key_entry = tk.Entry(key_frame)
        self.key_entry.pack(fill="x", padx=5, pady=5)
        self.key_entry.insert(0, "+".join(self.config["key_sequence"]) if self.config["key_sequence"] else "")
        
        # 说明标签
        tk.Label(key_frame, text="输入格式: 单个按键或用+分隔的按键序列 (例如: a 或 ctrl+c)").pack(pady=5)
        
        # 间隔设置
        interval_frame = tk.Frame(key_frame)
        interval_frame.pack(fill="x", pady=5)
        tk.Label(interval_frame, text="点击间隔 (秒):").pack(side="left")
        self.interval_entry = tk.Entry(interval_frame, width=10)
        self.interval_entry.pack(side="left", padx=5)
        self.interval_entry.insert(0, str(self.config["interval"]))
        
        # 热键设置框架
        hotkey_frame = tk.LabelFrame(self.root, text="热键设置", padx=10, pady=10)
        hotkey_frame.pack(fill="both", expand="yes", padx=10, pady=10)
        
        # 热键输入
        self.hotkey_entry = tk.Entry(hotkey_frame)
        self.hotkey_entry.pack(fill="x", padx=5, pady=5)
        self.hotkey_entry.insert(0, self.config["hotkey"])
        
        # 说明标签
        tk.Label(hotkey_frame, text="输入用于开启/关闭连点器的热键 (例如: f8)").pack(pady=5)
        
        # 状态框架
        status_frame = tk.LabelFrame(self.root, text="状态", padx=10, pady=10)
        status_frame.pack(fill="both", expand="yes", padx=10, pady=10)
        
        # 状态标签
        self.status_label = tk.Label(status_frame, text="已停止", fg="red")
        self.status_label.pack(pady=5)
        
        # 保存按钮
        save_button = tk.Button(self.root, text="保存设置", command=self.save_settings)
        save_button.pack(pady=10)
        
        # 最小化到托盘按钮
        minimize_button = tk.Button(self.root, text="最小化到后台", command=self.minimize_to_tray)
        minimize_button.pack(pady=5)
    
    def register_hotkey(self):
        # 注销之前的热键
        try:
            keyboard.unhook_all()
        except:
            pass
        
        # 注册新热键
        keyboard.add_hotkey(self.config["hotkey"], self.toggle_clicking)
    
    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def start_clicking(self):
        if not self.config["key_sequence"]:
            return
            
        self.is_running = True
        self.status_label.config(text="正在运行", fg="green")
        
        # 停止之前的线程
        if self.click_thread and self.click_thread.is_alive():
            self.stop_event.set()
            self.click_thread.join()
        
        # 重置停止事件
        self.stop_event.clear()
        
        # 创建新线程
        self.click_thread = threading.Thread(target=self.clicking_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
    
    def stop_clicking(self):
        self.is_running = False
        self.status_label.config(text="已停止", fg="red")
        
        if self.click_thread and self.click_thread.is_alive():
            self.stop_event.set()
    
    def clicking_loop(self):
        while not self.stop_event.is_set():
            for key in self.config["key_sequence"]:
                if self.stop_event.is_set():
                    break
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
                time.sleep(0.05)  # 短暂延迟以确保按键被正确识别
            
            # 等待指定的间隔时间
            time.sleep(float(self.config["interval"]))
    
    def save_settings(self):
        # 获取用户输入
        key_input = self.key_entry.get().strip()
        hotkey = self.hotkey_entry.get().strip()
        interval = self.interval_entry.get().strip()
        
        # 验证输入
        if not key_input or not hotkey or not interval:
            tk.messagebox.showwarning("输入错误", "请确保所有字段都已填写")
            return
        
        try:
            interval = float(interval)
            if interval <= 0:
                raise ValueError("间隔必须大于0")
        except ValueError:
            tk.messagebox.showwarning("输入错误", "间隔必须是大于0的数字")
            return
        
        # 更新配置
        self.config["key_sequence"] = key_input.split("+")
        self.config["hotkey"] = hotkey
        self.config["interval"] = interval
        
        # 保存配置
        save_result = self.save_config()
        
        # 显示保存结果
        if save_result:
            tk.messagebox.showinfo("保存成功", "设置已成功保存")
        else:
            tk.messagebox.showerror("保存失败", "无法保存设置，请查看控制台输出了解详情")
        
        # 重新注册热键
        self.register_hotkey()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def save_config(self):
        try:
            # 确保配置文件目录存在
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                try:
                    os.makedirs(config_dir)
                    print(f"创建目录成功: {config_dir}")
                except Exception as e:
                    print(f"创建目录失败: {e}")
                    # 如果无法创建原目录，尝试使用用户文档目录
                    user_doc_dir = os.path.join(os.path.expanduser("~"), "Documents", "键盘连点器")
                    if not os.path.exists(user_doc_dir):
                        os.makedirs(user_doc_dir)
                    self.config_file = os.path.join(user_doc_dir, "config.json")
                    print(f"改用备选配置文件路径: {self.config_file}")
                
            # 尝试写入配置文件
            try:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                print(f"写入配置文件成功")
            except Exception as write_error:
                print(f"写入配置文件失败: {write_error}")
                # 如果写入失败，尝试使用用户文档目录
                user_doc_dir = os.path.join(os.path.expanduser("~"), "Documents", "键盘连点器")
                if not os.path.exists(user_doc_dir):
                    os.makedirs(user_doc_dir)
                backup_config_file = os.path.join(user_doc_dir, "config.json")
                with open(backup_config_file, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                self.config_file = backup_config_file
                print(f"已保存到备选位置: {backup_config_file}")
                
            # 验证文件是否成功写入
            if os.path.exists(self.config_file):
                print(f"配置已成功保存到: {self.config_file}")
                return True
            else:
                print(f"配置文件未成功创建: {self.config_file}")
                return False
        except PermissionError as pe:
            print(f"保存配置失败 - 权限错误: {pe}")
            print(f"请确保您有权限写入此位置: {self.config_file}")
            # 尝试使用用户文档目录作为备选
            try:
                user_doc_dir = os.path.join(os.path.expanduser("~"), "Documents", "键盘连点器")
                if not os.path.exists(user_doc_dir):
                    os.makedirs(user_doc_dir)
                backup_config_file = os.path.join(user_doc_dir, "config.json")
                with open(backup_config_file, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                self.config_file = backup_config_file
                print(f"已保存到备选位置: {backup_config_file}")
                return True
            except Exception as backup_error:
                print(f"备选保存也失败: {backup_error}")
                return False
        except Exception as e:
            print(f"保存配置失败: {e}")
            # 尝试使用用户文档目录作为备选
            try:
                user_doc_dir = os.path.join(os.path.expanduser("~"), "Documents", "键盘连点器")
                if not os.path.exists(user_doc_dir):
                    os.makedirs(user_doc_dir)
                backup_config_file = os.path.join(user_doc_dir, "config.json")
                with open(backup_config_file, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                self.config_file = backup_config_file
                print(f"已保存到备选位置: {backup_config_file}")
                return True
            except Exception as backup_error:
                print(f"备选保存也失败: {backup_error}")
                return False
    
    def minimize_to_tray(self):
        self.root.withdraw()  # 隐藏窗口
    
    def on_closing(self):
        # 停止点击线程
        self.stop_clicking()
        
        # 保存配置
        self.save_config()
        
        # 停止系统托盘
        if hasattr(self, 'system_tray'):
            self.system_tray.stop()
        
        # 关闭窗口
        self.root.destroy()

if __name__ == "__main__":
    app = KeyboardClicker()
    app.root.mainloop()