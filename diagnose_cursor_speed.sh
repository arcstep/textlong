#!/bin/bash

echo "=========================================="
echo "Cursor AI 速度诊断工具"
echo "=========================================="
echo ""

echo "【1. 基本网络连接测试】"
echo "----------------------------------------"
echo -n "测试基本网络连通性 (ping 8.8.8.8): "
ping -c 3 -W 2 8.8.8.8 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ 正常"
    ping -c 3 8.8.8.8 | tail -1
else
    echo "✗ 异常"
fi
echo ""

echo "【2. DNS 解析速度测试】"
echo "----------------------------------------"
echo -n "Google DNS (8.8.8.8): "
time nslookup google.com 8.8.8.8 > /dev/null 2>&1
echo -n "Cloudflare DNS (1.1.1.1): "
time nslookup google.com 1.1.1.1 > /dev/null 2>&1
echo ""

echo "【3. HTTPS 连接速度测试】"
echo "----------------------------------------"
echo "测试 Google:"
curl -o /dev/null -s -w "  DNS解析: %{time_namelookup}s | 连接: %{time_connect}s | SSL握手: %{time_appconnect}s | 总时间: %{time_total}s\n" https://www.google.com

echo "测试 OpenAI API:"
curl -o /dev/null -s -w "  DNS解析: %{time_namelookup}s | 连接: %{time_connect}s | SSL握手: %{time_appconnect}s | 总时间: %{time_total}s\n" https://api.openai.com

echo "测试 GitHub:"
curl -o /dev/null -s -w "  DNS解析: %{time_namelookup}s | 连接: %{time_connect}s | SSL握手: %{time_appconnect}s | 总时间: %{time_total}s\n" https://github.com
echo ""

echo "【4. Cursor 相关域名测试】"
echo "----------------------------------------"
for domain in "cursor.sh" "www.cursor.sh" "api.cursor.sh" "app.cursor.sh"; do
    echo -n "测试 $domain: "
    if nslookup $domain > /dev/null 2>&1; then
        echo "✓ 可解析"
        curl -o /dev/null -s -w "  连接时间: %{time_total}s\n" "https://$domain" 2>&1 | head -1
    else
        echo "✗ 无法解析"
    fi
done
echo ""

echo "【5. 系统信息】"
echo "----------------------------------------"
echo "操作系统: $(uname -a)"
echo "DNS 服务器: $(grep nameserver /etc/resolv.conf 2>/dev/null | head -1 || echo '无法获取')"
echo "代理设置: $(env | grep -i proxy || echo '无')"
echo ""

echo "【6. 网络延迟统计】"
echo "----------------------------------------"
echo "测试多个目标服务器的延迟:"
for host in "8.8.8.8" "1.1.1.1" "github.com" "api.openai.com"; do
    echo -n "  $host: "
    ping -c 3 -W 2 $host 2>/dev/null | tail -1 | awk -F'/' '{print "平均延迟: "$5"ms"}'
done
echo ""

echo "=========================================="
echo "诊断完成！"
echo ""
echo "【判断建议】"
echo "1. 如果基本网络连接正常，但 Cursor 慢 → 可能是 Cursor 服务器负载问题"
echo "2. 如果所有 HTTPS 连接都慢 → 可能是网络问题或代理设置问题"
echo "3. 如果 DNS 解析慢 → 可能是 DNS 服务器问题"
echo "=========================================="
