
> [!NOTE]
> **本仓库已迁移至 Gitee**：<https://gitee.com/Everett5678/himawari8-earth-downloader>
> GitHub 端仅作只读归档，新代码请推送到 Gitee。

---
# Himawari8 Image Downloader

**himawari8downloader** is a tool to download near real time earth images taken by [**Himawari8**](https://en.wikipedia.org/wiki/Himawari_8) .

## Dependency
**himawari8downloader** depends on `Pillow`, `Requests`, and `python-dateutil`:

```bash
pip install -r requirements.txt
```

## Usage

支持多种参数组合，可以自定义输出文件名、分辨率倍数和下载路径。

### 参数说明
- *fout*: 输出文件名（可选，默认为时间戳）
- *scale*: 分辨率倍数，图像宽高为 *scale*×550（可选，默认为4）
- *output_dir*: 自定义下载目录路径（可选，默认为当前目录）

### 支持的分辨率倍数
*scale* 可以是：1, 2, 4, 8, 16, 20

### 使用示例

```bash
# 默认4倍大小，自动生成文件名，保存到当前目录
python himawari8downloader.py

# 指定输出文件名，使用默认4倍大小，保存到当前目录
python himawari8downloader.py earth.png

# 指定输出文件名和分辨率倍数，保存到当前目录
python himawari8downloader.py earth.png 2

# 指定输出文件名和自定义下载目录
python himawari8downloader.py earth.png D:\Images\Himawari8

# 指定输出文件名、分辨率倍数和自定义下载目录
python himawari8downloader.py earth.png 4 D:\Images\Himawari8

# 使用默认文件名，指定分辨率倍数和自定义下载目录
python himawari8downloader.py 4 D:\Images\Himawari8
```

### 自定义下载路径特性
- 如果指定的目录不存在，程序会自动创建
- 支持绝对路径和相对路径
- 跨平台兼容（Windows、Linux、macOS）

This will create an image file in the specified directory, and the image size will be *scale*×550 pixels.

## Result

![Result Image](earth.png)
