
# Attack Simulator Module

## Directory Structure

```
├── attack_simulator/
│   ├── packet_gen.py # Generates mDNS query packets (pcap files) targeting a specified IP address.
│   ├── replay.sh # Replays mDNS query traffic in batches and collects statistics.
│   ├── `output/` # Stores generated pcap files and logs.
│   └── README.md # This file.
```

## How to use

### 1. Generate mDNS Query Packets

```bash
python3 packet_gen.py <target_ip> <victim_ip> <output_pcap>
```

* `<target_ip>`: The IP address of the target device.
* `<victim_ip>`: The spoofed source IP address.
* `<output_pcap>`: The output pcap file path.

### 2. Batch Replay and Statistics

Edit `replay.sh` to fill in your network interface, source IP, target IP list, and other parameters.

Run:

```bash
bash replay.sh
```

The script will automatically generate packets for each target, replay them, capture traffic, and collect statistics. Logs are saved in the `output/` directory.

## Dependencies

* Python 3
* scapy
* tcpreplay
* tcpdump
* tcprewrite
* bc

## Notes

* Root privileges are required to run replay and packet capture commands.
* Ensure that the network interface, IP addresses, and other parameters are correctly configured.

