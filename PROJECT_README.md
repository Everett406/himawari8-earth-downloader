# 🛰️ Himawari8 地球观测系统

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenCV](https://img.shields.io/badge/opencv-4.0+-green.svg)](https://opencv.org/)

一个完整的Himawari8地球卫星图像自动下载与视频合成系统，支持智能调度和延时视频制作。

## ✨ 功能特性

### 🎯 核心功能
- **🔄 智能调度下载**：每10分钟自动下载最新地球图片
- **🎬 视频合成**：将图片合成为流畅的延时视频
- **⏰ 时间范围**：支持精确的时间范围选择
- **📊 多种模式**：单帧时长和帧率模式可选
- **🌐 Web接口**：预留API接口供前端集成

### 📱 用户界面
- **📋 菜单系统**：交互式命令行界面
- **📈 实时状态**：下载进度和倒计时显示
- **⚙️ 配置管理**：JSON配置文件支持
- **🚀 一键启动**：Windows批处理脚本

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动下载调度器
```bash
# Windows一键启动
双击 start_scheduler.bat

# 或命令行
python himawari8_scheduler.py
```

### 3. 制作延时视频
```bash
# Windows一键启动
双击 start_video_composer.bat

# 或命令行
python video_composer.py
```

## 📁 项目结构

```
Himawari8-Earth-Downloader/
├── 📁 核心组件
│   ├── himawari8_scheduler.py      # 智能调度器
│   ├── himawari8downloader.py      # 基础下载器
│   └── video_composer.py           # 视频合成器
├── ⚙️ 配置文件
│   ├── scheduler_config.json       # 调度器配置
│   ├── video_config.json          # 合成器配置
│   └── requirements.txt           # 依赖列表
├── 📖 文档
│   ├── README.md                  # 项目总览
│   ├── SCHEDULER_README.md        # 调度器指南
│   ├── VIDEO_COMPOSER_README.md   # 合成器指南
│   └── video_composer_requirements.md
├── 🚀 启动脚本
│   ├── start_scheduler.bat        # 调度器启动
│   └── start_video_composer.bat   # 合成器启动
├── 📥 数据目录
│   ├── downloads/                 # 下载图片
│   └── videos/                    # 输出视频
└── 📋 日志
    └── logs/                      # 运行日志
```

## 🎯 使用场景

### 📅 日常使用
1. **启动调度器**：自动下载地球图片
2. **等待收集**：积累一段时间的图片
3. **制作视频**：选择时间范围合成视频
4. **分享成果**：获得精美的地球延时视频

### 🎬 视频制作示例
```bash
# 制作一天的地球延时视频
python video_composer.py --input ./downloads --mode fps --fps 30

# 制作慢动作效果
python video_composer.py --mode duration --duration 3.0
```

## ⚙️ 配置说明

### 调度器配置 (scheduler_config.json)
```json
{
  "output_dir": "./downloads",
  "scale": 4,
  "max_retries": 3,
  "first_timeout": 300,
  "retry_timeout": 210,
  "log_level": "INFO"
}
```

### 合成器配置 (video_config.json)
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

## 📊 输出示例

### 图片命名格式
```
downloads/
├── 2024-12-19-14-00.png
├── 2024-12-19-14-10.png
├── 2024-12-19-14-20.png
└── ...
```

### 视频命名格式
```
videos/
├── himawari8_20241219_1400_20241219_1600.mp4
└── himawari8_20241220_0800_20241220_1800.mp4
```

## 🔧 技术栈

- **🐍 Python 3.6+**：核心编程语言
- **🖼️ OpenCV**：视频处理与编码
- **🎨 Pillow**：图像处理
- **📊 Rich**：终端美化界面
- **⏱️ tqdm**：进度条显示
- **🗂️ Pathlib**：路径管理

## 🌐 API接口

### 获取图片列表
```python
GET /api/images
{
  "count": 144,
  "start_time": "2024-12-19T08:00:00",
  "end_time": "2024-12-19T20:00:00",
  "images": [...]
}
```

### 创建视频任务
```python
POST /api/compose
{
  "start_time": "2024-12-19-08-00",
  "end_time": "2024-12-19-20-00",
  "mode": "fps",
  "fps": 30
}
```

## 🎨 自定义扩展

### 添加新功能
1. 修改配置文件
2. 扩展Python脚本
3. 集成Web前端
4. 添加新的处理模式

### 性能优化
- **批量处理**：支持大量图片
- **内存管理**：流式处理大文件
- **多线程**：并行处理优化

## 📱 系统要求

- **操作系统**：Windows 10+/Linux/macOS
- **Python版本**：3.6或更高
- **内存要求**：至少2GB RAM
- **存储空间**：根据图片数量而定

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境
```bash
git clone https://github.com/[your-username]/himawari8-earth-downloader.git
cd himawari8-earth-downloader
pip install -r requirements.txt
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙋‍♂️ 问题反馈

- **Issues**：GitHub Issues页面
- **讨论**：GitHub Discussions
- **邮件**：项目维护者邮箱

---

<p align="center">
  <i>🌍 用代码记录地球的美丽瞬间 🌍</i>
</p>