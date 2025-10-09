# MP3转LRC工具使用指南

这个工具包提供了多种方法从MP3文件中提取歌词并生成LRC格式文件。

## 安装依赖

### 基础依赖（ID3提取）
```bash
pip install eyed3 mutagen
```

### 语音识别依赖（可选）
```bash
pip install openai-whisper
```

## 使用方法

### 1. 快速使用（自动模式）
```bash
# 处理单个文件
python mp3_to_lrc_complete.py "MP3\CQ001.mp3"

# 处理整个目录
python mp3_to_lrc_complete.py MP3
```

### 2. 指定方法
```bash
# 仅从ID3标签提取
python mp3_to_lrc_complete.py "MP3\CQ001.mp3" --method id3

# 使用语音识别
python mp3_to_lrc_complete.py "MP3\CQ001.mp3" --method whisper
```

### 3. 仅检查ID3标签信息
```bash
python extract_id3_lyrics.py "MP3\CQ001.mp3"
```

## 支持的提取方法

### 1. ID3标签提取（推荐）
- **USLT标签**: 无时间戳的歌词
- **SYLT标签**: 带时间戳的同步歌词
- **其他歌词标签**: 通用歌词信息

**优点**:
- 快速，无需网络
- 如果有同步歌词，精度最高
- 保持原始歌词格式

**缺点**:
- 需要MP3文件包含歌词标签
- 无时间戳歌词需要估算时间

### 2. Whisper语音识别
- 自动将语音转换为文本
- 生成精确的时间戳

**优点**:
- 适用于任何MP3文件
- 时间戳精确
- 支持多语言

**缺点**:
- 需要下载Whisper模型
- 处理速度较慢
- 可能需要网络连接

### 3. 自动模式（默认）
1. 首先尝试ID3提取
2. 如果失败，使用Whisper识别
3. 选择最佳可用方法

## LRC文件格式

生成的LRC文件遵循标准格式：
```lrc
[ar:艺术家]
[ti:标题]
[al:专辑]
[by:提取方法]

[00:12.34]歌词内容
[00:25.67]下一行歌词
```

## 高级功能

### 批量处理
```bash
# 处理整个目录的MP3文件
python mp3_to_lrc_complete.py /path/to/music/folder
```

### 与NCE-Flow集成
生成的LRC文件可以直接用于NCE-Flow项目：
1. 将MP3文件放在对应的NCE目录下
2. 运行转换工具生成LRC文件
3. 更新`static/data.json`添加课程信息

## 常见问题

### Q: MP3文件没有歌词标签怎么办？
A: 使用Whisper语音识别方法：
```bash
python mp3_to_lrc_complete.py "your_song.mp3" --method whisper
```

### Q: 生成的LRC时间戳不准确？
A:
- 对于ID3提取的无时间戳歌词，工具会均匀分配时间戳
- 对于重要文件，建议手动调整或使用专业LRC编辑器

### Q: 如何处理中文歌词？
A: Whisper支持中文识别，但可能需要指定语言：
```python
# 在mp3_to_lrc_complete.py中修改
model = whisper.load_model("base")
result = model.transcribe(mp3_path, language="zh")
```

### Q: 生成的LRC文件如何用于NCE-Flow？
A:
1. 确保LRC文件名与MP3文件名相同（扩展名不同）
2. 放在对应的NCE目录下
3. 格式支持双语显示（英文|中文）

## 手动制作LRC

对于需要精确控制的LRC文件，建议使用专业工具：
- **Aegisub**: 专业字幕编辑器
- **PotPlayer**: 支持LRC制作
- **LyricsTraining**: 在线歌词同步工具

## 性能提示

- ID3提取：几乎瞬间完成
- Whisper识别：首次使用需要下载模型（约150MB），之后速度取决于音频长度
- 批量处理建议先测试几个文件，确认效果满意后再处理整个目录