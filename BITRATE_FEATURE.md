# 🎞️ 码率选择功能说明

## ✅ 新增功能

视频合成器现已支持**码率选择功能**！

## 📊 码率选项

| 码率级别 | 数值 (kbps) | 适用场景 | 文件大小 |
|----------|-------------|----------|----------|
| 高质量   | 20000       | 高清存档 | 大 |
| 中等质量 | 10000       | 日常使用 | 中 |
| 标准质量 | 5000        | 网络分享 | 小 |
| 低质量   | 2000        | 快速预览 | 很小 |

## 🚀 使用方法

### 1. 命令行参数
```bash
# 设置高质量码率
python video_composer.py --bitrate 20000

# 设置标准码率
python video_composer.py --bitrate 5000

# 完整参数示例
python video_composer.py --mode fps --fps 30 --bitrate 15000
```

### 2. 配置文件设置
在 `video_config.json` 中设置：
```json
{
  "default_bitrate": 10000
}
```

### 3. 交互式选择
运行程序时，会提示选择码率：
```
📋 选择视频码率:
1. 高质量 (20000 kbps)
2. 中等质量 (10000 kbps) - 默认
3. 标准质量 (5000 kbps)
4. 低质量 (2000 kbps)
```

## 📁 更新文件

### 修改的文件
- ✅ `video_composer.py` - 添加码率参数支持
- ✅ `video_config.json` - 添加默认码率配置
- ✅ `VIDEO_COMPOSER_README.md` - 更新文档说明

### 新增功能
- ✅ 命令行参数 `--bitrate`
- ✅ 配置文件支持
- ✅ 交互式码率选择
- ✅ 向后兼容

## 🎯 实际效果

- **高质量 (20000 kbps)**: 适合专业用途，细节清晰
- **中等质量 (10000 kbps)**: 平衡质量和文件大小
- **标准质量 (5000 kbps)**: 适合社交媒体分享
- **低质量 (2000 kbps)**: 快速生成预览视频

## 🔧 技术实现

使用OpenCV的VideoWriter，通过参数控制：
- 支持1000-50000 kbps范围
- 自动适配不同编码器
- 保持向后兼容性

## 📋 验证测试

运行以下命令验证功能：
```bash
# 查看帮助信息
python video_composer.py --help

# 测试码率参数
python video_composer.py --bitrate 8000
```