# 文件统计MCP服务 - 发布版本

## 📁 项目结构

```
files_statistic_release/
├── 📁 核心功能模块
│   ├── mcp_server.py          # MCP服务端（11个工具函数）
│   └── file_stats_agent.py  # 智能助手（Qwen-Agent集成）
├── 📁 测试与验证
│   └── test_client.py         # MCP功能测试
├── 📁 配置与文档
│   ├── requirements.txt       # 核心依赖（fastmcp）
│   ├── README.md             # 主项目文档
│   ├── pyproject.toml        # Python包配置
│   ├── mcp.json              # MCP服务元数据
│   ├── PUBLISH_GUIDE.md      # 发布指南
│   └── README_RELEASE.md     # 发布版本说明
└── 📁 配置
    └── .gitignore            # Git配置
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

#### MCP服务端

```bash
python mcp_server.py
```

#### 智能助手

```bash
python file_stats_agent.py
```

### 3. 测试功能

```bash
python test_client.py
```

## 📋 功能特性

### ✅ 已实现功能
- [x] **文件统计和分析** - 统计文件数量、大小、类型分布
- [x] **安全删除文件** - 双模式删除（直接删除/移动到回收站）
- [x] **时间维度分析** - 按修改时间筛选、时间线视图
- [x] **智能助手交互** - Qwen-Agent自然语言交互
- [x] **MCP协议支持** - 标准MCP工具调用接口
- [x] **跨平台兼容** - Windows/macOS/Linux全支持
- [x] **最小化依赖** - 仅需fastmcp，零配置启动

### 🔧 工具函数（11个）
#### 📊 统计分析类
- `count_files` - 统计目录文件总数
- `list_files` - 列出详细文件信息
- `get_directory_size` - 获取目录总大小（自动格式化）
- `categorize_files_by_extension` - 按扩展名智能分类
- `get_file_stats` - 获取文件详细统计

#### ⏰ 时间维度类
- `get_recent_files` - 获取指定天数内修改的文件
- `get_files_by_date_range` - 按日期范围筛选文件
- `get_file_timeline` - 时间线视图展示文件活动

#### 🗑️ 安全删除类
- `delete_file` - 安全删除文件（带确认和权限检查）
- `safe_delete` - 移动到系统回收站（可恢复）

#### 📁 目录操作类
- `get_directory_structure` - 获取目录树形结构
- `format_file_size` - 智能格式化文件大小

完整工具列表和参数说明详见 `mcp_server.py`

## 🎯 发布平台

- [ ] 魔搭社区
- [ ] 腾讯云MCP广场
- [ ] GitHub发布

## 📞 支持

如有问题，请参考 `PUBLISH_GUIDE.md` 或提交Issue。
