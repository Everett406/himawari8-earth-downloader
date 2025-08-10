#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Himawari8 智能调度器
一个具备精确时间控制、智能重试机制和实时状态反馈的卫星图像定时下载系统

作者: AI Assistant
版本: 1.0.0
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import signal

class Himawari8Scheduler:
    """Himawari8卫星图像智能调度器"""
    
    def __init__(self):
        self.config_file = 'scheduler_config.json'
        self.config = self.load_config()
        self.is_running = False
        self.current_status = "STOPPED"
        self.next_download_time = None
        self.download_thread = None
        self.status_lock = threading.Lock()
        self.stop_event = threading.Event()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "output_dir": "./downloads",
            "scale": 4,
            "auto_create_dirs": True,
            "max_retries": 2,
            "first_timeout": 300,  # 5分钟
            "retry_timeout": 210,  # 3分30秒
            "log_level": "INFO"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置
                    default_config.update(loaded_config)
            return default_config
        except Exception as e:
            print(f"警告: 加载配置文件失败，使用默认配置: {e}")
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"错误: 保存配置文件失败: {e}")
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        print("\n\n收到停止信号，正在优雅关闭...")
        self.stop_scheduler()
        sys.exit(0)
    
    def get_next_download_time(self):
        """计算下一次下载时间（分钟个位为0时）"""
        now = datetime.now()
        next_min = ((now.minute // 10) + 1) * 10
        next_time = now.replace(minute=next_min % 60, second=0, microsecond=0)
        if next_min >= 60:
            next_time += timedelta(hours=1)
        return next_time
    
    def format_filename(self, download_time):
        """格式化文件名"""
        return download_time.strftime("%Y-%m-%d-%H-%M.png")
    
    def create_output_directory(self, download_time):
        """创建输出目录"""
        output_dir = self.config["output_dir"]
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            return output_dir
        except Exception as e:
            print(f"错误: 创建目录失败 {output_dir}: {e}")
            return "./downloads"
    
    def log_message(self, level, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # 保存到日志文件
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d.log"))
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"日志写入失败: {e}")
    
    def download_image(self, download_time, output_dir, filename):
        """执行图像下载"""
        try:
            filepath = os.path.join(output_dir, filename)
            scale = self.config["scale"]
            
            # 调用现有的下载器
            cmd = [
                sys.executable,
                "himawari8downloader.py",
                filename,
                str(scale),
                output_dir
            ]
            
            self.log_message("INFO", f"开始下载: {filename} (分辨率: {scale}x)")
            self.log_message("INFO", f"输出目录: {output_dir}")
            
            # 设置超时
            timeout = self.config["first_timeout"]
            result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("SUCCESS", f"下载完成: {filepath}")
                return True
            else:
                self.log_message("ERROR", f"下载失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("WARNING", f"下载超时 ({timeout}秒)，准备重试...")
            return False
        except Exception as e:
            self.log_message("ERROR", f"下载异常: {e}")
            return False
    
    def retry_download(self, download_time, output_dir, filename):
        """重试下载"""
        try:
            self.log_message("INFO", f"开始重试下载 (倒计时3分30秒)...")
            
            # 3分30秒倒计时显示
            for remaining in range(210, 0, -1):
                if self.stop_event.is_set():
                    return False
                
                mins, secs = divmod(remaining, 60)
                print(f"\r重试倒计时: {mins:02d}:{secs:02d}", end="", flush=True)
                time.sleep(1)
            
            print("\r开始重试下载...")
            
            # 执行重试
            cmd = [
                sys.executable,
                "himawari8downloader.py",
                filename,
                str(self.config["scale"]),
                output_dir
            ]
            
            timeout = self.config["retry_timeout"]
            result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("SUCCESS", f"重试下载完成: {filename}")
                return True
            else:
                self.log_message("ERROR", f"重试下载失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("ERROR", f"重试下载超时 ({timeout}秒)")
            return False
        except Exception as e:
            self.log_message("ERROR", f"重试下载异常: {e}")
            return False
    
    def download_worker(self):
        """下载工作线程"""
        while not self.stop_event.is_set():
            try:
                now = datetime.now()
                
                # 检查是否到达下载时间
                if now.minute % 10 == 0 and now.second < 30:
                    download_time = now
                    
                    with self.status_lock:
                        self.current_status = "DOWNLOADING"
                    
                    # 创建输出目录
                    output_dir = self.create_output_directory(download_time)
                    filename = self.format_filename(download_time)
                    
                    # 第一次下载
                    success = self.download_image(download_time, output_dir, filename)
                    
                    # 如果需要重试
                    if not success and not self.stop_event.is_set():
                        with self.status_lock:
                            self.current_status = "RETRYING"
                        success = self.retry_download(download_time, output_dir, filename)
                    
                    if not success:
                        with self.status_lock:
                            self.current_status = "FAILED"
                        self.log_message("ERROR", f"下载失败，等待下一个周期...")
                    else:
                        with self.status_lock:
                            self.current_status = "IDLE"
                    
                    # 等待下一个周期
                    time.sleep(60)  # 避免在同一分钟内重复触发
                else:
                    time.sleep(1)  # 每秒检查一次
                    
            except Exception as e:
                self.log_message("ERROR", f"调度器异常: {e}")
                time.sleep(10)
    
    def countdown_display(self):
        """倒计时显示线程"""
        while not self.stop_event.is_set():
            try:
                now = datetime.now()
                next_time = self.get_next_download_time()
                remaining = next_time - now
                
                if remaining.total_seconds() > 0:
                    hours, remainder = divmod(remaining.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    print(f"\r距离下次下载: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}", end="", flush=True)
                
                time.sleep(1)  # 每秒更新
                
            except Exception as e:
                time.sleep(1)
    
    def start_scheduler(self):
        """启动调度器"""
        if self.is_running:
            print("调度器已在运行中")
            return
        
        self.stop_event.clear()
        self.is_running = True
        
        self.log_message("INFO", "启动Himawari8调度器...")
        self.log_message("INFO", f"输出目录: {self.config['output_dir']}")
        self.log_message("INFO", f"分辨率倍数: {self.config['scale']}x")
        
        # 启动工作线程
        self.download_thread = threading.Thread(target=self.download_worker, daemon=True)
        self.countdown_thread = threading.Thread(target=self.countdown_display, daemon=True)
        
        self.download_thread.start()
        self.countdown_thread.start()
        
        self.current_status = "IDLE"
        self.log_message("SUCCESS", "调度器启动成功")
    
    def stop_scheduler(self):
        """停止调度器"""
        if not self.is_running:
            print("调度器未运行")
            return
        
        self.log_message("INFO", "正在停止调度器...")
        self.stop_event.set()
        self.is_running = False
        self.current_status = "STOPPED"
        
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(timeout=5)
        
        self.log_message("SUCCESS", "调度器已停止")
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*50)
        print("    🛰️  Himawari8 智能调度器 v1.0.0")
        print("="*50)
        print("1. 启动调度器")
        print("2. 停止调度器")
        print("3. 配置设置")
        print("4. 查看状态")
        print("5. 查看日志")
        print("6. 退出程序")
        print("-"*50)
    
    def show_config_menu(self):
        """显示配置菜单"""
        print("\n" + "="*30)
        print("    配置设置")
        print("="*30)
        print(f"当前输出目录: {self.config['output_dir']}")
        print(f"当前分辨率: {self.config['scale']}x")
        print("-"*30)
        print("1. 修改输出目录")
        print("2. 修改分辨率")
        print("3. 返回主菜单")
    
    def update_output_dir(self):
        """更新输出目录"""
        new_dir = input("请输入新的输出目录 (留空保持当前): ").strip()
        if new_dir:
            # 处理相对路径
            if not os.path.isabs(new_dir):
                new_dir = os.path.abspath(new_dir)
            
            if os.path.exists(new_dir) or input(f"目录不存在，是否创建? (y/n): ").lower() == 'y':
                self.config["output_dir"] = new_dir
                self.save_config()
                print(f"输出目录已更新: {new_dir}")
            else:
                print("取消修改")
    
    def update_scale(self):
        """更新分辨率"""
        print("\n可用分辨率:")
        scales = [1, 2, 4, 8, 16, 20]
        for i, scale in enumerate(scales, 1):
            print(f"{i}. {scale}x ({550*scale}x{550*scale})")
        
        try:
            choice = int(input("请选择分辨率 (1-6): "))
            if 1 <= choice <= 6:
                self.config["scale"] = scales[choice-1]
                self.save_config()
                print(f"分辨率已更新: {self.config['scale']}x")
            else:
                print("无效选择")
        except ValueError:
            print("请输入数字")
    
    def show_status(self):
        """显示当前状态"""
        print("\n" + "="*30)
        print("    系统状态")
        print("="*30)
        print(f"运行状态: {self.current_status}")
        print(f"输出目录: {self.config['output_dir']}")
        print(f"分辨率: {self.config['scale']}x")
        
        if self.is_running:
            next_time = self.get_next_download_time()
            print(f"下次下载时间: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("调度器未运行")
    
    def show_logs(self):
        """显示最近日志"""
        log_dir = "logs"
        today_log = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d.log"))
        
        if os.path.exists(today_log):
            try:
                with open(today_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_logs = lines[-20:]  # 最近20条
                    
                print("\n" + "="*50)
                print("    最近日志")
                print("="*50)
                for line in recent_logs:
                    print(line.strip())
            except Exception as e:
                print(f"读取日志失败: {e}")
        else:
            print("今日暂无日志")
    
    def run(self):
        """运行主程序"""
        print("🛰️  Himawari8 智能调度器启动中...")
        
        while True:
            try:
                self.show_menu()
                choice = input("\n请选择操作 (1-6): ").strip()
                
                if choice == "1":
                    self.start_scheduler()
                    input("\n按Enter键返回菜单...")
                elif choice == "2":
                    self.stop_scheduler()
                    input("\n按Enter键返回菜单...")
                elif choice == "3":
                    while True:
                        self.show_config_menu()
                        config_choice = input("\n请选择 (1-3): ").strip()
                        
                        if config_choice == "1":
                            self.update_output_dir()
                        elif config_choice == "2":
                            self.update_scale()
                        elif config_choice == "3":
                            break
                        else:
                            print("无效选择")
                elif choice == "4":
                    self.show_status()
                    input("\n按Enter键返回菜单...")
                elif choice == "5":
                    self.show_logs()
                    input("\n按Enter键返回菜单...")
                elif choice == "6":
                    if self.is_running:
                        self.stop_scheduler()
                    print("感谢使用，再见！")
                    break
                else:
                    print("无效选择，请输入1-6")
                    
            except KeyboardInterrupt:
                print("\n\n收到退出信号...")
                if self.is_running:
                    self.stop_scheduler()
                break
            except Exception as e:
                print(f"程序异常: {e}")
                input("\n按Enter键继续...")


def main():
    """主函数"""
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 创建并运行调度器
    scheduler = Himawari8Scheduler()
    scheduler.run()


if __name__ == "__main__":
    main()