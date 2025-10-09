#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新课程整合工具
将MP3文件夹中的CQ课程整合到NCE-Flow系统中
"""

import os
import json
import eyed3
import re
from pathlib import Path
from typing import List, Dict, Any

class CourseIntegrator:
    def __init__(self, data_path: str = "static/data.json", mp3_path: str = "MP3"):
        self.data_path = data_path
        self.mp3_path = mp3_path
        self.existing_data = self.load_existing_data()

    def load_existing_data(self) -> Dict[str, Any]:
        """加载现有的课程数据"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"未找到数据文件: {self.data_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return {}

    def scan_mp3_files(self) -> List[Dict[str, Any]]:
        """扫描MP3文件夹，获取课程信息"""
        mp3_files = []

        if not os.path.exists(self.mp3_path):
            print(f"MP3文件夹不存在: {self.mp3_path}")
            return mp3_files

        # 扫描所有MP3文件
        for file in os.listdir(self.mp3_path):
            if file.endswith('.mp3') and file.startswith('CQ'):
                mp3_path = os.path.join(self.mp3_path, file)
                course_info = self.extract_course_info(mp3_path, file)
                if course_info:
                    mp3_files.append(course_info)

        # 按课程编号排序
        mp3_files.sort(key=lambda x: x['number'])
        return mp3_files

    def extract_course_info(self, mp3_path: str, filename: str) -> Dict[str, Any]:
        """从MP3文件提取课程信息"""
        try:
            audio = eyed3.load(mp3_path)
            if not audio.tag:
                return None

            # 从文件名提取课程编号
            match = re.match(r'CQ(\d+)', filename)
            if not match:
                return None

            course_number = int(match.group(1))

            # 构建课程信息
            course_info = {
                'number': course_number,
                'filename': filename.replace('.mp3', ''),
                'title': audio.tag.title or filename.replace('.mp3', ''),
                'artist': audio.tag.artist or '',
                'album': audio.tag.album or '',
                'path': mp3_path,
                'has_lrc': os.path.exists(mp3_path.replace('.mp3', '.lrc')),
                'has_srt': os.path.exists(mp3_path.replace('.mp3', '.srt'))
            }

            return course_info

        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
            return None

    def generate_course_entries(self, mp3_files: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """生成课程条目，格式与现有数据一致"""
        entries = []

        for course in mp3_files:
            entry = {
                "title": course['title'],
                "filename": course['filename']
            }
            entries.append(entry)

        return entries

    def integration_options(self, mp3_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提供不同的整合选项"""
        options = {
            'add_as_new_book': {
                'description': '将CQ课程作为新书添加',
                'data': self.add_as_new_book(mp3_files)
            },
            'add_as_book_5': {
                'description': '将CQ课程作为第5本书添加',
                'data': self.add_as_book_5(mp3_files)
            },
            'separate_category': {
                'description': '创建独立分类',
                'data': self.create_separate_category(mp3_files)
            }
        }

        return options

    def add_as_new_book(self, mp3_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """方案一：作为新书添加"""
        new_data = self.existing_data.copy()
        new_data['CQ'] = self.generate_course_entries(mp3_files)
        return new_data

    def add_as_book_5(self, mp3_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """方案二：作为第5本书添加"""
        new_data = self.existing_data.copy()
        new_data['5'] = self.generate_course_entries(mp3_files)
        return new_data

    def create_separate_category(self, mp3_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """方案三：创建独立分类"""
        new_data = {
            'NCE': {},
            'CQ': {
                'title': 'ESL Podcast Premium: Introduction to the U.S.',
                'description': '美国公民考试准备课程',
                'lessons': self.generate_course_entries(mp3_files)
            }
        }

        # 保持原有的NCE数据
        for key, value in self.existing_data.items():
            new_data['NCE'][key] = value

        return new_data

    def show_preview(self, mp3_files: List[Dict[str, Any]]):
        """显示预览信息"""
        print("=== 新课程预览 ===")
        print(f"发现课程数量: {len(mp3_files)}")
        print(f"课程系列: {mp3_files[0]['album'] if mp3_files else 'Unknown'}")
        print("\n前5个课程:")
        for i, course in enumerate(mp3_files[:5]):
            print(f"  {i+1}. {course['title']} ({course['filename']})")

        if len(mp3_files) > 5:
            print(f"  ... 还有 {len(mp3_files) - 5} 个课程")

    def backup_existing_data(self) -> str:
        """备份现有数据"""
        backup_path = f"{self.data_path}.backup"
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.existing_data, f, ensure_ascii=False, indent=2)
            print(f"已备份数据到: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"备份失败: {e}")
            return ""

    def integrate(self, option: str = 'add_as_new_book', dry_run: bool = True):
        """执行整合"""
        print("=== 开始整合新课程 ===")

        # 扫描MP3文件
        mp3_files = self.scan_mp3_files()
        if not mp3_files:
            print("未找到任何MP3文件")
            return False

        # 显示预览
        self.show_preview(mp3_files)

        # 获取整合选项
        options = self.integration_options(mp3_files)
        if option not in options:
            print(f"无效的选项: {option}")
            print(f"可用选项: {list(options.keys())}")
            return False

        selected_option = options[option]
        print(f"\n选择的方案: {selected_option['description']}")

        # 备份现有数据
        if not dry_run:
            backup_path = self.backup_existing_data()

        # 显示整合后的数据结构
        new_data = selected_option['data']
        print(f"\n整合后的数据结构:")
        print(f"  书籍/分类数量: {len(new_data)}")

        if option == 'separate_category':
            print(f"  NCE课程: {sum(len(v) if isinstance(v, list) else 1 for v in new_data['NCE'].values())}")
            print(f"  CQ课程: {len(new_data['CQ']['lessons'])}")
        else:
            total_lessons = sum(len(v) for v in new_data.values() if isinstance(v, list))
            print(f"  总课程数: {total_lessons}")

        # 如果不是预览模式，保存数据
        if not dry_run:
            try:
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=2)
                print(f"\n✓ 整合完成！数据已保存到: {self.data_path}")
                return True
            except Exception as e:
                print(f"\n✗ 保存失败: {e}")
                return False
        else:
            print(f"\n📋 预览模式 - 未实际修改文件")
            return True

def main():
    import argparse

    parser = argparse.ArgumentParser(description='新课程整合工具')
    parser.add_argument('--option', choices=['add_as_new_book', 'add_as_book_5', 'separate_category'],
                       default='add_as_new_book', help='整合方案')
    parser.add_argument('--execute', action='store_true', help='执行整合（非预览模式）')
    parser.add_argument('--data-path', default='static/data.json', help='数据文件路径')
    parser.add_argument('--mp3-path', default='MP3', help='MP3文件夹路径')

    args = parser.parse_args()

    integrator = CourseIntegrator(args.data_path, args.mp3_path)
    success = integrator.integrate(args.option, dry_run=not args.execute)

    if success and args.execute:
        print("\n🎉 新课程整合成功！")
        print("请重启NCE-Flow应用程序以查看新课程。")
    elif not args.execute:
        print("\n💡 使用 --execute 参数执行实际整合")

if __name__ == "__main__":
    main()