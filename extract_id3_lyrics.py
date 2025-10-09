#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MP3 ID3标签歌词提取工具
从MP3文件的ID3标签中提取歌词并转换为LRC格式
"""

import os
import sys
import eyed3
from pathlib import Path


def extract_id3_tags(mp3_path):
    """提取MP3文件的ID3标签信息"""
    try:
        audiofile = eyed3.load(mp3_path)
        if not audiofile.tag:
            return None

        tag_info = {
            'title': audiofile.tag.title or '',
            'artist': audiofile.tag.artist or '',
            'album': audiofile.tag.album or '',
            'lyrics': '',
            'unsync_lyrics': '',
            'uslt': '',
            'syllable': []
        }

        # 提取各种类型的歌词
        # USLT (Unsynchronized lyrics)
        for frame in audiofile.tag.frameiter(['USLT']):
            tag_info['uslt'] = frame.text or ''
            tag_info['unsync_lyrics'] = frame.text or ''

        # SYLT (Synchronized lyrics)
        for frame in audiofile.tag.frameiter(['SYLT']):
            tag_info['syllable'].append({
                'text': frame.text,
                'timestamp': frame.timestamp,
                'lang': frame.lang
            })

        # 其他可能的歌词标签
        for frame in audiofile.tag.frameiter():
            if hasattr(frame, 'text') and isinstance(frame.text, str):
                if 'lyrics' in str(frame.id).lower() or 'lrc' in str(frame.id).lower():
                    tag_info['lyrics'] = frame.text

        return tag_info

    except Exception as e:
        print(f"读取ID3标签时出错: {e}")
        return None


def convert_uslt_to_lrc(tag_info, mp3_path):
    """将无时间戳歌词转换为LRC格式"""
    if not tag_info['unsync_lyrics'] and not tag_info['lyrics']:
        return None

    lyrics = tag_info['unsync_lyrics'] or tag_info['lyrics']

    # 简单的歌词分行处理
    lines = lyrics.split('\n')

    # 估算每行的时间戳 (假设歌词均匀分布)
    # 获取音频时长
    try:
        audiofile = eyed3.load(mp3_path)
        duration = audiofile.info.time_secs
    except:
        duration = 180  # 默认3分钟

    time_per_line = duration / len(lines) if lines else 0

    lrc_content = f"[ar:{tag_info['artist']}]\n"
    lrc_content += f"[ti:{tag_info['title']}]\n"
    lrc_content += f"[al:{tag_info['album']}]\n"
    lrc_content += f"[by:ID3提取]\n\n"

    for i, line in enumerate(lines):
        if line.strip():
            timestamp = i * time_per_line
            minutes = int(timestamp // 60)
            seconds = timestamp % 60
            lrc_content += f"[{minutes:02d}:{seconds:05.2f}]{line}\n"

    return lrc_content


def convert_syllable_to_lrc(tag_info):
    """将带时间戳的歌词转换为LRC格式"""
    if not tag_info['syllable']:
        return None

    lrc_content = f"[ar:{tag_info['artist']}]\n"
    lrc_content += f"[ti:{tag_info['title']}]\n"
    lrc_content += f"[al:{tag_info['album']}]\n"
    lrc_content += f"[by:ID3同步歌词提取]\n\n"

    # 按时间戳排序
    syllable_sorted = sorted(tag_info['syllable'], key=lambda x: x.get('timestamp', 0))

    for item in syllable_sorted:
        timestamp = item.get('timestamp', 0)
        if timestamp:
            minutes = int(timestamp // 60)
            seconds = timestamp % 60
            text = item.get('text', '')
            lrc_content += f"[{minutes:02d}:{seconds:05.2f}]{text}\n"

    return lrc_content


def analyze_mp3_file(mp3_path):
    """分析MP3文件并提取歌词"""
    print(f"正在分析: {mp3_path}")

    if not os.path.exists(mp3_path):
        print(f"文件不存在: {mp3_path}")
        return

    # 提取ID3标签
    tag_info = extract_id3_tags(mp3_path)

    if not tag_info:
        print("未找到ID3标签信息")
        return

    print("=== ID3标签信息 ===")
    print(f"标题: {tag_info['title']}")
    print(f"艺术家: {tag_info['artist']}")
    print(f"专辑: {tag_info['album']}")

    # 显示歌词信息
    if tag_info['unsync_lyrics']:
        print(f"无时间戳歌词: {len(tag_info['unsync_lyrics'])} 字符")
        print(f"预览: {tag_info['unsync_lyrics'][:100]}...")

    if tag_info['syllable']:
        print(f"同步歌词: {len(tag_info['syllable'])} 个片段")

    if tag_info['lyrics']:
        print(f"其他歌词: {len(tag_info['lyrics'])} 字符")

    # 生成LRC文件
    lrc_content = None

    # 优先使用同步歌词
    if tag_info['syllable']:
        lrc_content = convert_syllable_to_lrc(tag_info)
        print("使用同步歌词生成LRC")
    elif tag_info['unsync_lyrics'] or tag_info['lyrics']:
        lrc_content = convert_uslt_to_lrc(tag_info, mp3_path)
        print("使用无时间戳歌词生成LRC")

    if lrc_content:
        lrc_path = os.path.splitext(mp3_path)[0] + '.lrc'

        # 检查是否已存在
        if os.path.exists(lrc_path):
            print(f"LRC文件已存在: {lrc_path}")
            overwrite = input("是否覆盖? (y/N): ").lower().strip()
            if overwrite != 'y':
                print("跳过保存")
                return

        try:
            with open(lrc_path, 'w', encoding='utf-8') as f:
                f.write(lrc_content)
            print(f"LRC文件已保存: {lrc_path}")
        except Exception as e:
            print(f"保存LRC文件时出错: {e}")
    else:
        print("未找到歌词信息，无法生成LRC文件")


def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python extract_id3_lyrics.py <mp3文件路径>")
        print("  python extract_id3_lyrics.py <目录路径>  # 处理目录下所有MP3")
        print("\n示例:")
        print("  python extract_id3_lyrics.py MP3\\CQ001.mp3")
        print("  python extract_id3_lyrics.py MP3")
        return

    path = sys.argv[1]

    if os.path.isfile(path) and path.lower().endswith('.mp3'):
        analyze_mp3_file(path)
    elif os.path.isdir(path):
        # 处理目录下所有MP3文件
        mp3_files = list(Path(path).rglob('*.mp3'))
        print(f"找到 {len(mp3_files)} 个MP3文件")

        for mp3_file in mp3_files:
            print(f"\n{'='*50}")
            analyze_mp3_file(str(mp3_file))
    else:
        print(f"无效的路径: {path}")


if __name__ == "__main__":
    main()