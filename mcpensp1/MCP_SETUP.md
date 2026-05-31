# MCP 服务器配置说明

## 方式1：使用启动脚本（推荐）

1. 将此文件夹整个移动到新位置
2. 更新你的 MCP 配置文件（通常在用户目录下，如 `%APPDATA%\Cursor\mcp.json` 或类似位置）
3. 配置示例：

```json
{
  "mcpServers": {
    "ensp": {
      "command": "cmd",
      "args": [
        "/c",
        "你的新路径\\start_mcp.bat"
      ],
      "env": {},
      "description": "eNSP Device MCP Server"
    }
  }
}
```

## 方式2：使用 Python 模块方式

将 mcp_server.py 所在目录添加到 PYTHONPATH，然后：

```json
{
  "mcpServers": {
    "ensp": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server"
      ],
      "env": {
        "PYTHONPATH": "你的项目路径"
      }
    }
  }
}
```

## 注意事项

- 移动文件夹时，请保持 `app.py` 和 `mcp_server.py` 在同一目录
- 确保 `templates/`、`uploads/`、`inspections/` 文件夹也一起移动
- 启动 app.py 后再启动 MCP 服务器
