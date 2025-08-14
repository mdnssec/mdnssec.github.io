#/usr/bin/python3
#!coding=utf-8

import socket
import time
import pandas as pd
from scapy.all import raw, DNS, DNSQR, Raw
import concurrent.futures
import utils
import csv

def get_service_info_an(sock, target, resp_an, count):
    """
    发送第二阶段DNS-SD请求（基于an ancount），并解析响应。
    """
    service = Raw(load=resp_an)
    req = DNS(id=0x0001, rd=1, qd=service, qdcount=count)
    try:
        sock.sendto(raw(req), target)
        data, _ = sock.recvfrom(10240)
        resp = DNS(data)
        print("Second DNS-SD (from AN):")
        resp.show()
        print("============RESP END===========")
    except (socket.timeout, ConnectionResetError):
        print(f"[{target[0]}] OFFLINE or timeout.")
        return -1
    except Exception as e:
        print(f"An error occurred with {target[0]}: {e}")
        return -1

    magnify = round(len(resp)/len(req),2)
    repeat = {}
    port = 0
    if resp.ancount > 0:
        for i in range(0, resp.ancount):
            rrname = (resp.an[i].rrname).decode()
            if hasattr(resp.an[i], "rdata"):
                rdata  = resp.an[i].rdata
            if hasattr(resp.an[i], "port"):
                port = resp.an[i].port
            if hasattr(resp.an[i], "target"):
                rdata = ("target:" + str(resp.an[i].target))
            repeat[rrname] = rdata
            utils.write_scan_log(target,rrname,rdata,port,resp.an[i].type)

    if resp.arcount > 0:
        for i in range(0, resp.arcount):
            rrname = (resp.ar[i].rrname).decode()
            if hasattr(resp.ar[i], "rdata"):
                rdata  = resp.ar[i].rdata
            if hasattr(resp.ar[i], "port"):
                port = (resp.ar[i].port)
            if hasattr(resp.ar[i], "target"):
                rdata = ("target:" + str(resp.ar[i].target))
            repeat[rrname] = rdata
            utils.write_scan_log(target,rrname,rdata,port)
    utils.get_magnify(target,len(req),len(resp),magnify,"mDNS")
    return magnify,len(resp)

def get_service_info_ar(sock, target, resp_ar, count):
    """
    发送第二阶段DNS-SD请求（基于arcount），并解析响应。
    """
    service = Raw(load=resp_ar)
    req = DNS(id=0x0001, rd=1, qd=service, qdcount=count)
    try:
        sock.sendto(raw(req), target)
        data, _ = sock.recvfrom(10240)
        resp = DNS(data)
    except (socket.timeout, ConnectionResetError):
        print(f"[{target[0]}] OFFLINE or timeout.")
        return -1
    except Exception as e:
        print(f"An error occurred with {target[0]}: {e}")
        return -1
        
    magnify=round(len(resp)/len(req))
    repeat = {}
    port = 0
    if resp.arcount > 0:
        for i in range(0, resp.arcount):
            rrname = (resp.ar[i].rrname).decode()
            if hasattr(resp.ar[i], "rdata"):
                rdata  = resp.ar[i].rdata
            if hasattr(resp.ar[i], "port"):
                port = resp.ar[i].port
            if hasattr(resp.ar[i], "target"):
                rdata = ( "target:" + str(resp.ar[i].target))
            repeat[rrname] = rdata
            utils.write_scan_log(target,rrname,rdata,port,resp.ar[i].type)

    if resp.ancount > 0:
        for i in range(0, resp.ancount):
            rrname = (resp.an[i].rrname).decode()
            if hasattr(resp.an[i], "rdata"):
                rdata  = resp.an[i].rdata
            if hasattr(resp.an[i], "port"):
                port = (resp.an[i].port)
            if hasattr(resp.an[i], "target"):
                rdata = ( "target:" + str(resp.an[i].target))
            repeat[rrname] = rdata
            utils.write_scan_log(target,rrname,rdata,port,resp.an[i].type)
    utils.get_magnify(target,len(req),len(resp),magnify,"DNS-SD")
    return magnify,len(resp)

def dnssd_scan(target_ip, port=5353):
    """
    对单个目标执行聚合模式的DNS-SD扫描。
    """
    target = (target_ip, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    # 阶段一: 查询所有服务
    f_req = DNS(id=0x0001, rd=1, qd=DNSQR(qtype="PTR", qname="_services._dns-sd._udp.local"))
    print("First DNS-SD request:")
    f_req.show()
    try:
        sock.sendto(raw(f_req), target)
        data, _ = sock.recvfrom(10240)
        magnify = round(len(data)/len(f_req),2)
        utils.get_magnify(target,len(f_req),len(data),magnify,"DNS-SD")
    except (socket.timeout, ConnectionResetError):
        print(f"[{target[0]}] OFFLINE or timeout.")
        return -1
    except Exception as e:
        print(f"An error occurred with {target[0]}: {e}")
        return -1

    resp = DNS(data)
    print("First DNS-SD response:")
    resp.show()
    print("============RESP END===========")
    
    an_mag = ar_mag = 0
    an_resp = ar_resp = 0
    an_req = ar_req = 0
    print(f"[{target[0]}] ONLINE")

    # 阶段二: 基于 ancount 的聚合查询
    if resp.ancount > 0:
        print(f"resp.ancount={resp.ancount}")
        dns_payload=b""
        for i in range(0, resp.ancount):
            if hasattr(resp.an[i],"rdata"):
                print("service:", resp.an[i].rdata)
                try:
                    dns_payload+=bytes(DNSQR(qtype=255, qname=resp.an[i].rdata))
                except Exception as e:
                    print(f"Error processing AN record {resp.an[i].rdata}: {e}")
            else:
                print(resp.an[i])
        ret = get_service_info_an(sock, target, dns_payload, resp.ancount)
        if ret != -1:
            an_mag , an_resp = ret
            service = Raw(load=dns_payload)
            an_req = len(DNS(id=0x0001, rd=1, qd=service, qdcount=resp.ancount))
        else:
            return 0
        print("AN round return: ",ret)

    # 阶段三: 基于 arcount 的聚合查询
    if resp.arcount > 0:
        dns_payload=b""
        print(f"resp.arcount={resp.arcount}")
        for i in range(0, resp.arcount):
            if hasattr(resp.ar[i],"rdata"):
                try:
                    dns_payload+=bytes(DNSQR(qtype=255, qname=resp.ar[i].rdata))
                except Exception as e:
                    print(f"Error processing AR record {resp.ar[i].rdata}: {e}")
        ret = get_service_info_ar(sock, target, dns_payload, resp.arcount)
        if ret!=-1:
            ar_mag , ar_resp = ret
            service = Raw(load=dns_payload)
            ar_req = len(DNS(id=0x0001, rd=1, qd=service, qdcount=resp.arcount))
        else:
            return 0
    
    try:
        total_req_len = len(f_req) + an_req + ar_req
        total_resp_len = len(resp) + an_resp + ar_resp
        mdns_mag = total_resp_len / total_req_len if total_req_len > 0 else 0
        print(f"mDNS magnification: {mdns_mag:.2f}")
    except:
        mdns_mag = 0
        
    return [magnify, mdns_mag, (len(resp)+an_resp+ar_resp), (len(f_req)+an_req+ar_req), resp.ancount+resp.arcount]

def separate_send(target_ip, port=5353):
    """
    对单个目标执行分离模式的DNS-SD扫描。
    """
    target = (target_ip, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    magnify = 0
    f_req = DNS(id=0x0001, rd=1, qd=DNSQR(qtype="PTR", qname="_services._dns-sd._udp.local"))
    try:
        sock.sendto(raw(f_req), target)
        data, _ = sock.recvfrom(10240)
        magnify = round(len(data)/len(f_req),2)
        utils.get_magnify(target,len(f_req),len(data),magnify,"DNS-SD")
    except (socket.timeout, ConnectionResetError):
        print(f"[{target[0]}] OFFLINE or timeout.")
        return -1
    except Exception as e:
        print(f"An error occurred with {target[0]}: {e}")
        return -1
        
    resp = DNS(data)
    an_resp = ar_resp = 0
    an_req = ar_req = 1 # Avoid division by zero
    
    time_start=time.perf_counter()
    if resp.ancount > 0:
        print(f"resp.ancount={resp.ancount}")
        for i in range(0, resp.ancount):
            dns_payload=b""
            if hasattr(resp.an[i],"rdata"):
                try:
                    dns_payload=bytes(DNSQR(qtype=255, qname=resp.an[i].rdata))
                except Exception as e:
                    print(f"Error processing AN record {resp.an[i].rdata}: {e}")
                    continue
            else:
                print(resp.an[i])
                continue
            
            ret = get_service_info_an(sock, target, dns_payload, 1)
            service = Raw(load=dns_payload)
            req = DNS(id=0x0001, rd=1, qd=service, qdcount=1)
            
            if ret!=-1:
                mag , res = ret
                an_resp += res
                an_req += len(req)

    if resp.arcount > 0:
        print(f"resp.arcount={resp.arcount}")
        for i in range(0, resp.arcount):
            dns_payload=b""
            if hasattr(resp.ar[i],"rdata"):
                try:
                    dns_payload=bytes(DNSQR(qtype=255, qname=resp.ar[i].rdata))
                except Exception as e:
                    print(f"Error processing AR record {resp.ar[i].rdata}: {e}")
                    continue
            ret = get_service_info_ar(sock, target, dns_payload, 1)
            service = Raw(load=dns_payload)
            req = DNS(id=0x0001, rd=1, qd=service, qdcount=1)
            if ret!=-1:
                mag , res = ret
                ar_resp += res
                ar_req += len(req)
                
    time_end=time.perf_counter()
    time_consumed=time_end-time_start
    
    total_req_len = len(f_req) + an_req + ar_req
    total_resp_len = len(resp) + an_resp + ar_resp
    mdns_mag = total_resp_len / total_req_len if total_req_len > 0 else 0
    
    return [magnify, mdns_mag, total_resp_len, total_req_len, time_consumed, resp.ancount+resp.arcount]

def speed_test(duration, target_ip):
    """
    在指定时间内，对单个IP重复发送扫描包以测试速度。
    """
    start_time = time.time()
    end_time = start_time + duration

    packet_count = 0
    while time.time() < end_time:
        dnssd_scan(target_ip)
        packet_count += 1
    elapsed_time = time.time() - start_time
    print(f"Sent {packet_count} packets in {elapsed_time:.2f} seconds")
    
def magnify_test(excel_file_path):
    """
    测试Excel文件中IP列表的放大倍数。
    """
    df = pd.read_excel(excel_file_path)
    dnssd_max=0
    mdns_max=0
    len_max=0
    
    # 示例：只扫描部分IP
    subset_df = df.head(10) 
    
    for index, row in subset_df.iterrows():
        if index % 100==0:
            print(f"{index} scan finished")
        if row["Port_5353_Status"] == "Open":
            network = row['IP']
            status = dnssd_scan(network)
            if status == -1:
                df.at[index, "Port_5353_Status"] = "Close"
            else:
                if status[0] > dnssd_max:
                    dnssd_max = status[0]
                if status[1] > mdns_max:
                    mdns_max = status[1]
                if status[2] > len_max:
                    len_max = status[2]
    
    print("Scan end")
    print(f"Max DNS-SD magnify: {dnssd_max}")
    print(f"Max mDNS magnify: {mdns_max}")
    df.to_excel(excel_file_path, index=False)

def model_test(df):
    """
    对DataFrame中的IP列表同时进行聚合和分离模式的扫描，并记录结果。
    """
    with open("aggtest.csv","a+", newline='') as wf1, open("septest.csv","a+", newline='') as wf2:
        csv_write1 = csv.writer(wf1)
        csv_write2 = csv.writer(wf2)
        
        # 写入标题行
        header = ["IP", "dnssd_mag", "mdns_mag", "total_resp_len", "total_req_len", "service_count"]
        csv_write1.writerow(header)
        header_sep = header + ["time_consumed"]
        csv_write2.writerow(header_sep)

        networks = df["IP"]
        i=0
        for network in networks:
            agg_status = dnssd_scan(network)
            sep_status = separate_send(network)
            if(agg_status!=-1 and sep_status!=-1):
                agg_status.insert(0,network)
                sep_status.insert(0,network)
                csv_write1.writerow(agg_status)
                csv_write2.writerow(sep_status)
            i+=1
            if i%100==0:
                print(f"{i} scan finished!")
    print("Scan end")

def func(network):
    """
    单次扫描任务，用于多线程测试。
    """
    off = 0
    for i in range(5):
        temp = dnssd_scan(network)
        if temp == -1:
            off += 2
        else:
            if temp == 0 or temp[1] == 0:
                off += 1
    return off

def run_threads(num_threads, ip):
    """
    使用线程池并发执行扫描任务。
    """
    off=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        threads = [executor.submit(func,ip) for _ in range(num_threads)]
        for future in concurrent.futures.as_completed(threads):
            try:
                off += future.result()
            except Exception as e:
                print(f"An error occurred in thread: {e}")
    print(f"Total offline/failed count: {off}")
    return off

def thread_test(num, ip):
    """
    测试不同线程数下的丢包率和发送速度。
    """
    l_rate=[]
    s_speed=[]
    dur_time=[]
    for j in range(1, num):
        start_time = time.perf_counter()
        off = run_threads(j, ip)
        end_time = time.perf_counter()
        duration = round(end_time - start_time, 6)
        print(f"Duration for {j} threads: {duration} seconds")
        
        total_packets = j * 5 * 2
        loss_rate = off / total_packets if total_packets > 0 else 0
        send_speed = (total_packets - off) / duration if duration > 0 else 0
        
        l_rate.append(loss_rate)
        s_speed.append(send_speed)
        dur_time.append(duration)
        
        print(f"Threads: {j}, Loss Rate: {loss_rate:.2%}, Send Speed: {send_speed:.2f} packets/s")
        time.sleep(30)

if __name__ == "__main__":
    # 示例：对单个IP执行一次聚合扫描
    # 稳定开放的IP: "165.242.125.37"
    # 放大倍数很高的IP: "193.117.56.24"
    target_ip = "8.8.8.8" # 使用一个已知的主机进行测试，或者替换为你的目标IP
    print(f"--- Starting Aggregated Scan for {target_ip} ---")
    result = dnssd_scan(target_ip)
    if result != -1 and result != 0:
        print("\n--- Aggregated Scan Summary ---")
        print(f"  Initial DNS-SD Magnification: {result[0]}")
        print(f"  Overall mDNS Magnification: {result[1]:.2f}")
        print(f"  Total Response Length: {result[2]} bytes")
        print(f"  Total Request Length: {result[3]} bytes")
        print(f"  Service Count: {result[4]}")
        print("--------------------------------\n")

    # 示例：对单个IP执行一次分离扫描
    print(f"--- Starting Separated Scan for {target_ip} ---")
    result_sep = separate_send(target_ip)
    if result_sep != -1:
        print("\n--- Separated Scan Summary ---")
        print(f"  Initial DNS-SD Magnification: {result_sep[0]}")
        print(f"  Overall mDNS Magnification: {result_sep[1]:.2f}")
        print(f"  Total Response Length: {result_sep[2]} bytes")
        print(f"  Total Request Length: {result_sep[3]} bytes")
        print(f"  Time Consumed: {result_sep[4]:.4f}s")
        print(f"  Service Count: {result_sep[5]}")
        print("-----------------------------\n")
