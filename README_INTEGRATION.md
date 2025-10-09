# 新课程整合指南

## 概述
MP3文件夹包含101个CQ系列课程（ESL Podcast Premium: Introduction to the U.S.），需要整合到NCE-Flow系统中。

## 课程信息
- **课程系列**: ESL Podcast Premium: Introduction to the U.S.
- **课程数量**: 101个 (CQ001-CQ100 + CQ2009Update)
- **文件格式**: MP3 + LRC + SRT
- **课程类型**: 美国公民考试准备课程

## 整合方案

### 方案一：作为新书添加 (推荐)
```json
{
  "1": [...],  // NCE1
  "2": [...],  // NCE2
  "3": [...],  // NCE3
  "4": [...],  // NCE4
  "CQ": [...]  // CQ系列 (新增)
}
```

**优点**:
- 保持CQ课程的独立性
- 不影响现有NCE课程结构
- 便于后续扩展

### 方案二：作为第5本书添加
```json
{
  "1": [...],
  "2": [...],
  "3": [...],
  "4": [...],
  "5": [...]   // CQ系列作为第5本书
}
```

**优点**:
- 统一的课程编号
- 简化数据结构

### 方案三：独立分类结构
```json
{
  "NCE": {
    "1": [...],
    "2": [...],
    "3": [...],
    "4": [...]
  },
  "CQ": {
    "title": "ESL Podcast Premium: Introduction to the U.S.",
    "description": "美国公民考试准备课程",
    "lessons": [...]
  }
}
```

**优点**:
- 完全分离的课程体系
- 支持不同的元数据结构

## 使用整合工具

### 1. 预览整合效果
```bash
# 预览方案一（推荐）
python integrate_new_courses.py --option add_as_new_book

# 预览方案二
python integrate_new_courses.py --option add_as_book_5

# 预览方案三
python integrate_new_courses.py --option separate_category
```

### 2. 执行整合
```bash
# 执行方案一整合
python integrate_new_courses.py --option add_as_new_book --execute

# 指定路径
python integrate_new_courses.py --data-path static/data.json --mp3-path MP3 --execute
```

## 整合工具功能

### 自动特性
- **自动扫描**: 扫描MP3文件夹中的所有CQ课程
- **ID3标签提取**: 从MP3文件中提取标题、艺术家、专辑信息
- **文件检查**: 自动检测LRC和SRT文件是否存在
- **数据备份**: 整合前自动备份现有数据
- **排序处理**: 按课程编号自动排序

### 课程信息提取
```python
{
    "number": 1,
    "filename": "CQ001",
    "title": "CQ001",
    "artist": "Center for Educational Development",
    "album": "ESL Podcast Premium: Introduction to the U.S.",
    "path": "MP3/CQ001.mp3",
    "has_lrc": true,
    "has_srt": true
}
```

## 后续步骤

### 1. 前端适配
需要修改前端代码以支持新的课程结构：

```javascript
// 在app.js中添加CQ系列支持
function loadBookList() {
    const books = ['1', '2', '3', '4', 'CQ']; // 添加CQ
    // ...
}
```

### 2. 文件组织
建议将CQ课程文件移到独立文件夹：
```
NCE-Flow/
├── CQ/           # CQ课程文件夹
│   ├── CQ001.mp3
│   ├── CQ001.lrc
│   └── ...
├── NCE1/          # 现有NCE课程
├── NCE2/
├── NCE3/
└── NCE4/
```

### 3. 数据格式统一
确保CQ课程的数据格式与NCE课程一致：

```json
{
    "title": "CQ001",
    "filename": "CQ001"
}
```

## 注意事项

1. **备份重要**: 整合工具会自动备份现有数据
2. **测试先行**: 建议先在预览模式下检查效果
3. **文件路径**: 确保MP3文件路径正确
4. **编码格式**: 使用UTF-8编码处理中文内容
5. **LRC兼容性**: 确保生成的LRC文件与现有播放器兼容

## 故障排除

### 常见问题
1. **依赖缺失**: 确保安装了eyed3库
   ```bash
   pip install eyed3
   ```

2. **路径问题**: 使用绝对路径或确保相对路径正确

3. **权限问题**: 确保有写入data.json的权限

4. **编码问题**: 确保系统支持UTF-8编码

### 回滚操作
如果整合出现问题，可以使用备份文件恢复：
```bash
cp static/data.json.backup static/data.json
```

## 预期效果

整合成功后，用户将能够：
- 在主界面看到CQ课程系列
- 正常播放CQ课程的音频和歌词
- 使用现有的语言切换功能
- 享受与NCE课程相同的使用体验