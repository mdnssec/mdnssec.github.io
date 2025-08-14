#/usr/bin/python3
#!coding=utf-8

import csv

def write_scan_log(target,rrname,rdata,port= 0,rtype="NA"):
    """将扫描到的服务信息写入CSV文件。"""
    filename = "service.csv"
    with open(filename,"a+", newline='') as wf:
        csv_write = csv.writer(wf)
        data = [target,rrname,rdata,port,rtype]
        csv_write.writerow(data)
        
def get_magnify(target,send,receive,magnify,type):
    """将放大倍数信息写入CSV文件。"""
    filename = "service_magnify.csv"
    with open(filename,"a+", newline='') as wf:
        csv_write = csv.writer(wf)
        data = [target,type,send,receive,magnify]
        csv_write.writerow(data)
