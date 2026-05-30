# 🌐 Network Inspection Tool

> 基于 Web 的 eNSP 设备管理与巡检平台 | 支持 MCP 协议 | 自动化运维

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)](https://flask.palletsprojects.com/)

---

## 📖 项目简介

**Network Inspection Tool** 是一款专为 **eNSP（Enterprise Network Simulation Platform）** 设计的智能化网络设备管理工具。通过 Web 界面即可实现设备的扫描发现、远程连接、配置管理、自动巡检和配置比对，大幅提升网络工程师的学习和工作效率。

### ✨ 核心优势

- 🚀 **开箱即用**：无需复杂配置，一键启动即可使用
- 🎨 **直观易用**：现代化 Web 界面，操作简洁明了
- 🤖 **AI 集成**：支持 MCP 协议，可与 AI 助手无缝对接
- ⚡ **高效巡检**：一键生成完整的设备巡检报告
- 🔄 **实时响应**：Socket.IO 实现毫秒级命令响应
- 📊 **历史追溯**：完整保存巡检历史，支持随时查阅

---

## 🎯 核心功能

### 1️⃣ 智能设备管理
- ✅ **自动扫描**：一键扫描 2000-2050 端口范围，自动发现所有 eNSP 设备
- ✅ **多设备连接**：支持同时连接多个设备，标签页切换操作
- ✅ **设备重命名**：为设备设置友好的别名（LSW1、R1、SW2 等）
- ✅ **状态监控**：实时显示设备连接状态和在线情况

### 2️⃣ 终端操作中心
- ✅ **命令执行**：在设备上执行任意命令，实时获取输出
- ✅ **快捷命令**：一键执行常用命令（版本、时间、VLAN、接口、路由、配置、比对）
- ✅ **命令历史**：保存历史命令记录，方便回溯
- ✅ **批量操作**：支持多设备同时执行相同命令

### 3️⃣ 自动化巡检
**一键生成完整巡检报告，包含：**
- 📋 **设备版本信息**：`display version`
- 🕐 **系统时间**：`display clock`
- 🌐 **VLAN 配置**：`display vlan`
- 🔀 **路由表**：`display ip routing-table`
- 📊 **接口状态**：`display ip interface brief`
- ⚙️ **当前配置**：`display saved-configuration`

**巡检报告特性：**
- 📄 HTML 格式，浏览器直接查看
- 📅 自动归档，支持历史查询
- 📥 一键下载，便于分享存档

### 4️⃣ 配置比对
- ✅ **配置差异分析**：快速发现配置变更
- ✅ **历史版本对比**：与历史配置进行比对
- ✅ **变更记录**：完整记录所有配置变更
- ✅ **异常检测**：及时发现异常配置

### 5️⃣ MCP 协议支持
通过 Model Context Protocol 与 AI 助手集成：
```python
# 可用的 MCP 工具
- scan_devices        # 扫描设备
- connect_device      # 连接设备
- send_command       # 发送命令
- disconnect_device   # 断开连接
- get_connected_devices  # 获取已连接设备
- rename_device       # 重命名设备
- get_topology        # 获取拓扑
- save_topology       # 保存拓扑
```

### 6️⃣ 拓扑可视化
- 📤 **拓扑上传**：支持 JSON 和 TXT 格式
- 📊 **可视化展示**：自动生成设备拓扑图
- 🔗 **连接关系**：清晰展示设备间连接

---

## 🛠️ 技术架构

### 技术栈
| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | HTML5 + CSS3 + JavaScript | 响应式 Web 界面 |
| **通信** | Socket.IO | 实时双向通信 |
| **后端** | Python Flask | 轻量级 Web 框架 |
| **异步** | Flask-SocketIO + Eventlet | 高性能异步处理 |
| **协议** | Telnet | 设备通信协议 |
| **集成** | MCP | AI 助手协议支持 |

### 系统要求
- 🐍 Python 3.7+
- 🌐 现代浏览器（Chrome、Firefox、Edge、Safari）
- 💻 Windows/Linux/macOS
- 🔌 eNSP 模拟器（已启动设备）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/zhen237/Network-Inspection-Tool-2.git
cd Network-Inspection-Tool-2

# 安装 Python 依赖
cd mcpensp1
pip install flask flask-socketio eventlet
```

### 2. 启动服务

```bash
# 启动主服务器
python app.py

# 服务运行在 http://localhost:5001
```

### 3. 开始使用

1. 🌐 打开浏览器访问：`http://localhost:5001`
2. 🔍 点击「扫描」按钮，发现 eNSP 设备
3. 🔌 点击「连接」按钮，连接目标设备
4. 💻 在终端中执行命令或使用快捷按钮
5. 📋 点击「巡检」按钮，一键生成巡检报告

---

## 📖 使用指南

### 扫描设备

```
1. 设置端口范围（默认 2000-2050）
2. 点击「扫描」按钮
3. 等待扫描完成
4. 设备列表自动更新
```

### 连接设备

```
1. 从设备列表选择目标设备
2. 点击「连接」按钮
3. 右侧打开终端标签页
4. 开始执行命令
```

### 生成巡检报告

```
1. 确保设备已连接
2. 点击「巡检」按钮
3. 等待巡检完成（通常 10-30 秒）
4. 点击日志区域的报告链接查看
```

### 使用快捷命令

```
支持的快捷命令：
📱 版本 - display version
🕐 时间 - display clock
🌐 VLAN - display vlan
📊 接口 - display ip interface brief
🔀 路由 - display ip routing-table
⚙️ 配置 - display saved-configuration
🔍 比对 - compare configuration
```

---

## 📁 项目结构

```
Network-Inspection-Tool-2/
│
├── mcpensp1/                    # 主应用目录
│   ├── app.py                   # Flask 主应用
│   ├── mcp_server.py            # MCP 服务器
│   ├── mcp.json                 # MCP 配置
│   ├── requirements.txt         # Python 依赖
│   │
│   ├── templates/               # 前端模板
│   │   └── index.html          # Web 界面
│   │
│   ├── uploads/                 # 上传文件目录
│   │   └── topology.json       # 拓扑文件
│   │
│   ├── inspections/             # 巡检报告目录
│   │   ├── inspection_*.html   # 巡检报告
│   │   └── comparison_*.html    # 比对报告
│   │
│   └── baselines/               # 基线配置目录
│       └── baseline_*.cfg       # 基线配置文件
│
├── README.md                    # 项目说明文档
└── 实验报告.md                  # 实验报告
```

---

## 👥 团队分工

| 成员 | 职责 | 贡献内容 |
|------|------|----------|
| **组长** | 项目架构设计与核心开发 | Flask 应用架构、Socket.IO 集成、Telnet 通信 |
| **组员1** | 前端开发与 UI 设计 | Web 界面、交互设计、样式优化 |
| **组员2** | MCP 集成与 AI 对接 | MCP 协议实现、工具定义、API 对接 |
| **组员3** | 巡检功能开发 | 巡检逻辑、报告生成、数据解析 |
| **组员4** | 测试与文档 | 功能测试、用户文档、故障排查 |
| **组员5** | 配置比对与优化 | 配置比对算法、性能优化 |

---

## 🎨 功能截图预览

```
┌─────────────────────────────────────────────┐
│  🌐 Network Inspection Tool    [扫描] [历史报告] │
├──────────────┬──────────────────────────────┤
│              │                              │
│  📡 设备列表  │     💻 终端操作面板           │
│              │                              │
│  LSW1 [连接] │  ┌──────────────────────┐  │
│  LSW3 [连接] │  │ display version       │  │
│  R1   [连接] │  │                      │  │
│  SW2  [连接] │  │ Huawei Versatile...   │  │
│              │  │                      │  │
│              │  └──────────────────────┘  │
│              │                              │
│              │  [版本] [时间] [VLAN] [路由]  │
├──────────────┴──────────────────────────────┤
│  📋 日志: 巡检完成 | 报告已生成 | 3.2MB      │
└─────────────────────────────────────────────┘
```

---

## ❓ 常见问题

### Q1: 无法连接设备？
- ✅ 检查 eNSP 设备是否已启动
- ✅ 确认 Telnet 服务已开启
- ✅ 验证端口号是否正确

### Q2: 巡检报告生成失败？
- ✅ 确保设备连接正常
- ✅ 检查磁盘空间是否充足
- ✅ 查看日志区域错误信息

### Q3: MCP 工具无法使用？
- ✅ 确认 mcp.json 配置正确
- ✅ 检查端口号是否匹配（5001）
- ✅ 重启 MCP 服务器

### Q4: 命令执行无响应？
- ✅ 等待命令完成（配置命令可能需要 10+ 秒）
- ✅ 检查网络连接状态
- ✅ 尝试重新连接设备

---

## 🔧 故障排查

### 查看日志
```bash
# 启动调试模式
python app.py --debug
```

### 检查端口占用
```bash
netstat -ano | findstr 5001
```

### 重启服务
```bash
# 停止服务 (Ctrl+C)
# 重新启动
python app.py
```

---

## 📚 参考资源

- [Flask 文档](https://flask.palletsprojects.com/)
- [Socket.IO 文档](https://socket.io/)
- [eNSP 官方文档](https://forum.huawei.com/)
- [MCP 协议规范](https://modelcontextprotocol.io/)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. 🍴 Fork 本仓库
2. 🔨 创建新分支 (`git checkout -b feature/AmazingFeature`)
3. 💾 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送到分支 (`git push origin feature/AmazingFeature`)
5. 🔃 创建 Pull Request

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 详见 LICENSE 文件

---

## 📧 联系我们

- 🐛 Bug 报告：[GitHub Issues](https://github.com/zhen237/Network-Inspection-Tool-2/issues)
- 💡 功能建议：[GitHub Discussions](https://github.com/zhen237/Network-Inspection-Tool-2/discussions)
- 📧 邮箱：zhen@example.com

---

<p align="center">
  <strong>如果这个项目对你有帮助，请给我们一个 ⭐！</strong>
</p>
