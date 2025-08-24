"""文件统计智能助手 - 基于Qwen-Agent + MCP实现

这个模块提供了一个智能文件统计助手，可以通过自然语言进行文件分析和管理：
1. 统计目录文件数量和大小
2. 按类型分类文件
3. 查找大文件和重复文件
4. 管理最近修改的文件
5. 文件重命名等操作
"""

import os
import asyncio
from typing import Optional
import dashscope
from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置 DashScope
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
print(dashscope.api_key)
dashscope.timeout = 60  # 延长超时时间以处理大目录

def init_file_stats_agent():
    """初始化文件统计智能助手
    
    配置说明：
    - 使用 qwen-max 作为底层语言模型
    - 设置系统角色为文件管理专家
    - 集成文件统计MCP工具
    
    Returns:
        Assistant: 配置好的文件统计助手实例
    """
    # LLM 模型配置
    llm_cfg = {
        'model': 'qwen-max',
        'timeout': 60,
        'retry_count': 3,
    }
    
    # 系统角色设定 - 文件管理专家
    system = """你是一个专业的文件管理助手，具备强大的文件分析和统计能力。

核心能力：
1. 文件统计：统计目录中的文件数量、总大小、平均大小等
2. 文件分类：按文件类型（扩展名）自动分类整理
3. 大文件检测：快速找出占用空间最多的文件
4. 重复文件清理：基于内容哈希值查找重复文件
5. 时间管理：分析最近修改的文件，提供时间线视图
6. 文件操作：支持文件重命名等基础操作

使用规范：
- 始终使用绝对路径处理文件
- 对于大目录操作，主动提醒用户可能耗时较长
- 提供清晰的统计结果，包括数字和格式化大小
- 发现异常（如大文件、重复文件）时给出优化建议
- 支持递归和非递归两种模式

交互风格：
- 用简洁易懂的语言解释复杂的文件统计信息
- 主动发现潜在问题并提供解决方案
- 支持自然语言查询，理解用户的真实意图

示例响应格式：
"📊 目录统计结果：
- 总文件数：1,234个
- 总大小：15.7 GB
- 最大文件：video.mp4 (2.3 GB)
- 建议：发现3个重复文件，可节省500MB空间"
"""

    # MCP工具配置 - 连接文件统计服务器
    tools = [{
        "type": "mcp",
        "mcpServers": {
            "file-stats": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio"
            }
        }
    }]
    
    try:
        # 创建文件统计助手实例
        agent = Assistant(
            llm=llm_cfg,
            name='文件统计智能助手',
            description='智能文件分析与管理专家',
            system_message=system,
            function_list=tools,
        )
        print("文件统计智能助手初始化成功！")
        return agent
    except Exception as e:
        print(f"文件统计助手初始化失败: {str(e)}")
        raise

def run_test_mode(query: str = "统计当前目录的文件情况"):
    """测试模式 - 快速验证功能
    
    Args:
        query: 测试查询语句
    """
    try:
        agent = init_file_stats_agent()
        messages = [{'role': 'user', 'content': query}]
        
        print("🧪 测试模式启动...")
        print(f"查询: {query}")
        print("-" * 50)
        
        for response in agent.run(messages):
            print('🤖 助手回复:', response)
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def run_tui_mode():
    """终端交互模式
    
    提供命令行交互界面，支持：
    - 连续对话
    - 智能提示
    - 实时文件分析
    """
    try:
        agent = init_file_stats_agent()
        messages = []
        
        print("🚀 文件统计智能助手 - 终端模式")
        print("支持的查询示例：")
        print("• 统计桌面目录的文件情况")
        print("• 按类型分类显示文档目录的文件")
        print("• 找出下载目录超过500MB的大文件")
        print("• 显示最近7天修改过的文件")
        print("• 检查图片目录有没有重复文件")
        print("• 把test.txt重命名为new_test.txt")
        print("• 退出/quit - 退出程序")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n👤 请输入查询: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['退出', 'quit', 'exit']:
                    print("👋 感谢使用，再见！")
                    break
                
                messages.append({'role': 'user', 'content': query})
                
                print("\n🤖 正在分析...")
                for response in agent.run(messages):
                    print(f"回复: {response}")
                    messages.extend(response)
                    
            except KeyboardInterrupt:
                print("\n👋 程序已终止")
                break
            except Exception as e:
                print(f"❌ 处理出错: {str(e)}")
                
    except Exception as e:
        print(f"❌ 启动终端模式失败: {str(e)}")

def run_gui_mode():
    """图形界面模式 - Web GUI
    
    提供专业的Web界面，特点：
    - 友好的用户界面
    - 智能查询建议
    - 实时文件分析结果
    - 支持历史对话
    """
    try:
        agent = init_file_stats_agent()
        
        # 智能查询建议配置
        chatbot_config = {
            'prompt.suggestions': [
                '统计当前目录的文件总数和总大小',
                '按扩展名分类显示桌面目录的所有文件',
                '找出下载目录中超过100MB的大文件',
                '显示最近7天内修改过的所有文件',
                '检查文档目录是否有重复文件',
                '清理桌面目录的空文件夹',
                '显示最近30天的文件时间线',
                '统计2024-01-01到2024-12-31创建的文件',
                '重命名文件 old_name.txt 为 new_name.txt',
                '分析用户目录的磁盘空间使用情况',
                '按周统计最近一个月的文件创建情况',
                '查找并列出所有图片文件（jpg, png, gif）',
                '统计代码目录中不同编程语言的文件数量',
                '分析大文件并提供清理建议',
                '创建最近修改文件的详细报告'
            ]
        }
        
        print("🌐 启动文件统计智能助手 Web界面...")
        print("访问地址: http://localhost:8001")
        
        WebUI(
            agent,
            chatbot_config=chatbot_config
        ).run(port=8001)
        
    except Exception as e:
        print(f"❌ 启动Web界面失败: {str(e)}")
        print("请检查：")
        print("1. DashScope API Key是否配置正确")
        print("2. 端口8001是否被占用")
        print("3. 网络连接是否正常")

if __name__ == '__main__':
    # 运行模式选择
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'test':
            run_test_mode()
        elif mode == 'tui':
            run_tui_mode()
        elif mode == 'gui':
            run_gui_mode()
        else:
            print("使用方式:")
            print("python file_stats_agent.py test  # 测试模式")
            print("python file_stats_agent.py tui   # 终端模式")
            print("python file_stats_agent.py gui   # Web界面模式")
            print("python file_stats_agent.py       # 默认Web界面模式")
    else:
        # 默认启动Web界面
        run_gui_mode()