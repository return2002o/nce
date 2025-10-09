#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的MP3转LRC工具
支持多种方法：ID3提取、语音识别、手动制作
"""

import os
import sys
import json
import argparse
from pathlib import Path
import subprocess

try:
    import eyed3
    import mutagen
    ID3_AVAILABLE = True
except ImportError:
    ID3_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class MP3ToLRCConverter:
    def __init__(self):
        self.id3_available = ID3_AVAILABLE
        self.whisper_available = WHISPER_AVAILABLE

    def extract_id3_lyrics(self, mp3_path):
        """从ID3标签提取歌词"""
        if not self.id3_available:
            print("未安装eyed3库，无法提取ID3标签")
            return None

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
                'syllable': []
            }

            # 提取USLT歌词
            for frame in audiofile.tag.frameiter(['USLT']):
                tag_info['unsync_lyrics'] = frame.text or ''

            # 提取SYLT同步歌词
            for frame in audiofile.tag.frameiter(['SYLT']):
                tag_info['syllable'].append({
                    'text': frame.text,
                    'timestamp': frame.timestamp,
                    'lang': frame.lang
                })

            return tag_info

        except Exception as e:
            print(f"读取ID3标签时出错: {e}")
            return None

    def extract_with_whisper(self, mp3_path):
        """使用Whisper语音识别提取歌词"""
        if not self.whisper_available:
            print("未安装whisper库，无法使用语音识别")
            return None

        try:
            print("正在使用Whisper进行语音识别...")
            model = whisper.load_model("base")
            result = model.transcribe(mp3_path)
            return result
        except Exception as e:
            print(f"Whisper识别时出错: {e}")
            return None

    def create_lrc_from_id3(self, tag_info, mp3_path):
        """从ID3标签信息创建LRC文件"""
        if tag_info['syllable']:
            # 有同步歌词，直接转换
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

        elif tag_info['unsync_lyrics']:
            # 无时间戳歌词，估算时间戳
            lyrics = tag_info['unsync_lyrics']
            lines = [line.strip() for line in lyrics.split('\n') if line.strip()]

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
                timestamp = i * time_per_line
                minutes = int(timestamp // 60)
                seconds = timestamp % 60
                lrc_content += f"[{minutes:02d}:{seconds:05.2f}]{line}\n"

            return lrc_content

        return None

    def create_lrc_from_whisper(self, whisper_result, mp3_path):
        """从Whisper识别结果创建LRC文件"""
        if 'segments' not in whisper_result:
            return None

        lrc_content = "[ar:Whisper识别]\n[ti:自动生成]\n[by:语音识别]\n\n"

        for segment in whisper_result['segments']:
            start_time = segment['start']
            text = segment['text'].strip()

            if text:
                minutes = int(start_time // 60)
                seconds = start_time % 60
                lrc_content += f"[{minutes:02d}:{seconds:05.2f}]{text}\n"

        return lrc_content

    def convert_single_file(self, mp3_path, method='auto'):
        """转换单个MP3文件"""
        if not os.path.exists(mp3_path):
            print(f"文件不存在: {mp3_path}")
            return False

        print(f"正在处理: {mp3_path}")

        lrc_content = None
        lrc_path = os.path.splitext(mp3_path)[0] + '.lrc'

        # 检查是否已存在
        if os.path.exists(lrc_path):
            print(f"LRC文件已存在: {lrc_path}")
            return False

        # 根据方法选择处理方式
        if method == 'id3' or method == 'auto':
            tag_info = self.extract_id3_lyrics(mp3_path)
            if tag_info and (tag_info['unsync_lyrics'] or tag_info['syllable']):
                lrc_content = self.create_lrc_from_id3(tag_info, mp3_path)
                print("✓ 从ID3标签提取歌词成功")
                method_used = 'ID3'
            elif method == 'id3':
                print("✗ ID3标签中未找到歌词")
                return False

        if not lrc_content and (method == 'whisper' or method == 'auto'):
            whisper_result = self.extract_with_whisper(mp3_path)
            if whisper_result:
                lrc_content = self.create_lrc_from_whisper(whisper_result, mp3_path)
                print("✓ 使用Whisper语音识别成功")
                method_used = 'Whisper'
            elif method == 'whisper':
                print("✗ Whisper识别失败")
                return False

        if not lrc_content:
            if method == 'auto':
                print("✗ 所有方法都失败了")
            return False

        # 保存LRC文件
        try:
            with open(lrc_path, 'w', encoding='utf-8') as f:
                f.write(lrc_content)
            print(f"✓ LRC文件已保存: {lrc_path} (使用{method_used}方法)")
            return True
        except Exception as e:
            print(f"✗ 保存LRC文件时出错: {e}")
            return False

    def batch_convert(self, directory, method='auto'):
        """批量转换目录下的MP3文件"""
        mp3_files = list(Path(directory).rglob('*.mp3'))

        if not mp3_files:
            print(f"在目录 {directory} 中未找到MP3文件")
            return

        print(f"找到 {len(mp3_files)} 个MP3文件")

        success_count = 0
        for mp3_file in mp3_files:
            print(f"\n{'='*60}")
            if self.convert_single_file(str(mp3_file), method):
                success_count += 1

        print(f"\n{'='*60}")
        print(f"转换完成: {success_count}/{len(mp3_files)} 个文件成功")


def main():
    parser = argparse.ArgumentParser(description='MP3转LRC工具')
    parser.add_argument('input', help='MP3文件或目录路径')
    parser.add_argument('-m', '--method', choices=['auto', 'id3', 'whisper'],
                       default='auto', help='提取方法: auto(自动), id3(ID3标签), whisper(语音识别)')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    converter = MP3ToLRCConverter()

    # 检查依赖
    if not converter.id3_available:
        print("警告: 未安装eyed3库，无法使用ID3提取方法")
        print("安装命令: pip install eyed3")

    if not converter.whisper_available:
        print("警告: 未安装whisper库，无法使用语音识别方法")
        print("安装命令: pip install openai-whisper")

    # 处理输入
    if os.path.isfile(args.input) and args.input.lower().endswith('.mp3'):
        converter.convert_single_file(args.input, args.method)
    elif os.path.isdir(args.input):
        converter.batch_convert(args.input, args.method)
    else:
        print(f"无效的路径: {args.input}")


if __name__ == "__main__":
    main()