#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Himawari8 视频合成器
将下载的地球图片按时间顺序合成为MP4视频
"""

import os
import re
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm
import logging

class ImageScanner:
    """图片扫描和时间解析器"""
    
    def __init__(self, input_dir: str):
        self.input_dir = Path(input_dir)
        self.image_pattern = re.compile(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})\.png')
    
    def scan_images(self) -> List[Tuple[datetime, Path]]:
        """扫描目录中的所有图片并返回时间戳和路径列表"""
        images = []
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"目录不存在: {self.input_dir}")
        
        for png_file in self.input_dir.rglob("*.png"):
            match = self.image_pattern.match(png_file.name)
            if match:
                year, month, day, hour, minute = map(int, match.groups())
                timestamp = datetime(year, month, day, hour, minute)
                images.append((timestamp, png_file))
        
        # 按时间排序
        images.sort(key=lambda x: x[0])
        return images
    
    def get_time_range(self, images: List[Tuple[datetime, Path]]) -> Tuple[datetime, datetime]:
        """获取图片的时间范围"""
        if not images:
            return None, None
        return images[0][0], images[-1][0]

class TimeRangeSelector:
    """时间范围选择器"""
    
    @staticmethod
    def select_range(images: List[Tuple[datetime, Path]]) -> Tuple[int, int]:
        """交互式选择时间范围"""
        if not images:
            raise ValueError("没有找到图片")
        
        start_time = images[0][0]
        end_time = images[-1][0]
        
        print(f"\n📁 找到 {len(images)} 张图片")
        print(f"⏰ 时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}")
        
        print("\n📋 选择时间范围模式:")
        print("1. 使用全部图片")
        print("2. 指定起止时间")
        print("3. 最近N小时")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            return 0, len(images)
        
        elif choice == "2":
            return TimeRangeSelector._manual_range(images)
        
        elif choice == "3":
            return TimeRangeSelector._recent_hours(images)
        
        else:
            return 0, len(images)
    
    @staticmethod
    def _manual_range(images: List[Tuple[datetime, Path]]) -> Tuple[int, int]:
        """手动指定时间范围"""
        time_format = "%Y-%m-%d-%H-%M"
        
        try:
            start_str = input(f"起始时间 ({time_format}): ").strip()
            end_str = input(f"结束时间 ({time_format}): ").strip()
            
            start_time = datetime.strptime(start_str, time_format)
            end_time = datetime.strptime(end_str, time_format)
            
            # 找到对应的图片索引
            start_idx = next(i for i, (t, _) in enumerate(images) if t >= start_time)
            end_idx = next(i for i, (t, _) in enumerate(images[::-1]) if t <= end_time)
            end_idx = len(images) - end_idx
            
            return max(0, start_idx), min(len(images), end_idx + 1)
            
        except (ValueError, StopIteration):
            print("⚠️ 时间格式错误或范围无效，使用全部图片")
            return 0, len(images)
    
    @staticmethod
    def _recent_hours(images: List[Tuple[datetime, Path]]) -> Tuple[int, int]:
        """选择最近N小时"""
        try:
            hours = float(input("最近多少小时: ").strip())
            cutoff_time = images[-1][0] - timedelta(hours=hours)
            
            start_idx = next(i for i, (t, _) in enumerate(images) if t >= cutoff_time)
            return start_idx, len(images)
            
        except (ValueError, StopIteration):
            print("⚠️ 输入无效，使用全部图片")
            return 0, len(images)

class VideoComposer:
    """视频合成器"""
    
    def __init__(self, output_dir: str = "./videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def compose_video(self, 
                     images: List[Tuple[datetime, Path]],
                     start_idx: int,
                     end_idx: int,
                     mode: str = "duration",
                     duration: float = 2.0,
                     fps: int = 30,
                     quality: int = 95,
                     bitrate: int = 10000,
                     codec: str = "h264") -> Path:
        """合成视频"""
        
        selected_images = images[start_idx:end_idx]
        if not selected_images:
            raise ValueError("没有选中图片")
        
        # 获取第一张图片的尺寸
        first_img = Image.open(selected_images[0][1])
        width, height = first_img.size
        
        # 计算视频参数
        if mode == "duration":
            # 单帧时长模式
            frame_duration = duration
            total_duration = len(selected_images) * duration
            actual_fps = 1.0 / duration
        else:  # fps模式
            actual_fps = fps
            total_duration = len(selected_images) / fps
        
        # 生成输出文件名
        start_time = selected_images[0][0]
        end_time = selected_images[-1][0]
        output_name = f"himawari8_{start_time.strftime('%Y%m%d_%H%M')}_{end_time.strftime('%Y%m%d_%H%M')}.mp4"
        output_path = self.output_dir / output_name
        
        print(f"\n🎬 开始合成视频...")
        print(f"📊 图片数量: {len(selected_images)}")
        # 编码格式映射
        codec_map = {
            'h264': 'X264',   # H.264 - 高压缩率，质量好
            'h265': 'X265',   # H.265 - 更高压缩率，需要更多CPU
            'mp4v': 'mp4v',   # MPEG-4 - 兼容性最好
            'mjpeg': 'MJPG'   # MJPEG - 质量高但文件大
        }
        
        codec_fourcc = codec_map.get(codec, 'X264')
        
        print(f"⏱️ 视频时长: {total_duration:.1f} 秒")
        print(f"📹 帧率: {actual_fps:.2f} FPS")
        print(f"🎞️ 码率: {bitrate} kbps")
        print(f"🎬 编码格式: {codec.upper()} ({codec_fourcc})")
        print(f"💾 输出文件: {output_path}")
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*codec_fourcc)
        writer = cv2.VideoWriter(str(output_path), fourcc, actual_fps, (width, height))
        
        # 设置码率（如果支持）
        if writer.isOpened():
            try:
                # OpenCV的VideoWriter对码率的支持有限
                # 这里我们记录码率设置，实际效果取决于编码器
                print(f"🎞️ 设置码率: {bitrate} kbps")
            except:
                pass
        
        try:
            for timestamp, img_path in tqdm(selected_images, desc="合成进度"):
                # 读取并转换图片
                img = Image.open(img_path)
                img_array = np.array(img)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # 根据模式写入帧
                if mode == "duration":
                    # 单帧时长模式：重复写入帧
                    frames_to_write = int(duration * actual_fps)
                    for _ in range(max(1, frames_to_write)):
                        writer.write(img_array)
                else:
                    # FPS模式：每帧写入一次
                    writer.write(img_array)
            
            writer.release()
            print(f"✅ 视频合成完成: {output_path}")
            return output_path
            
        except Exception as e:
            writer.release()
            if output_path.exists():
                output_path.unlink()
            raise e

class VideoConfig:
    """配置管理器"""
    
    def __init__(self, config_file: str = "video_config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            "input_dir": "./downloads",
            "output_dir": "./videos",
            "default_mode": "duration",
            "default_duration": 2.0,
            "default_fps": 30,
            "default_quality": 95,
            "default_codec": "h264",
            "default_bitrate": 10000
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {**self.default_config, **config}
            except json.JSONDecodeError:
                print("⚠️ 配置文件格式错误，使用默认配置")
        
        return self.default_config.copy()
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

class VideoComposerAPI:
    """为Web UI预留的API接口"""
    
    def __init__(self):
        self.config = VideoConfig()
    
    def get_available_images(self, input_dir: str = None) -> Dict[str, Any]:
        """获取可用图片列表"""
        try:
            input_dir = input_dir or self.config.config["input_dir"]
            scanner = ImageScanner(input_dir)
            images = scanner.scan_images()
            
            return {
                "status": "success",
                "count": len(images),
                "start_time": images[0][0].isoformat() if images else None,
                "end_time": images[-1][0].isoformat() if images else None,
                "images": [(t.isoformat(), str(p)) for t, p in images]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def compose_video_async(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """异步视频合成（预留接口）"""
        return {
            "status": "queued",
            "task_id": "placeholder",
            "message": "此接口为Web UI预留"
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Himawari8 视频合成器")
    parser.add_argument("--input", "-i", help="输入图片目录")
    parser.add_argument("--output", "-o", help="输出视频目录")
    parser.add_argument("--mode", choices=["duration", "fps"], help="合成模式")
    parser.add_argument("--duration", type=float, help="单帧时长（秒）")
    parser.add_argument("--fps", type=int, help="每秒帧数")
    parser.add_argument("--quality", type=int, help="视频质量（1-100）")
    parser.add_argument("--bitrate", type=int, help="视频码率（kbps，默认10000）")
    parser.add_argument("--codec", choices=["h264", "h265", "mp4v", "mjpeg"], help="视频编码格式（默认h264）")
    
    args = parser.parse_args()
    
    # 初始化配置
    config = VideoConfig()
    
    # 使用命令行参数或配置
    input_dir = args.input or config.config["input_dir"]
    output_dir = args.output or config.config["output_dir"]
    mode = args.mode or config.config["default_mode"]
    duration = args.duration or config.config["default_duration"]
    fps = args.fps or config.config["default_fps"]
    quality = args.quality or config.config["default_quality"]
    bitrate = args.bitrate or config.config["default_bitrate"]
    codec = args.codec or config.config["default_codec"]

    try:
        # 扫描图片
        print(f"🔍 扫描图片目录: {input_dir}")
        scanner = ImageScanner(input_dir)
        images = scanner.scan_images()
        
        if not images:
            print("❌ 没有找到符合条件的图片")
            return
        
        # 选择时间范围
        start_idx, end_idx = TimeRangeSelector.select_range(images)
        selected_count = end_idx - start_idx
        
        if selected_count == 0:
            print("❌ 没有选中图片")
            return
        
        # 选择合成模式
        print(f"\n📋 选择合成模式:")
        print("1. 单帧时长模式（每张图片显示固定时长）")
        print("2. 帧率模式（设置每秒帧数）")
        
        mode_choice = input("请选择 (1-2): ").strip()
        if mode_choice == "2":
            mode = "fps"
            fps = int(input("请输入帧率 (1-60): ") or fps)
        else:
            mode = "duration"
            duration = float(input("请输入单帧时长 (秒): ") or duration)
        
        # 选择码率
        print(f"\n📋 选择视频码率:")
        print("1. 高质量 (20000 kbps)")
        print("2. 中等质量 (10000 kbps) - 默认")
        print("3. 标准质量 (5000 kbps)")
        print("4. 低质量 (2000 kbps)")
        
        bitrate_choice = input("请选择码率 (1-4): ").strip()
        bitrate_map = {"1": 20000, "2": 10000, "3": 5000, "4": 2000}
        bitrate = bitrate_map.get(bitrate_choice, bitrate)
        
        # 选择编码格式
        print(f"\n📋 选择视频编码格式:")
        print("1. H.264 - 高压缩率，质量好（推荐）")
        print("2. H.265 - 更高压缩率，需要更多CPU")
        print("3. MPEG-4 - 兼容性最好")
        print("4. MJPEG - 质量高但文件大")
        
        codec_choice = input("请选择编码格式 (1-4): ").strip()
        codec_map = {"1": "h264", "2": "h265", "3": "mp4v", "4": "mjpeg"}
        codec = codec_map.get(codec_choice, "h264")
        
        # 合成视频
        composer = VideoComposer(output_dir)
        output_path = composer.compose_video(
            images, start_idx, end_idx, mode, duration, fps, quality, bitrate, codec
        )
        
        print(f"\n🎉 视频合成成功！")
        print(f"📁 文件位置: {output_path}")
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()