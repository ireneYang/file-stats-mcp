# 文件统计MCP服务

一个基于MCP协议的文件统计与分析工具，提供11个核心工具函数，支持文件统计、分类、时间线分析等功能。

## 🚀 服务配置

- **服务名称**: file-stats-mcp
- **版本**: 2.3.0
- **协议**: MCP (Model Context Protocol)
- **运行方式**: `python mcp_server.py`
- **依赖**: fastmcp>=0.4.1

## 📋 功能特性

### 核心工具函数（11个）

#### 📊 统计分析类
- **count_files** - 统计指定类型文件数量
- **list_files** - 列出详细文件信息
- **get_directory_size** - 计算目录总大小
- **categorize_files_by_extension** - 按扩展名智能分类
- **get_file_info** - 获取文件详细信息

#### ⏰ 时间维度类
- **get_recent_files** - 获取最近修改的文件
- **get_file_timeline** - 时间线视图展示文件活动

#### 🗑️ 安全删除类
- **delete_file** - 安全删除文件（带确认和权限检查）
- **safe_delete** - 移动到系统回收站

#### 📁 目录操作类
- **rename_file** - 文件重命名
- **move_file** - 文件移动操作

### 服务优势
- ✅ 跨平台支持（Windows/macOS/Linux）
- ✅ 最小化依赖（仅需fastmcp）
- ✅ 标准MCP协议兼容
- ✅ 中文界面友好

## 🔧 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python mcp_server.py
```

### 3. 测试功能
```bash
python test_client.py
```

## 📁 项目结构

```
file-stats-mcp/
├── mcp_server.py      # MCP服务端主程序
├── mcp.json          # MCP服务配置
├── requirements.txt  # 依赖列表
├── README.md         # 项目文档
└── test_client.py    # 测试客户端
```

## 📞 支持

如有问题，请参考项目文档或提交Issue。
