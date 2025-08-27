📡 Cisco Router Monitoring Suite

🚀 Overview
This project is a multi-component Cisco router monitoring system developed as part of a networking assignment. It leverages SNMP, Python, Flask, and Discord integrations to provide real-time insights into router performance and interface statuses.

The suite includes:

Flask-based SNMP Monitoring Dashboard

SNMP Metrics Exporter for Prometheus

Discord Webhook Alert System

Comprehensive Router Monitoring Script (Ping + SNMP + Port Scan)

🧩 Features
🔍 Flask SNMP Dashboard
Displays live SNMP data from Cisco routers in GNS3

Shows hostname, uptime, CPU, memory usage, and interface status

Easily extendable with more OIDs and SNMP metrics

Built with Flask and follows Prometheus data structure

🚨 Discord Interface Alert Script
Continuously monitors interface status via SNMP

Sends real-time alerts when an interface goes UP/DOWN

Uses Discord Webhook integration

🧪 SNMP + Ping + Port Monitoring Script
Retrieves hostname, domain, uptime, and hardware stats

Checks reachability via ping

Scans for open ports (SSH, Telnet, HTTP, HTTPS) using Nmap

⚙️ Technologies Used
Python 3

SNMP (snmpwalk/snmpget)

Flask

Nmap

Discord Webhooks

GNS3 Virtual Routers

ping3, netmiko, nmap, subprocess, requests libraries
🔒 Security Considerations
Add basic authentication or IP whitelisting for Flask dashboard

Rotate SNMP community strings periodically

Implement SNMP timeout and retry mechanisms

Log errors and alerts for auditing
