#!/bin/bash
# 自動黑名單監控和更新系統

BLACKLIST_DIR="/etc/firewall/blacklist"
BLACKLIST_FILE="$BLACKLIST_DIR/ssh_attackers.txt"
LOG_FILE="/var/log/blacklist_monitor.log"
TEMP_FILE="/tmp/new_attackers.txt"

# 確保目錄存在
sudo mkdir -p $BLACKLIST_DIR

# 記錄開始時間
echo "$(date): 開始黑名單監控" | sudo tee -a $LOG_FILE

# 查找新的重複攻擊者 (攻擊次數 > 5)
sudo grep 'invalid user' /var/log/auth.log | grep -v 'sudo.*grep' | \
grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | \
sort | uniq -c | sort -nr | \
awk '$1 > 5 {print $2}' > $TEMP_FILE

# 比較現有黑名單，找出新的攻擊者
if [ -f $BLACKLIST_FILE ]; then
    NEW_IPS=$(comm -23 <(sort $TEMP_FILE) <(sort $BLACKLIST_FILE))
else
    NEW_IPS=$(cat $TEMP_FILE)
fi

# 如果有新的攻擊者，添加到黑名單
if [ -n "$NEW_IPS" ]; then
    echo "$NEW_IPS" | while IFS= read -r ip; do
        if [ -n "$ip" ]; then
            # 添加到黑名單文件
            echo "$ip" | sudo tee -a $BLACKLIST_FILE
            # 添加防火牆規則
            sudo iptables -I INPUT -s $ip -j DROP
            sudo ufw deny from $ip
            echo "$(date): 新增黑名單 IP: $ip" | sudo tee -a $LOG_FILE
        fi
    done
    # 保存規則
    sudo netfilter-persistent save
    echo "$(date): 黑名單已更新" | sudo tee -a $LOG_FILE
else
    echo "$(date): 無新的攻擊者" | sudo tee -a $LOG_FILE
fi

# 清理臨時文件
rm -f $TEMP_FILE

