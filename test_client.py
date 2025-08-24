#!/usr/bin/env python3
"""
通用文件统计MVP测试客户端
使用fastmcp的stdio模式进行测试
"""

import asyncio
import subprocess
import json
import sys
from pathlib import Path
import json  # 添加json模块用于解析时间维度功能返回数据

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mvp():
    """通过命令行方式测试MCP服务"""
    
    print("🧪 通用文件统计MVP测试")
    print("=" * 40)
    
    # 测试1：直接调用函数测试
    from mcp_server import (
        count_files, list_files, categorize_files_by_extension,
        get_directory_size, find_large_files,
        find_empty_folders, find_duplicate_files,
        get_recent_files, get_files_by_date_range, get_file_timeline
    )
    
    # 测试桌面文件统计
    try:
        desktop_total = await count_files()
        print(f"📁 桌面文件总数: {desktop_total}")
    except Exception as e:
        print(f"❌ 桌面文件统计失败: {e}")
    
    # 测试Documents目录PDF
    try:
        pdf_count = await count_files("~/Documents", "pdf")
        print(f"📄 Documents目录PDF文件: {pdf_count}")
    except Exception as e:
        print(f"❌ PDF文件统计失败: {e}")
    
    # 测试下载目录JPG（递归）
    try:
        jpg_count = await count_files("~/Downloads", "jpg", True)
        print(f"🖼️ Downloads目录JPG文件（含子目录）: {jpg_count}")
    except Exception as e:
        print(f"❌ JPG文件统计失败: {e}")
    
    # 测试列出PNG文件
    try:
        png_files = await list_files("~/Desktop", "png")
        if png_files:
            print(f"🎨 桌面PNG文件（前3个）: {png_files[:3]}")
        else:
            print("🎨 桌面无PNG文件")
    except Exception as e:
        print(f"❌ PNG文件列表失败: {e}")
    
    # 测试递归列出所有文件
    try:
        all_files = await list_files("~/Desktop", recursive=True)
        if all_files:
            print(f"📂 桌面所有文件（前5个）: {all_files[:5]}")
            print(f"📊 桌面文件总数: {len(all_files)}")
        else:
            print("📂 桌面无文件")
    except Exception as e:
        print(f"❌ 文件列表失败: {e}")
    
    # 测试按后缀分类功能
    print("\n🗂️  按文件后缀分类（桌面）:")
    print("-" * 40)
    try:
        categorized = await categorize_files_by_extension("~/Desktop")
        if categorized:
            for ext, files in sorted(categorized.items()):
                print(f"{ext}: {len(files)}个文件")
                # 显示前3个文件的完整路径
                for i, file_path in enumerate(files[:3]):
                    print(f"  {i+1}. {file_path}")
                if len(files) > 3:
                    print(f"  ... 还有{len(files)-3}个文件")
        else:
            print("📂 桌面无文件")
    except Exception as e:
        print(f"❌ 文件分类失败: {e}")
    
    # 测试递归分类
    print("\n🗂️  按文件后缀分类（桌面-递归）:")
    print("-" * 40)
    categorized_recursive = await categorize_files_by_extension("~/Desktop", True)
    for ext, files in categorized_recursive.items():
        print(f"{ext}: {len(files)}个文件")
        if files:
            print(f"  示例: {files[0]}")
    
    # 测试新功能：文件大小统计
    print("\n📊 文件大小统计测试")
    print("=" * 50)
    
    # 测试目录大小统计
    desktop_size = await get_directory_size("~/Desktop")
    print(f"📁 桌面总大小: {desktop_size['formatted_total']}")
    print(f"📊 文件总数: {desktop_size['total_files']}个")
    print(f"📏 平均大小: {desktop_size['formatted_average']}")
    
    # 测试指定单位的大小统计
    desktop_size_mb = await get_directory_size("~/Desktop", "MB")
    print(f"📁 桌面大小(MB): {desktop_size_mb['formatted_total']}")
    
    # 测试递归目录大小
    recursive_size = await get_directory_size("~/Desktop", "GB", True)
    print(f"📁 桌面递归大小(GB): {recursive_size['formatted_total']}")
    
    # 测试大文件识别
    print("\n🔍 大文件识别测试")
    print("-" * 30)
    large_files = await find_large_files("~/Desktop", 10)  # 查找超过10MB的文件
    if large_files:
        print(f"发现 {len(large_files)} 个大文件:")
        for file in large_files[:3]:  # 只显示前3个
            print(f"  📄 {file['filename']}: {file['size_formatted']}")
    else:
        print("未发现超过10MB的大文件")
    
    # 测试递归大文件查找
    large_files_recursive = await find_large_files("~/Desktop", 50, True)
    if large_files_recursive:
        print(f"递归查找发现 {len(large_files_recursive)} 个超过50MB的文件")
    
    print("\n✅ 文件大小统计功能验证完成！")
    print("支持：目录总大小、平均大小、智能单位转换、大文件识别")
    
    print("\n✅ 通用文件统计功能验证完成！")
    print("支持：任意文件类型、任意目录、递归统计、后缀分类")
    
    # 🧪 新增功能测试：空文件夹检测和重复文件查找
    print("\n🧪 新增功能测试")
    print("=" * 40)
    
    # 空文件夹检测
    empty_folders = await find_empty_folders("~/Desktop")
    print(f"📁 桌面空文件夹: {len(empty_folders)}个")
    if empty_folders:
        for folder in empty_folders[:3]:  # 显示前3个
            print(f"   📂 {Path(folder).name}")
    else:
        print("   ✅ 未发现空文件夹")
    
    # 重复文件查找
    duplicate_files = await find_duplicate_files("~/Desktop")
    print(f"🔄 桌面重复文件: {len(duplicate_files)}组")
    if duplicate_files:
        for hash_val, files in list(duplicate_files.items())[:2]:  # 显示前2组
            print(f"   📋 重复组: {len(files)}个文件")
            for file_path in files[:2]:  # 每组显示前2个
                print(f"      📄 {Path(file_path).name}")
    else:
        print("   ✅ 未发现重复文件")
    
    # 时间维度功能测试 - 通过MCP客户端调用
    print("\n" + "="*50)
    print("时间维度功能测试 (MCP客户端)")
    print("="*50)
    
    # 测试1: 最近7天文件
    try:
        from mcp_server import get_recent_files
        recent_files = await get_recent_files("~/Desktop", 7, None, False)
        print(f"最近7天修改文件: {len(recent_files)}个")
        if len(recent_files) > 0:
            print("最新3个文件:")
            for file in recent_files[:3]:
                print(f"  - {file['filename']} ({file['size_formatted']}) - {file['modified_time']}")
        else:
            print("最近7天无文件修改")
    except Exception as e:
        print(f"❌ 最近文件查询失败: {e}")
    
    # 测试2: 日期范围查询
    try:
        from mcp_server import get_files_by_date_range
        date_range_files = await get_files_by_date_range(
            "~/Desktop", 
            "2024-01-01", 
            "2024-12-31", 
            None, 
            False
        )
        print(f"\n2024年文件查询: {date_range_files['total_count']}个文件")
        if date_range_files['files']:
            print("前3个文件:")
            for file in date_range_files['files'][:3]:
                print(f"  - {file['filename']} ({file['size_formatted']}) - {file['modified_time']}")
    except Exception as e:
        print(f"❌ 日期范围查询失败: {e}")
    
    # 测试3: 时间线视图
    try:
        from mcp_server import get_file_timeline
        timeline = await get_file_timeline("~/Desktop", 30, "day", False)
        summary = timeline.get("summary", {})
        print(f"\n最近30天时间线:")
        print(f"总文件数: {summary.get('total_files', 0)}个")
        print(f"总大小: {summary.get('total_size_formatted', '0 B')}")
        
        timeline_dict = timeline.get("timeline", {})
        if timeline_dict:
            # 显示最近3天
            recent_days = sorted(timeline_dict.keys(), reverse=True)[:3]
            for day in recent_days:
                day_data = timeline_dict[day]
                print(f"  {day}: {day_data['count']}个文件, {day_data['total_size_formatted']}")
        else:
            print("时间线视图无数据")
    except Exception as e:
        print(f"❌ 时间线视图查询失败: {e}")
    
    # 测试4: 按扩展名过滤
    try:
        recent_pdfs = await get_recent_files("~/Desktop", 30, "pdf", False)
        print(f"\n最近30天PDF文件: {len(recent_pdfs)}个")
        if recent_pdfs:
            for file in recent_pdfs[:2]:
                print(f"  - {file['filename']} ({file['size_formatted']})")
    except Exception as e:
        print(f"❌ PDF文件过滤查询失败: {e}")
    
    print("\n时间维度功能验证完成！")

def run_server_test():
    """运行服务器测试"""
    print("🔧 启动MCP服务器测试...")
    
    # 启动服务器
    try:
        import mcp_server
        print("✅ MCP服务器加载成功")
        return True
    except Exception as e:
        print(f"❌ MCP服务器加载失败: {e}")
        return False

if __name__ == "__main__":
    # 先测试服务器
    if run_server_test():
        # 再测试功能
        asyncio.run(test_mvp())
    else:
        sys.exit(1)