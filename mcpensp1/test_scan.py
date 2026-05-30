import socket
import time

def scan_ports(start=2000, end=2050):
    found = []
    print(f"🔍 开始扫描端口 {start} 到 {end}...\n")
    
    for port in range(start, end + 1):
        try:
            s = socket.socket()
            s.settimeout(0.05)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                found.append({'port': port, 'path': f'127.0.0.1:{port}'})
                print(f"✅ 发现设备: 端口 {port}")
            s.close()
        except:
            pass
    
    print(f"\n📊 扫描完成！共发现 {len(found)} 个设备\n")
    
    if found:
        print("📋 设备列表：")
        for i, device in enumerate(found, 1):
            print(f"  {i}. 端口 {device['port']} - {device['path']}")
    else:
        print("⚠️ 未发现任何设备")
        print("💡 提示：请确保 eNSP 设备已启动并开启 Telnet 服务")
    
    return found

if __name__ == "__main__":
    print("="*50)
    print("       eNSP MCP 设备扫描工具")
    print("="*50)
    
    devices = scan_ports()
    
    if devices:
        print("\n" + "="*50)
        print("下一步操作建议：")
        print("1. 在浏览器打开 http://localhost:5001")
        print("2. 点击「扫描」按钮")
        print("3. 点击「连接」按钮连接设备")
        print("="*50)
