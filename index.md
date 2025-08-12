---
layout: project_page
permalink: /

title: "Exposing Unintended Public mDNS Services at Scale: Measurement, Vulnerability Analysis, and Abuse Potential"
paper: /
code: /
data: /
---

<!-- Using HTML to center the abstract -->
<div class="columns is-centered has-text-centered">
    <div class="column is-four-fifths">
        <h2>Abstract</h2>
        <div class="content has-text-justified">
With the growing ubiquity of smart and portable devices in local networks (LANs), DNS Service Discovery (DNS-SD) over multicast DNS (mDNS) has become essential for zero-configuration connectivity.  
While prior studies have focused on local security risks, the exposure of mDNS services to the broader Internet remains largely unexplored.  In this paper, we present the first large-scale security analysis of Internet-exposed mDNS services.  Our measurements uncover <b>millions of open mDNS services</b> across <b>187 countries</b> that are externally accessible due to misconfigurations and a lack of access control.  A fine-grained investigation reveals that these services span <b>six major categories of internal devices</b>, posing serious risks including remote exploitation and privacy leakage.  Critically, we identify protocol-level vulnerabilities that allow these services to be abused for <b>high-volume reflection-based DDoS attacks</b>, reaching terabit-scale amplification.  To address these threats, we propose and validate a set of <b>practical defenses-optimized configurations</b>, <b>zero-trust access control</b> and a <b>token-based authentication mechanism</b> for mDNS—demonstrating their effectiveness through real-world Internet experiments.
        </div>
    </div>
</div>

---

## Developed Tools

- **mDNS Scanner** – Custom multi-threaded script to identify open mDNS services on UDP port 5353.
- **Service Semantic Enhancer** – Uses LLM + TF-IDF/LDA to classify and describe mDNS service names.
- **Web Snapshot Collector** – Automated system for capturing HTTP/HTTPS pages linked from mDNS records.
- **mDNS Attack Simulator** – Controlled testbed for measuring reflection amplification traffic patterns.
- **Token-based mDNS Auth** – Modified Avahi implementation with authentication & rate-limiting defenses.

Repository & resources: [https://mdnssec.github.io](https://mdnssec.github.io)

---

## Key Findings

- **327,702** unique hosts actively responding via mDNS, **187 countries**.
- **Top countries**: 🇨🇳 China (142,540), 🇺🇸 USA (47,139), 🇰🇷 South Korea (27,023).
- **598 distinct service types** identified.
- **Terabit-scale amplification** possible with coordinated botnet abuse.
- Significant **privacy leaks**: IP/MAC addresses, personal names, emails, geographic locations.

## Simulated mDNS DDoS Attack Traffic

- **Query packet size**: ~167 bytes  
- **Average response size**: ~370 bytes  
- **Mean amplification factor**: **2.22** (max observed **21.0**)  
- **Max per-device response rate**: ~1000 pps (default cap)  
- **Example scenario**:  
  - 1,000 zombies × 70 targets each → **207.2 Gbps** reflected  
  - Global exposure potential → **1.1 Tbps** (default limits) or **3.7 Tbps** (if limits bypassed)

---

## Top 20 Exposed mDNS Services

| Service Name                  | % of Total | Type |
|--------------------------------|------------|------|
| `_http._tcp.local.`            | 15.26%     | HTTP protocol |
| `_workstation._tcp.local.`     | 14.99%     | Workstation discovery |
| `_smb._tcp.local.`             | 11.15%     | SMB protocol |
| `_device-info._tcp.local.`     | 9.89%      | Device info |
| `_afpovertcp._tcp.local.`      | 7.13%      | Apple filing |
| `_spotify-connect._tcp.local.` | 6.74%      | Spotify connect |
| `_ftp._tcp.local.`             | 3.89%      | FTP protocol |
| `_ssh._tcp.local.`             | 3.86%      | SSH protocol |
| `_sftp-ssh._tcp.local.`        | 2.92%      | SSH/SFTP protocol |
| `_qdiscover._tcp.local.`       | 2.07%      | Custom discovery |
| `_webdav._tcp.local.`          | 1.99%      | WebDAV |
| `_webdavs._tcp.local.`         | 1.95%      | WebDAV over HTTPS |
| `_ipp._tcp.local.`             | 1.27%      | Internet printing |
| `_printer._tcp.local.`         | 1.26%      | Local printing |
| `_udisks-ssh._tcp.local.`      | 1.15%      | Remote disk via SSH |
| `_qmobile._tcp.local.`         | 1.00%      | NAS mobile service |
| `_sftp._tcp.local.`            | 0.97%      | SSH file transfer |
| `_https._tcp.local.`           | 0.85%      | HTTPS protocol |
| `_daap._tcp.local.`            | 0.80%      | Digital audio access |
| `_pdl-datastream._tcp.local.`  | 0.77%      | PDL datastream |

---

## Proposed Defenses

1. **Configuration Hardening** – Bind mDNS to local interfaces only.
2. **Firewall ACLs** – Restrict UDP 5353 to trusted sources.
3. **Zero-trust Access Control** – Only authenticated clients allowed.
4. **Token-based Authentication** –  
   - AC token: `SHA256(sip, sport, Pkey, Rkey)`  
   - Added in TXT records; backward compatible.
5. **Rate-limiting** – Enforce RFC 6762 recommendations.

---

## Resources

- **Paper PDF** – *update soon within one week*
- **Dataset & Tools** – [https://mdnssec.github.io](https://mdnssec.github.io)
- **Contact** – *update soon*

---
