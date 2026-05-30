from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import socket
import time
import os
import json
import datetime
import re
from jinja2 import Template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ensp-mcp'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['INSPECTION_FOLDER'] = 'inspections'
app.config['BASELINE_FOLDER'] = 'baselines'
socketio = SocketIO(app, cors_allowed_origins='*')

devices = {}
device_names = {}
topology_data = {}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['INSPECTION_FOLDER'], exist_ok=True)
os.makedirs(app.config['BASELINE_FOLDER'], exist_ok=True)


class TelnetConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket()
        self.sock.settimeout(1)
        self.sock.connect((self.host, self.port))
        self.sock.send(b'\r\n')
        time.sleep(0.1)
        return True

    def send_cmd(self, cmd):
        try:
            # 发送命令
            self.sock.send(f'{cmd}\r\n'.encode())
            
            # 等待设备处理命令
            time.sleep(0.5)
            
            # 开始接收数据
            response = b''
            start_time = time.time()
            timeout = 30 if 'configuration' in cmd else 8
            
            # 设置合理的接收超时
            self.sock.settimeout(2.0)
            
            while time.time() - start_time < timeout:
                try:
                    data = self.sock.recv(8192)
                    if not data:
                        break
                    response += data
                    # 检查是否收到命令提示符
                    if b'>' in response or b'#' in response:
                        # 等待一下，确保所有数据都已接收
                        time.sleep(0.5)
                        # 尝试再接收一次，确保没有遗漏数据
                        try:
                            more_data = self.sock.recv(8192)
                            if more_data:
                                response += more_data
                        except:
                            pass
                        break
                except socket.timeout:
                    # 超时是正常的，继续尝试接收
                    if response:
                        break
                    continue
                except Exception as e:
                    # 其他错误，中断接收
                    break
            
            # 确保返回至少部分响应
            if not response:
                return 'No response from device'
            
            # 清理响应，只保留命令输出，移除命令回显和命令提示符
            response_str = response.decode('gbk', errors='ignore')
            
            # 检查是否只包含控制字符和空白字符
            if re.match(r'^[\s\x00-\x1F\x7F]*$', response_str):
                return 'No configuration available'
            
            # 检查是否包含错误信息
            if 'Error:' in response_str:
                # 直接返回错误信息，不尝试清理命令
                return response_str
            
            # 移除命令回显，但保留命令输出
            if cmd in response_str:
                # 对于 display version 命令，只移除命令本身，保留所有输出
                if 'display version' in cmd:
                    # 找到命令在响应中的位置
                    cmd_pos = response_str.find(cmd)
                    if cmd_pos >= 0:
                        # 从命令结束位置开始提取输出
                        response_str = response_str[cmd_pos + len(cmd):].strip()
                else:
                    response_str = response_str.replace(cmd, '').strip()
            # 处理命令被设备提示符覆盖的情况（如 [LSW2]isplay current-configuration）
            elif cmd[1:] in response_str:
                # 尝试移除不完整的命令
                response_str = response_str.replace(cmd[1:], '').strip()
            # 处理命令被设备提示符和其他字符覆盖的情况
            else:
                # 检查是否是版本命令的错误情况
                if 'display version' in cmd and 'isplay version' in response_str:
                    # 移除不完整的命令
                    response_str = response_str.replace('isplay version', '').strip()
            
            # 移除最后的命令提示符
            if '>' in response_str:
                response_str = response_str.split('>')[0].strip()
            elif '#' in response_str:
                response_str = response_str.split('#')[0].strip()
            
            # 移除设备名称标记（如 <LSW3>）
            response_str = re.sub(r'<\w+\s*$', '', response_str).strip()
            
            # 清理系统时间格式
            if 'display clock' in cmd:
                # 尝试规范化时间格式
                lines = response_str.split('\n')
                clean_lines = []
                for line in lines:
                    line = line.strip()
                    if line:
                        # 处理时间格式，确保有适当的空格
                        if re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line):
                            # 为星期和时区添加空格
                            line = re.sub(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(\w+)', r'\1 \2', line)
                            line = re.sub(r'(Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(Time Zone)', r'\1 \2', line)
                        clean_lines.append(line)
                response_str = '\n'.join(clean_lines)
            
            return response_str
        except Exception as e:
            return f'Error: {str(e)}'

    def close(self):
        if self.sock:
            self.sock.close()


def scan_ports(start=2000, end=2050):
    found = []
    for port in range(start, end + 1):
        try:
            s = socket.socket()
            s.settimeout(0.05)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                found.append({'port': port, 'path': f'127.0.0.1:{port}'})
            s.close()
        except:
            pass
    return found


def scan_devices(start: int = 2000, end: int = 2050):
    result = scan_ports(start, end)
    for device in result:
        device['name'] = device_names.get(device['path'], device['path'])
    return result


def connect_device(port: int):
    path = f'127.0.0.1:{port}'
    if path in devices:
        return {'success': False, 'error': 'Device already connected'}
    try:
        conn = TelnetConnection('127.0.0.1', port)
        conn.connect()
        devices[path] = conn
        name = device_names.get(path, path)
        return {'success': True, 'port': port, 'path': path, 'name': name}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_command(path: str, command: str):
    if path not in devices:
        return {'success': False, 'error': 'Device not connected'}
    try:
        result = devices[path].send_cmd(command)
        
        # 检查是否是 compare configuration 命令
        if command.strip() == 'compare configuration':
            # 尝试找到最新的巡检文件并追加比对结果
            try:
                device_name = device_names.get(path, path)
                inspection_dir = app.config['INSPECTION_FOLDER']
                
                # 查找该设备的巡检文件
                # 与 inspect_device 函数使用相同的文件名生成逻辑，只替换冒号
                device_pattern = re.escape(path.replace(':', '_'))
                pattern = f'inspection_{device_pattern}_.*\.html'
                
                inspection_files = []
                for filename in os.listdir(inspection_dir):
                    if re.match(pattern, filename):
                        filepath = os.path.join(inspection_dir, filename)
                        mtime = os.path.getmtime(filepath)
                        inspection_files.append((mtime, filepath))
                
                # 按修改时间排序，取最新的
                if inspection_files:
                    inspection_files.sort(reverse=True)
                    latest_inspection = inspection_files[0][1]
                    
                    # 读取现有报告
                    with open(latest_inspection, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 找到 </body> 标签并在其前插入比对结果
                    if '</body>' in content:
                        comparison_section = f'''
        <div class="section">
            <h2>配置比对结果</h2>
            <pre>{result}</pre>
        </div>'''
                        new_content = content.replace('</body>', comparison_section + '\n</body>')
                        
                        # 写回文件
                        with open(latest_inspection, 'w', encoding='utf-8') as f:
                            f.write(new_content)
            except Exception as e:
                # 追加比对结果失败，打印错误信息以便调试
                print(f"追加比对结果失败: {str(e)}")
                # 不影响命令执行
                pass
        
        return {'success': True, 'path': path, 'output': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def disconnect_device(path: str):
    if path not in devices:
        return {'success': False, 'error': 'Device not connected'}
    try:
        devices[path].close()
        del devices[path]
        return {'success': True, 'path': path}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_connected_devices():
    connected = []
    for path in devices:
        port = int(path.split(':')[1])
        connected.append({
            'port': port,
            'path': path,
            'name': device_names.get(path, path)
        })
    return connected


def rename_device(path: str, name: str):
    device_names[path] = name
    return {'success': True, 'path': path, 'name': name}


def get_topology():
    # 尝试从文件加载拓扑数据
    topology_file = os.path.join(app.config['UPLOAD_FOLDER'], 'topology.json')
    if os.path.exists(topology_file):
        try:
            with open(topology_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return topology_data


def save_topology(data):
    global topology_data
    topology_data = data
    # 持久化存储到文件
    topology_file = os.path.join(app.config['UPLOAD_FOLDER'], 'topology.json')
    with open(topology_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {'success': True, 'topology': topology_data}


def inspect_device(path: str):
    if path not in devices:
        return {'success': False, 'error': 'Device not connected'}
    
    try:
        conn = devices[path]
        device_info = {
            'name': device_names.get(path, path),
            'path': path,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 收集设备版本信息
        version_output = conn.send_cmd('display version')
        device_info['version'] = version_output
        time.sleep(0.5)  # 添加等待时间
        
        # 收集系统时间
        clock_output = conn.send_cmd('display clock')
        device_info['clock'] = clock_output
        time.sleep(0.5)  # 添加等待时间
        
        # 收集 VLAN 信息
        vlan_output = conn.send_cmd('display vlan')
        device_info['vlan'] = vlan_output
        time.sleep(0.5)  # 添加等待时间
        
        # 收集路由表信息
        routing_output = conn.send_cmd('display ip routing-table')
        device_info['routing'] = routing_output
        time.sleep(0.5)  # 添加等待时间
        
        # 收集接口信息
        interface_output = conn.send_cmd('display ip interface brief')
        device_info['interfaces'] = interface_output
        time.sleep(0.5)  # 添加等待时间
        
        # 生成 HTML 报告
        html_report = generate_inspection_report(device_info)
        
        # 保存报告文件
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'inspection_{path.replace(":", "_")}_{timestamp}.html'
        filepath = os.path.join(app.config['INSPECTION_FOLDER'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        return {
            'success': True,
            'path': path,
            'report': html_report,
            'filename': filename,
            'filepath': filepath
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def generate_inspection_report(device_info):
    template = Template('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>设备巡检报告 - {{ device.name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; padding: 20px; background: #f8f9fa; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { color: #2c3e50; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #007bff; }
        h2 { color: #34495e; margin: 20px 0 10px; padding-bottom: 5px; border-bottom: 1px solid #dee2e6; }
        .info-box { background: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .info-item { margin: 10px 0; }
        .info-label { font-weight: bold; color: #2c3e50; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 12px; border: 1px solid #dee2e6; }
        .timestamp { color: #6c757d; font-size: 14px; margin-bottom: 20px; }
        .section { margin: 30px 0; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1>设备巡检报告</h1>
        <div class="timestamp">生成时间: {{ device.timestamp }}</div>
        
        <div class="section">
            <h2>基本信息</h2>
            <div class="info-box">
                <div class="info-item"><span class="info-label">设备名称:</span> {{ device.name }}</div>
                <div class="info-item"><span class="info-label">设备路径:</span> {{ device.path }}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>版本信息</h2>
            <pre>{{ device.version }}</pre>
        </div>
        
        <div class="section">
            <h2>系统时间</h2>
            <pre>{{ device.clock }}</pre>
        </div>
        
        <div class="section">
            <h2>VLAN 信息</h2>
            <pre>{{ device.vlan }}</pre>
        </div>
        
        <div class="section">
            <h2>路由表信息</h2>
            <pre>{{ device.routing }}</pre>
        </div>
        
        <div class="section">
            <h2>接口信息</h2>
            <pre>{{ device.interfaces }}</pre>
        </div>
    </div>
</body>
</html>
    ''')
    return template.render(device=device_info)











@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/devices/scan')
def api_scan():
    start = request.args.get('start', 2000, type=int)
    end = request.args.get('end', 2050, type=int)
    result = scan_devices(start, end)
    return jsonify(result)


@app.route('/api/devices/connect', methods=['POST'])
def api_connect():
    data = request.get_json()
    port = data.get('port')
    result = connect_device(port)
    if result['success']:
        socketio.emit('device_connected', {'port': port, 'path': result['path'], 'name': result['name']})
    else:
        socketio.emit('device_error', {'port': port, 'error': result['error']})
    return jsonify(result)


@app.route('/api/devices/command', methods=['POST'])
def api_command():
    data = request.get_json()
    path = data.get('path')
    command = data.get('command')
    result = send_command(path, command)
    if result['success']:
        socketio.emit('device_output', {'path': path, 'output': result['output']})
    else:
        socketio.emit('device_error', {'path': path, 'error': result['error']})
    return jsonify(result)


@app.route('/api/devices/disconnect', methods=['POST'])
def api_disconnect():
    data = request.get_json()
    path = data.get('path')
    result = disconnect_device(path)
    if result['success']:
        socketio.emit('device_disconnected', {'path': path})
    return jsonify(result)


@app.route('/api/devices')
def api_get_devices():
    result = get_connected_devices()
    return jsonify(result)


@app.route('/api/devices/rename', methods=['POST'])
def api_rename():
    data = request.get_json()
    path = data.get('path')
    name = data.get('name')
    result = rename_device(path, name)
    socketio.emit('device_renamed', {'path': path, 'name': name})
    return jsonify(result)


@app.route('/api/topology', methods=['GET'])
def api_get_topology():
    return jsonify(get_topology())


@app.route('/api/topology', methods=['POST'])
def api_save_topology():
    data = request.get_json()
    result = save_topology(data)
    socketio.emit('topology_updated', get_topology())
    return jsonify(result)


@app.route('/api/topology/file', methods=['POST'])
def api_upload_topology_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    try:
        content = file.read()
        if file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
        else:
            data = {'filename': file.filename, 'content': content.decode('utf-8', errors='ignore')}
        result = save_topology(data)
        socketio.emit('topology_updated', get_topology())
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/inspect', methods=['POST'])
def api_inspect():
    data = request.get_json()
    path = data.get('path')
    result = inspect_device(path)
    if result['success']:
        socketio.emit('device_inspected', {
            'path': path,
            'filename': result['filename'],
            'filepath': result['filepath']
        })
    else:
        socketio.emit('device_error', {'path': path, 'error': result['error']})
    return jsonify(result)











@socketio.on('scan')
def on_scan(data):
    start = data.get('start', 2000)
    end = data.get('end', 2050)
    result = scan_devices(start, end)
    emit('scan_result', result)


@socketio.on('get_connected_devices')
def on_get_connected_devices():
    connected = get_connected_devices()
    emit('connected_devices_list', connected)


@socketio.on('connect_device')
def on_connect(data):
    port = data.get('port')
    result = connect_device(port)
    if result['success']:
        emit('device_connected', {'port': port, 'path': result['path'], 'name': result['name']})
    else:
        emit('device_error', {'port': port, 'error': result['error']})


@socketio.on('send_command')
def on_send(data):
    path = data.get('path')
    cmd = data.get('command')
    result = send_command(path, cmd)
    if result['success']:
        emit('device_output', {'path': path, 'output': result['output']})
    else:
        emit('device_error', {'path': path, 'error': result['error']})


@socketio.on('disconnect_device')
def on_disconnect_device(data):
    path = data.get('path')
    result = disconnect_device(path)
    if result['success']:
        emit('device_disconnected', {'path': path})


@socketio.on('rename_device')
def on_rename_device(data):
    path = data.get('path')
    new_name = data.get('name', path)
    result = rename_device(path, new_name)
    emit('device_renamed', {'path': path, 'name': new_name})


@socketio.on('inspect_device')
def on_inspect(data):
    path = data.get('path')
    result = inspect_device(path)
    if result['success']:
        emit('device_inspected', {
            'path': path,
            'filename': result['filename'],
            'filepath': result['filepath']
        })
    else:
        emit('device_error', {'path': path, 'error': result['error']})


@app.route('/api/inspections/list')
def list_inspections():
    inspection_dir = app.config['INSPECTION_FOLDER']
    files = []
    if os.path.exists(inspection_dir):
        for filename in os.listdir(inspection_dir):
            if filename.startswith('inspection_') and filename.endswith('.html'):
                filepath = os.path.join(inspection_dir, filename)
                mtime = os.path.getmtime(filepath)
                size = os.path.getsize(filepath)
                files.append({
                    'filename': filename,
                    'mtime': mtime,
                    'size': size
                })
    # 按时间倒序排列
    files.sort(key=lambda x: x['mtime'], reverse=True)
    return jsonify({'inspections': files})


@app.route('/inspections/<filename>')
def serve_inspection(filename):
    filepath = os.path.join(app.config['INSPECTION_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/inspections/view/<filename>')
def view_inspection(filename):
    filepath = os.path.join(app.config['INSPECTION_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='text/html')
    else:
        return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    print('eNSP Server starting on http://127.0.0.1:5001')
    socketio.run(app, host='0.0.0.0', port=5001)
