#!/bin/bash

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
  echo "请以root权限运行此脚本 (例如: sudo sh open_port.sh)"
  exit
fi

echo "==================================================="
echo "正在检查并配置防火墙以开放端口 3000..."
echo "==================================================="

# 检查 UFW (Uncomplicated Firewall)
if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS=$(ufw status | grep "Status: active")
    if [ -n "$UFW_STATUS" ]; then
        echo "[UFW] 检测到 UFW 防火墙正在运行"
        echo "[UFW] 正在添加 3000/tcp 规则..."
        ufw allow 3000/tcp
        echo "[UFW] 规则已添加"
    else
        echo "[UFW] UFW 已安装但未激活 (Status: inactive)，跳过"
    fi
else
    echo "[UFW] 未检测到 UFW"
fi

echo "---------------------------------------------------"

# 检查 Firewalld (CentOS/RHEL 常用)
if command -v firewall-cmd >/dev/null 2>&1; then
    FIREWALLD_STATUS=$(systemctl is-active firewalld)
    if [ "$FIREWALLD_STATUS" = "active" ]; then
        echo "[Firewalld] 检测到 Firewalld 正在运行"
        echo "[Firewalld] 正在添加 3000/tcp 规则..."
        firewall-cmd --zone=public --add-port=3000/tcp --permanent
        firewall-cmd --reload
        echo "[Firewalld] 规则已添加并重载"
    else
        echo "[Firewalld] Firewalld 已安装但未运行，跳过"
    fi
else
    echo "[Firewalld] 未检测到 Firewalld"
fi

echo "---------------------------------------------------"

# 检查 iptables (如果上述都没有生效，尝试直接添加 iptables 规则)
if command -v iptables >/dev/null 2>&1; then
    # 检查是否已有规则
    IPTABLES_CHECK=$(iptables -L INPUT -n | grep "dpt:3000")
    if [ -z "$IPTABLES_CHECK" ]; then
        echo "[iptables] 未检测到 3000 端口规则，正在尝试添加..."
        # 尝试添加到 INPUT 链
        iptables -I INPUT -p tcp --dport 3000 -j ACCEPT
        echo "[iptables] 规则已临时添加 (重启后可能失效)"
        echo "[iptables] 建议使用 ufw 或 firewalld 管理规则"
    else
        echo "[iptables] 检测到 iptables 中已存在 3000 端口规则"
    fi
else
    echo "[iptables] 未检测到 iptables"
fi

echo "==================================================="
echo "               !!! 重要提示 !!!                    "
echo "==================================================="
echo "如果您的服务器是云服务器 (如阿里云, 腾讯云, AWS, RainYun等)"
echo "您必须去云服务商的【网页控制台】->【安全组 / 防火墙】中"
echo "手动添加入站规则，放行 TCP 协议的 3000 端口。"
echo ""
echo "仅仅在服务器内部开放端口是不够的！云厂商的安全组在服务器外部拦截流量。"
echo "==================================================="
