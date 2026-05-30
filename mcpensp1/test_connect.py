import socket
import time
import re

class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
    
    def connect(self):
        self.sock = socket.socket()
        self.sock.settimeout(3)
        self.sock.connect((self.host, self.port))
        self.sock.send(b'\r\n')
        time.sleep(0.5)
        return True
    
    def send_cmd(self, cmd):
        try:
            self.sock.send(f'{cmd}\r\n'.encode())
            time.sleep(0.5)
            response = b''
            start_time = time.time()
            timeout = 3
            
            self.sock.settimeout(0.5)
            while time.time() - start_time < timeout:
                try:
                    data = self.sock.recv(8192)
                    if not data:
                        break
                    response += data
                except socket.timeout:
                    if response:
                        break
                    continue
                except Exception as e:
                    break
            
            return response.decode('gbk', errors='ignore')
        except Exception as e:
            return f'Error: {str(e)}'
    
    def close(self):
        if self.sock:
            self.sock.close()


def get_device_name(conn, port):
    """尝试多种方式获取设备名称"""
    print(f"\n📡 正在连接端口 {port}...")
    
    try:
        # 先发送回车，看提示符
        prompt = conn.send_cmd('')
        time.sleep(0.3)
        
        # 尝试获取系统信息
        info = conn.send_cmd('display version')
        time.sleep(0.5)
        
        # 方法1: 从提示符中提取
        prompt_match = re.search(r'<([A-Za-z0-9_-]+)>', info)
        if prompt_match:
            return prompt_match.group(1)
        
        # 方法2: 从系统信息中提取
        hostname_match = re.search(r'Sysname\s+:\s*([A-Za-z0-9_-]+)', info)
        if hostname_match:
            return hostname_match.group(1)
        
        # 方法3: 尝试其他命令
        hostname_cmd = conn.send_cmd('display current-configuration | include sysname')
        time.sleep(0.3)
        sysname_match = re.search(r'sysname\s+([A-Za-z0-9_-]+)', hostname_cmd)
        if sysname_match:
            return sysname_match.group(1)
        
        # 如果都没找到，尝试查看原始输出
        lines = info.split('\n')
        for line in lines[:20]:
            if any(keyword in line for keyword in ['Quidway', 'HUAWEI', 'Router', 'Switch', 'sysname']):
                return line.strip()
        
        return f"Device_{port}"
    except Exception as e:
        return f"Unknown_{port}"


def scan_devices_info(ports):
    print("="*60)
    print("       eNSP MCP 设备信息扫描工具")
    print("="*60)
    
    devices_info = []
    
    for port in ports:
        try:
            conn = TelnetConnection('127.0.0.1', port)
            conn.connect()
            time.sleep(0.5)
            
            device_name = get_device_name(conn, port)
            
            print(f"✅ 端口 {port}: 设备名 = {device_name}")
            devices_info.append({
                'port': port,
                'address': f'127.0.0.1:{port}',
                'name': device_name
            })
            
            conn.close()
        except Exception as e:
            print(f"❌ 端口 {port}: 连接失败 - {str(e)}")
            devices_info.append({
                'port': port,
                'address': f'127.0.0.1:{port}',
                'name': f"Error_{port}"
            })
        
        time.sleep(0.5)
    
    return devices_info


if __name__ == "__main__":
    # 扫描发现的端口
    ports = [2001, 2002, 2003, 2004, 2007]
    
    devices_info = scan_devices_info(ports)
    
    print("\n" + "="*60)
    print("📋 设备信息汇总:")
    print("="*60)
    
    for device in devices_info:
        print(f"  端口 {device['port']} - {device['address']}")
        print(f"    设备名: {device['name']}")
        print()
    
    print("="*60)
    print("💡 提示：现在可以在 http://localhost:5001 中连接这些设备")
    print("="*60)
