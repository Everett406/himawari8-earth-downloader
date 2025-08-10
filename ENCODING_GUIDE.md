# 🎬 视频编码格式指南

## 📊 编码格式对比

| 编码格式 | 参数值 | 特点 | 文件大小 | 兼容性 | 质量 |
|----------|--------|------|----------|--------|------|
| **H.264** | `h264` | 高压缩率，平衡质量 | 小 | 非常好 | 高 |
| **H.265** | `h265` | 更高压缩率 | 更小 | 较好 | 很高 |
| **MPEG-4** | `mp4v` | 兼容性最好 | 中等 | 最好 | 中等 |
| **MJPEG** | `mjpeg` | 逐帧压缩 | 很大 | 好 | 最高 |

## 🎯 推荐设置

### 📱 日常使用
```bash
python video_composer.py --codec h264 --bitrate 10000
```

### 🎥 高质量存档
```bash
python video_composer.py --codec h265 --bitrate 20000
```

### 🌐 网络分享
```bash
python video_composer.py --codec h264 --bitrate 5000
```

### 💾 兼容性优先
```bash
python video_composer.py --codec mp4v --bitrate 8000
```

## 🔧 技术细节

### H.264 vs H.265
- **H.264**: 平衡压缩率和兼容性，适合大多数场景
- **H.265**: 压缩率比H.264高50%，但需要更多CPU资源

### 编码器支持
- **Windows**: H.264需要安装OpenH264或FFmpeg
- **macOS**: 原生支持H.264，H.265需要macOS 10.13+
- **Linux**: 需要安装x264/x265编码器

### 文件大小对比（30张图片，30秒视频）
| 编码格式 | 码率 | 文件大小 |
|----------|------|----------|
| H.264 | 10000 kbps | ~37 MB |
| H.265 | 10000 kbps | ~19 MB |
| MPEG-4 | 10000 kbps | ~42 MB |
| MJPEG | 10000 kbps | ~112 MB |

## 🚀 使用方法

### 命令行参数
```bash
# 指定H.264编码
python video_composer.py --codec h264 --bitrate 15000

# 使用H.265获得更小文件
python video_composer.py --codec h265 --bitrate 10000

# 兼容性设置
python video_composer.py --codec mp4v --bitrate 8000
```

### 交互式选择
运行程序时会提示：
```
📋 选择视频编码格式:
1. H.264 - 高压缩率，质量好（推荐）
2. H.265 - 更高压缩率，需要更多CPU
3. MPEG-4 - 兼容性最好
4. MJPEG - 质量高但文件大
```

### 配置文件设置
在 `video_config.json` 中：
```json
{
  "default_codec": "h264",
  "default_bitrate": 10000
}
```

## ⚠️ 注意事项

1. **系统支持**: H.265可能需要额外安装编码器
2. **播放兼容性**: 老设备可能不支持H.265
3. **处理时间**: H.265编码需要更多CPU资源
4. **文件扩展名**: 所有格式都输出为.mp4文件

## 🔍 故障排除

如果H.264编码不可用：
1. 安装FFmpeg
2. 使用 `--codec mp4v` 作为备选
3. 检查OpenCV版本（建议4.0+）