# Himawari8 视频合成器使用指南

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install opencv-python pillow numpy tqdm
```

### 2. 基本使用
```bash
# 启动交互式界面
python video_composer.py

# 指定输入目录
python video_composer.py --input ./downloads

# 指定输出目录
python video_composer.py --output ./my_videos
```

## 📋 功能详解

### 图片扫描
- **默认目录**：`./downloads/`
- **文件格式**：`YYYY-MM-DD-HH-MM.png`
- **时间解析**：从文件名提取拍摄时间
- **自动排序**：按时间顺序排列

### 时间范围选择
1. **全部图片**：使用所有扫描到的图片
2. **指定时间**：手动输入起止时间（格式：YYYY-MM-DD-HH-MM）
3. **最近时间**：选择最近N小时的图片

### 合成模式

#### 模式A：单帧时长模式
- **概念**：每张图片显示固定时长
- **参数**：单帧时长（秒）
- **示例**：100张图片 × 2秒/张 = 200秒视频

#### 模式B：帧率模式
- **概念**：设置视频每秒帧数
- **参数**：FPS（帧/秒）
- **示例**：100张图片 ÷ 30 FPS = 3.33秒视频

## 🎯 使用示例

### 示例1：基本合成
```bash
python video_composer.py
```
按提示操作即可。

### 示例2：命令行参数
```bash
# 使用帧率模式，30 FPS，高质量码率
python video_composer.py --mode fps --fps 30 --bitrate 20000 --codec h264

# 使用单帧时长模式，每张3秒，标准码率
python video_composer.py --mode duration --duration 3.0 --bitrate 5000 --codec h264

# 指定完整参数
python video_composer.py --input ./downloads --output ./videos --mode fps --fps 24 --quality 90 --bitrate 15000 --codec h265

# 高质量设置
python video_composer.py --mode fps --fps 60 --bitrate 50000 --codec h264

# 兼容性设置
python video_composer.py --codec mp4v --bitrate 8000
```

### 示例3：时间范围选择
```bash
# 先启动程序，在交互界面选择：
# 1. 选择"指定起止时间"
# 2. 输入起始时间：2024-12-19-14-00
# 3. 输入结束时间：2024-12-19-16-00
```

## 📁 文件结构

### 输入目录结构
```
downloads/
├── 2024-12-19-14-00.png
├── 2024-12-19-14-10.png
├── 2024-12-19-14-20.png
└── ...
```

### 输出文件命名
```
videos/
├── himawari8_20241219_1400_20241219_1600.mp4
└── ...
```

## ⚙️ 配置文件

### video_config.json
```json
{
  "input_dir": "./downloads",
  "output_dir": "./videos",
  "default_mode": "duration",
  "default_duration": 2.0,
  "default_fps": 30,
  "default_quality": 95
}
```

## 🔧 参数说明

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| `--input` | 输入图片目录 | `./downloads` | 任意路径 |
| `--output` | 输出视频目录 | `./videos` | 任意路径 |
| `--mode` | 合成模式 | `duration` | `duration`/`fps` |
| `--duration` | 单帧时长(秒) | `2.0` | 0.1-10.0 |
| `--fps` | 每秒帧数 | `30` | 1-60 |
| `--quality` | 视频质量 | `95` | 1-100 |
| `--bitrate` | 视频码率 | `10000` | 1000-50000 |
| `--codec` | 编码格式 | h264 | h264/h265/mp4v/mjpeg |

## 🌐 API接口（预留）

### 获取图片列表
```python
import requests

response = requests.get('http://localhost:8001/api/images')
print(response.json())
```

### 启动合成任务
```python
response = requests.post('http://localhost:8001/api/compose', json={
    "start_time": "2024-12-19-14-00",
    "end_time": "2024-12-19-16-00",
    "mode": "fps",
    "fps": 30
})
```

## 🎬 使用技巧

### 制作流畅视频
- **慢动作效果**：使用单帧时长模式，设置较长时长（如5秒/张）
- **快进效果**：使用帧率模式，设置较高FPS（如60 FPS）
- **标准视频**：使用30 FPS帧率模式

### 时间选择技巧
- **全天视频**：选择00:00到23:50的图片
- **特定时段**：选择日出/日落时段的图片
- **天气对比**：选择不同天气状况的时段

### 性能优化
- **大量图片**：建议降低质量参数或提高FPS
- **高清视频**：保持高质量设置，但注意文件大小
- **长时段**：分批次处理，避免单次处理过多图片

## ❗ 常见问题

### Q: 找不到图片？
A: 确保图片格式正确（YYYY-MM-DD-HH-MM.png）且位于指定目录

### Q: 视频文件很大？
A: 尝试降低`--quality`参数或提高`--fps`值

### Q: 合成速度很慢？
A: 图片数量多时，降低质量或使用更高FPS

### Q: 如何查看进度？
A: 程序会自动显示进度条，显示处理进度

## 📊 效果示例

### 示例1：2小时时段，单帧2秒
- 12张图片 × 2秒/张 = 24秒视频
- 文件大小：约15-20MB

### 示例2：1天时段，30 FPS
- 144张图片 ÷ 30 FPS = 4.8秒视频
- 文件大小：约8-12MB