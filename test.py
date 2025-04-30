import socket
import struct
import threading

def send_message(send_socket, multicast_group, multicast_port):
    """
    向指定的多播组发送消息。
    """
    while True:
        message = input("输入要发送的消息：")
        send_socket.sendto(message.encode('utf-8'), (multicast_group, multicast_port))
        print(f"已发送消息到多播组 {multicast_group}:{multicast_port} -> {message}")

def receive_message(recv_socket, multicast_group):
    """
    接收其他进程发送到多播组的消息（排除自身发送的消息），并打印。
    """
    while True:
        data, addr = recv_socket.recvfrom(1024)
        if addr[0] != socket.gethostbyname(socket.gethostname()):  # 排除自身发送的消息
            print(f"\n收到来自 {addr} 的消息：{data.decode('utf-8')}\n输入要发送的消息：", end="")

def main():
    # 用户输入多播组地址和端口
    multicast_group = input("请输入多播组地址（如 224.0.0.1）：")
    multicast_port = int(input("请输入多播组端口："))

    # 创建发送套接字
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # 创建接收套接字
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 绑定到多播组端口
    recv_socket.bind(('', multicast_port))

    # 加入多播组
    multicast_request = struct.pack(
        "4s4s",
        socket.inet_aton(multicast_group),
        socket.inet_aton('0.0.0.0')  # 本地网络接口
    )
    recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)

    print(f"已加入多播组 {multicast_group}:{multicast_port}，正在接收消息...")

    # 创建线程以同时接收和发送消息
    recv_thread = threading.Thread(target=receive_message, args=(recv_socket, multicast_group))
    send_thread = threading.Thread(target=send_message, args=(send_socket, multicast_group, multicast_port))

    recv_thread.daemon = True
    send_thread.daemon = True

    recv_thread.start()
    send_thread.start()

    recv_thread.join()
    send_thread.join()

if __name__ == "__main__":
    main()
