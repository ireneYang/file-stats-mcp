from fastmcp import FastMCP
from pathlib import Path
import shutil
import os
import json
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

mcp = FastMCP("Universal File Counter")

@mcp.tool()
async def count_files(
    directory: str = "~/Desktop", 
    extension: str = None,
    recursive: bool = False
) -> int:
    """统计指定目录中的文件数量（支持任意文件类型）
    
    Args:
        directory: 目标目录路径，支持用户目录简写（如 ~/Documents）
        extension: 文件扩展名（如 txt, pdf, jpg），None表示所有文件
        recursive: 是否递归子目录，默认False
    
    Returns:
        文件数量
    
    Examples:
        count_files()  # 统计桌面所有文件
        count_files("~/Documents", "pdf")  # 统计Documents目录PDF文件
        count_files("~/Downloads", "jpg", True)  # 递归统计下载目录JPG文件
    """
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return 0
    
    if extension:
        pattern = f"**/*.{extension}" if recursive else f"*.{extension}"
    else:
        pattern = "**/*" if recursive else "*"
    
    return len([f for f in target_dir.glob(pattern) if f.is_file()])

@mcp.tool()
async def list_files(
    directory: str = "~/Desktop",
    extension: str = None,
    recursive: bool = False
) -> list[str]:
    """列出指定目录中的所有文件（支持任意文件类型）
    
    Args:
        directory: 目标目录路径，支持用户目录简写
        extension: 文件扩展名，None表示所有文件
        recursive: 是否递归子目录，默认False
    
    Returns:
        相对路径列表
    
    Examples:
        list_files()  # 列出桌面所有文件
        list_files("~/Documents", "pdf")  # 列出Documents目录PDF文件
    """
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return []
    
    if extension:
        pattern = f"**/*.{extension}" if recursive else f"*.{extension}"
    else:
        pattern = "**/*" if recursive else "*"
    
    files = [f.relative_to(target_dir) for f in target_dir.glob(pattern) if f.is_file()]
    return [str(f) for f in sorted(files)]

@mcp.tool()
async def categorize_files_by_extension(
    directory: str = "~/Desktop",
    recursive: bool = False
) -> dict[str, list[str]]:
    """按文件后缀分类并列出文件列表（包含完整路径）
    
    Args:
        directory: 目标目录路径，支持用户目录简写（如 ~/Desktop）
        recursive: 是否递归子目录，默认False
    
    Returns:
        按文件后缀分类的字典，键为后缀名，值为包含完整路径的文件列表
    
    Examples:
        categorize_files_by_extension()  # 桌面文件按后缀分类
        categorize_files_by_extension("~/Documents", True)  # 递归分类Documents目录
    """
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return {}
    
    pattern = "**/*" if recursive else "*"
    
    # 收集所有文件并按后缀分类
    categorized = {}
    for file_path in target_dir.glob(pattern):
        if file_path.is_file():
            suffix = file_path.suffix.lower()  # 获取文件后缀（小写）
            if not suffix:  # 无后缀文件
                suffix = "no_extension"
            
            # 使用完整绝对路径
            full_path = str(file_path.absolute())
            
            if suffix not in categorized:
                categorized[suffix] = []
            categorized[suffix].append(full_path)
    
    # 对每个分类的文件按名称排序
    for suffix in categorized:
        categorized[suffix].sort()
    
    return categorized

@mcp.tool()
def format_file_size(size_bytes: int) -> str:
    """将字节大小转换为人类可读格式
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        格式化后的字符串（如：1.5 GB、256.3 MB）
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"

@mcp.tool()
async def get_directory_size(
    directory: str = "~/Desktop",
    unit: str = "auto",
    recursive: bool = False
) -> dict[str, any]:
    """统计目录总大小和文件数量
    
    Args:
        directory: 目标目录路径
        unit: 返回单位（"auto", "B", "KB", "MB", "GB", "TB"）
        recursive: 是否递归子目录
    
    Returns:
        包含总大小、文件数量、平均大小的字典
    
    Examples:
        get_directory_size()  # 桌面总大小（自动单位）
        get_directory_size("~/Documents", "MB")  # Documents大小（MB）
        get_directory_size("~/Downloads", "GB", True)  # 递归统计下载目录（GB）
    """
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return {"total_size": 0, "total_files": 0, "average_size": 0, "unit": unit}
    
    pattern = "**/*" if recursive else "*"
    
    total_size = 0
    total_files = 0
    
    for file_path in target_dir.glob(pattern):
        if file_path.is_file():
            try:
                total_size += file_path.stat().st_size
                total_files += 1
            except (OSError, PermissionError):
                # 跳过无法访问的文件
                continue
    
    average_size = total_size / total_files if total_files > 0 else 0
    
    # 根据单位格式化结果
    if unit == "auto":
        formatted_total = format_file_size(total_size)
        formatted_avg = format_file_size(int(average_size))
    else:
        units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        if unit in units:
            formatted_total = f"{total_size / units[unit]:.1f} {unit}"
            formatted_avg = f"{average_size / units[unit]:.1f} {unit}"
        else:
            formatted_total = format_file_size(total_size)
            formatted_avg = format_file_size(int(average_size))
    
    return {
        "total_size_bytes": total_size,
        "total_files": total_files,
        "average_size_bytes": int(average_size),
        "formatted_total": formatted_total,
        "formatted_average": formatted_avg,
        "unit": unit
    }

@mcp.tool()
async def find_large_files(
    directory: str = "~/Desktop",
    min_size_mb: float = 100,
    recursive: bool = False
) -> list[dict[str, any]]:
    """查找大文件
    
    Args:
        directory: 目标目录路径
        min_size_mb: 最小文件大小（MB）
        recursive: 是否递归子目录
    
    Returns:
        大文件列表，包含文件名、大小、路径信息
    
    Examples:
        find_large_files()  # 查找桌面超过100MB的文件
        find_large_files("~/Documents", 500)  # 查找超过500MB的文件
        find_large_files("~/Downloads", 1024, True)  # 递归查找超过1GB的文件
    """
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return []
    
    min_size_bytes = int(min_size_mb * 1024 * 1024)
    pattern = "**/*" if recursive else "*"
    
    large_files = []
    
    for file_path in target_dir.glob(pattern):
        if file_path.is_file():
            try:
                file_size = file_path.stat().st_size
                if file_size >= min_size_bytes:
                    large_files.append({
                        "filename": file_path.name,
                        "size_bytes": file_size,
                        "size_formatted": format_file_size(file_size),
                        "full_path": str(file_path.absolute()),
                        "relative_path": str(file_path.relative_to(target_dir)),
                        "directory": str(file_path.parent)
                    })
            except (OSError, PermissionError):
                continue
    
    # 按文件大小降序排序
    large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
    
    return large_files

@mcp.tool()
async def find_empty_folders(directory: str = "~/Desktop", recursive: bool = False) -> list[str]:
    """查找空文件夹
    
    Args:
        directory: 要检查的目录路径，支持~简写
        recursive: 是否递归检查子目录
    
    Returns:
        空文件夹路径列表
    """
    base_path = Path(directory).expanduser()
    if not base_path.exists():
        return []
    
    empty_folders = []
    
    if recursive:
        # 递归检查所有子目录
        for folder_path, subdirs, files in os.walk(base_path):
            folder = Path(folder_path)
            try:
                # 检查文件夹是否为空（不包含文件和子文件夹）
                if not any(folder.iterdir()):
                    empty_folders.append(str(folder))
            except (PermissionError, OSError):
                continue
    else:
        # 只检查指定目录的直接子目录
        try:
            for item in base_path.iterdir():
                if item.is_dir() and not any(item.iterdir()):
                    empty_folders.append(str(item))
        except (PermissionError, OSError):
            pass
    
    return empty_folders

@mcp.tool()
async def find_duplicate_files(directory: str = "~/Desktop", recursive: bool = False) -> dict[str, list[str]]:
    """查找重复文件（基于文件内容哈希值）
    
    Args:
        directory: 要检查的目录路径，支持~简写
        recursive: 是否递归检查子目录
    
    Returns:
        重复文件字典：{哈希值: [文件路径列表]}
    """
    import hashlib
    
    base_path = Path(directory).expanduser()
    if not base_path.exists():
        return {}
    
    file_hashes = {}
    
    def get_file_hash(file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError):
            return ""
    
    if recursive:
        # 递归查找所有文件
        for folder_path, subdirs, files in os.walk(base_path):
            folder = Path(folder_path)
            for file_name in files:
                file_path = folder / file_name
                if file_path.is_file():
                    file_hash = get_file_hash(file_path)
                    if file_hash:
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(str(file_path))
    else:
        # 只查找指定目录的直接文件
        try:
            for item in base_path.iterdir():
                if item.is_file():
                    file_hash = get_file_hash(item)
                    if file_hash:
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(str(item))
        except (PermissionError, OSError):
            pass
    
    # 只返回重复的文件（哈希值对应多个文件）
    duplicate_files = {hash_val: paths for hash_val, paths in file_hashes.items() 
                      if len(paths) > 1}
    
    return duplicate_files

@mcp.tool()
async def get_recent_files(
    directory: str = "~/Desktop",
    days: int = 7,
    extension: str = None,
    recursive: bool = False
) -> list[dict[str, any]]:
    """获取最近修改的文件列表
    
    Args:
        directory: 目标目录路径
        days: 最近天数（如7表示最近7天）
        extension: 文件扩展名过滤，None表示所有文件
        recursive: 是否递归子目录
    
    Returns:
        包含文件信息的列表，按修改时间降序排列
    """
    import time
    from datetime import datetime, timedelta
    
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return []
    
    # 计算时间阈值
    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = cutoff_time.timestamp()
    
    if extension:
        pattern = f"**/*.{extension}" if recursive else f"*.{extension}"
    else:
        pattern = "**/*" if recursive else "*"
    
    recent_files = []
    
    for file_path in target_dir.glob(pattern):
        if file_path.is_file():
            try:
                stat = file_path.stat()
                mod_time = stat.st_mtime
                
                if mod_time >= cutoff_timestamp:
                    recent_files.append({
                        "filename": file_path.name,
                        "full_path": str(file_path.absolute()),
                        "relative_path": str(file_path.relative_to(target_dir)),
                        "size_bytes": stat.st_size,
                        "size_formatted": format_file_size(stat.st_size),
                        "modified_time": datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S"),
                        "modified_timestamp": mod_time,
                        "extension": file_path.suffix.lower(),
                        "directory": str(file_path.parent)
                    })
            except (OSError, PermissionError):
                continue
    
    # 按修改时间降序排序
    recent_files.sort(key=lambda x: x["modified_timestamp"], reverse=True)
    return recent_files

@mcp.tool()
async def get_files_by_date_range(
    directory: str = "~/Desktop",
    start_date: str = None,
    end_date: str = None,
    extension: str = None,
    recursive: bool = False
) -> dict[str, any]:
    """按日期范围查询文件
    
    Args:
        directory: 目标目录路径
        start_date: 开始日期（格式：YYYY-MM-DD）
        end_date: 结束日期（格式：YYYY-MM-DD）
        extension: 文件扩展名过滤
        recursive: 是否递归子目录
    
    Returns:
        包含文件列表和统计信息的字典
    """
    import time
    from datetime import datetime
    
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return {"files": [], "total_count": 0, "total_size": 0}
    
    # 解析日期范围
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            start_timestamp = start_dt.replace(hour=0, minute=0, second=0).timestamp()
        else:
            start_timestamp = 0
            
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_timestamp = end_dt.replace(hour=23, minute=59, second=59).timestamp()
        else:
            end_timestamp = datetime.now().timestamp()
    except ValueError:
        return {"error": "日期格式错误，请使用YYYY-MM-DD格式", "files": [], "total_count": 0, "total_size": 0}
    
    if extension:
        pattern = f"**/*.{extension}" if recursive else f"*.{extension}"
    else:
        pattern = "**/*" if recursive else "*"
    
    files_in_range = []
    total_size = 0
    
    for file_path in target_dir.glob(pattern):
        if file_path.is_file():
            try:
                stat = file_path.stat()
                mod_time = stat.st_mtime
                
                if start_timestamp <= mod_time <= end_timestamp:
                    file_info = {
                        "filename": file_path.name,
                        "full_path": str(file_path.absolute()),
                        "relative_path": str(file_path.relative_to(target_dir)),
                        "size_bytes": stat.st_size,
                        "size_formatted": format_file_size(stat.st_size),
                        "modified_time": datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S"),
                        "extension": file_path.suffix.lower()
                    }
                    files_in_range.append(file_info)
                    total_size += stat.st_size
            except (OSError, PermissionError):
                continue
    
    # 按修改时间排序
    files_in_range.sort(key=lambda x: x["modified_time"], reverse=True)
    
    return {
        "files": files_in_range,
        "total_count": len(files_in_range),
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "start_date": start_date or "不限",
        "end_date": end_date or "今天",
        "directory": str(target_dir)
    }

@mcp.tool()
async def get_file_timeline(
    directory: str = "~/Desktop",
    days: int = 30,
    group_by: str = "day",
    recursive: bool = False
) -> dict[str, any]:
    """获取文件时间线视图
    
    Args:
        directory: 目标目录路径
        days: 查看最近多少天的文件
        group_by: 分组方式（"day", "week", "month"）
        recursive: 是否递归子目录
    
    Returns:
        按时间分组的文件统计信息
    """
    import time
    from datetime import datetime, timedelta
    
    target_dir = Path(directory).expanduser()
    if not target_dir.exists():
        return {"timeline": {}, "summary": {}}
    
    # 获取最近指定天数的文件
    recent_files = await get_recent_files(directory, days, None, recursive)
    
    timeline = {}
    
    for file_info in recent_files:
        mod_time = datetime.fromtimestamp(file_info["modified_timestamp"])
        
        if group_by == "day":
            key = mod_time.strftime("%Y-%m-%d")
        elif group_by == "week":
            # 获取周的开始日期（周一）
            week_start = mod_time - timedelta(days=mod_time.weekday())
            key = week_start.strftime("%Y-%m-%d")
        elif group_by == "month":
            key = mod_time.strftime("%Y-%m")
        else:
            key = mod_time.strftime("%Y-%m-%d")
        
        if key not in timeline:
            timeline[key] = {
                "files": [],
                "count": 0,
                "total_size": 0,
                "total_size_formatted": "0 B"
            }
        
        timeline[key]["files"].append(file_info)
        timeline[key]["count"] += 1
        timeline[key]["total_size"] += file_info["size_bytes"]
        timeline[key]["total_size_formatted"] = format_file_size(timeline[key]["total_size"])
    
    # 计算统计摘要
    total_files = len(recent_files)
    total_size = sum(f["size_bytes"] for f in recent_files)
    
    summary = {
        "total_files": total_files,
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "date_range": f"最近{days}天",
        "group_by": group_by,
        "directory": str(target_dir)
    }
    
    return {
        "timeline": timeline,
        "summary": summary
    }



@mcp.tool()
async def rename_file(old_path: str, new_name: str) -> dict[str, any]:
    """重命名文件或文件夹
    
    Args:
        old_path: 原始文件或文件夹路径
        new_name: 新的名称（不包含路径）
    
    Returns:
        操作结果字典
    """
    try:
        old_path = Path(old_path).expanduser().resolve()
        if not old_path.exists():
            return {"success": False, "error": "文件或文件夹不存在"}
        
        # 验证新名称是否包含非法字符
        if any(char in new_name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            return {"success": False, "error": "文件名包含非法字符"}
        
        new_path = old_path.parent / new_name
        
        # 检查目标是否已存在
        if new_path.exists():
            return {"success": False, "error": "目标名称已存在"}
        
        # 执行重命名
        old_path.rename(new_path)
        
        return {
            "success": True,
            "old_path": str(old_path),
            "new_path": str(new_path),
            "type": "file" if new_path.is_file() else "directory"
        }
    
    except PermissionError:
        return {"success": False, "error": "权限不足，无法重命名"}
    except Exception as e:
        return {"success": False, "error": f"重命名失败: {str(e)}"}

@mcp.tool()
async def move_file(source_path: str, target_directory: str) -> dict[str, any]:
    """移动文件或文件夹到指定目录
    
    Args:
        source_path: 源文件或文件夹路径
        target_directory: 目标目录路径
    
    Returns:
        操作结果字典
    """
    try:
        source_path = Path(source_path).expanduser().resolve()
        target_directory = Path(target_directory).expanduser().resolve()
        
        if not source_path.exists():
            return {"success": False, "error": "源文件或文件夹不存在"}
        
        if not target_directory.exists() or not target_directory.is_dir():
            return {"success": False, "error": "目标目录不存在"}
        
        # 检查目标位置是否已存在同名文件
        target_path = target_directory / source_path.name
        if target_path.exists():
            return {"success": False, "error": "目标位置已存在同名文件"}
        
        # 执行移动
        shutil.move(str(source_path), str(target_directory))
        
        return {
            "success": True,
            "source_path": str(source_path),
            "target_path": str(target_path),
            "type": "file" if source_path.is_file() else "directory"
        }
    
    except PermissionError:
        return {"success": False, "error": "权限不足，无法移动"}
    except Exception as e:
        return {"success": False, "error": f"移动失败: {str(e)}"}

@mcp.tool()
async def get_file_info(file_path: str) -> dict[str, any]:
    """获取文件或文件夹的详细信息
    
    Args:
        file_path: 文件或文件夹路径
    
    Returns:
        详细信息字典
    """
    try:
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            return {"success": False, "error": "文件或文件夹不存在"}
        
        stat = path.stat()
        
        info = {
            "success": True,
            "name": path.name,
            "full_path": str(path),
            "parent_directory": str(path.parent),
            "type": "file" if path.is_file() else "directory",
            "size_bytes": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "created_time": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "accessed_time": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            "extension": path.suffix.lower() if path.is_file() else None,
            "is_hidden": path.name.startswith('.')
        }
        
        # 如果是目录，添加子项统计
        if path.is_dir():
            try:
                items = list(path.iterdir())
                info["sub_items_count"] = len(items)
                info["sub_files_count"] = len([i for i in items if i.is_file()])
                info["sub_dirs_count"] = len([i for i in items if i.is_dir()])
            except PermissionError:
                info["sub_items_count"] = 0
                info["sub_files_count"] = 0
                info["sub_dirs_count"] = 0
        
        return info
    
    except Exception as e:
        return {"success": False, "error": f"获取信息失败: {str(e)}"}

@mcp.tool()
async def delete_file(file_path: str, force: bool = False) -> dict[str, any]:
    """删除文件或文件夹（支持递归删除）
    
    安全删除功能，提供多种保护机制：
    1. 路径验证：确保路径存在且可访问
    2. 权限检查：验证删除权限
    3. 递归警告：删除非空目录时给出警告
    4. 操作确认：重要操作需要确认
    
    Args:
        file_path: 要删除的文件或文件夹路径
        force: 强制删除模式，跳过非空目录警告（谨慎使用）
    
    Returns:
        操作结果字典，包含删除详情
    
    Examples:
        delete_file("~/Desktop/test.txt")  # 删除单个文件
        delete_file("~/Desktop/temp_folder")  # 删除空文件夹
        delete_file("~/Desktop/old_project", force=True)  # 强制删除非空文件夹
    """
    try:
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            return {
                "success": False, 
                "error": "文件或文件夹不存在",
                "path": str(path)
            }
        
        # 获取文件/文件夹信息用于返回
        is_directory = path.is_dir()
        original_size = 0
        item_count = 0
        
        if is_directory:
            try:
                # 计算目录大小和文件数量
                for item in path.rglob("*"):
                    if item.is_file():
                        original_size += item.stat().st_size
                        item_count += 1
            except (OSError, PermissionError):
                original_size = 0
                item_count = 0
        else:
            original_size = path.stat().st_size
            item_count = 1
        
        # 检查是否为系统关键目录（额外保护）
        critical_paths = ["/", "/System", "/Library", "/Applications", "/Users", str(Path.home())]
        if str(path) in critical_paths or str(path.parent) == "/":
            return {
                "success": False,
                "error": "不允许删除系统关键目录",
                "path": str(path),
                "suggestion": "请选择具体文件或子目录进行删除"
            }
        
        # 检查目录是否非空
        if is_directory and not force:
            try:
                items = list(path.iterdir())
                if items:
                    return {
                        "success": False,
                        "error": "目录非空，删除可能导致数据丢失",
                        "path": str(path),
                        "item_count": len(items),
                        "suggestion": "使用 force=True 强制删除",
                        "contents": [item.name for item in items[:10]]  # 显示前10个文件
                    }
            except (OSError, PermissionError):
                pass
        
        # 执行删除操作
        if is_directory:
            if force:
                shutil.rmtree(str(path))
            else:
                try:
                    path.rmdir()  # 只能删除空目录
                except OSError as e:
                    return {
                        "success": False,
                        "error": f"目录非空: {str(e)}",
                        "path": str(path),
                        "suggestion": "使用 force=True 强制删除整个目录"
                    }
        else:
            path.unlink()
        
        return {
            "success": True,
            "message": f"{'文件夹' if is_directory else '文件'}删除成功",
            "path": str(path),
            "type": "directory" if is_directory else "file",
            "original_size": original_size,
            "item_count": item_count,
            "space_freed": format_file_size(original_size)
        }
    
    except PermissionError:
        return {
            "success": False,
            "error": "权限不足，无法删除",
            "path": str(path),
            "suggestion": "检查文件权限或使用管理员权限"
        }
    except OSError as e:
        return {
            "success": False,
            "error": f"删除失败: {str(e)}",
            "path": str(path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"未知错误: {str(e)}",
            "path": str(path)
        }

@mcp.tool()
async def safe_delete(file_path: str, backup: bool = False) -> dict[str, any]:
    """安全删除文件（移动到回收站）
    
    提供更安全的数据保护方案：
    1. 支持移动到回收站（macOS）
    2. 可选备份功能
    3. 详细的操作记录
    
    Args:
        file_path: 要删除的文件或文件夹路径
        backup: 是否创建备份
    
    Returns:
        操作结果字典
    """
    try:
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            return {"success": False, "error": "文件或文件夹不存在"}
        
        # 获取文件信息
        original_path = str(path)
        file_name = path.name
        
        # macOS: 移动到废纸篓 (~/.Trash)
        if os.name == 'posix':  # macOS/Linux
            trash_path = Path.home() / ".Trash"
            if not trash_path.exists():
                trash_path = Path.home() / "Trash"  # 备选路径
            
            if backup:
                # 创建备份
                backup_dir = Path.home() / ".file_backup"
                backup_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{file_name}_{timestamp}"
                backup_path = backup_dir / backup_name
                
                if path.is_dir():
                    shutil.copytree(str(path), str(backup_path))
                else:
                    shutil.copy2(str(path), str(backup_path))
            
            # 移动到废纸篓
            target_trash = trash_path / file_name
            counter = 1
            while target_trash.exists():
                target_trash = trash_path / f"{file_name}_{counter}"
                counter += 1
            
            shutil.move(str(path), str(target_trash))
            
            return {
                "success": True,
                "message": "文件已移动到废纸篓",
                "original_path": original_path,
                "trash_path": str(target_trash),
                "backup_created": backup if backup else None,
                "recovery_hint": "可以在废纸篓中恢复文件"
            }
        
        else:
            # 非macOS系统，使用标准删除
            return {
                "success": False,
                "error": "当前系统不支持废纸篓功能",
                "suggestion": "使用 delete_file 进行标准删除"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"安全删除失败: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run()