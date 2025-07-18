#\!/bin/bash
# IP 黑名單管理工具

BLACKLIST_FILE="/etc/firewall/blacklist/ssh_attackers.txt"
LOG_FILE="/var/log/blacklist_monitor.log"

case $1 in
    "list")
        echo "📋 當前黑名單 IP 地址："
        if [ -f $BLACKLIST_FILE ]; then
            cat $BLACKLIST_FILE | nl
            echo ""
            echo "📊 總計: $(wc -l < $BLACKLIST_FILE) 個 IP"
        else
            echo "黑名單文件不存在"
        fi
        ;;
    "add")
        if [ -z "$2" ]; then
            echo "用法: $0 add <IP地址>"
            exit 1
        fi
        IP=$2
        echo "$IP" | sudo tee -a $BLACKLIST_FILE
        sudo iptables -I INPUT -s $IP -j DROP
        sudo ufw deny from $IP
        sudo netfilter-persistent save
        echo "✅ 已添加 $IP 到黑名單"
        ;;
    "remove")
        if [ -z "$2" ]; then
            echo "用法: $0 remove <IP地址>"
            exit 1
        fi
        IP=$2
        sudo sed -i "/^$IP$/d" $BLACKLIST_FILE
        sudo iptables -D INPUT -s $IP -j DROP
        sudo ufw delete deny from $IP
        sudo netfilter-persistent save
        echo "✅ 已從黑名單移除 $IP"
        ;;
    "stats")
        echo "📊 黑名單統計："
        echo "- 黑名單 IP 數量: $(wc -l < $BLACKLIST_FILE 2>/dev/null || echo 0)"
        echo "- 最近更新時間: $(tail -1 $LOG_FILE 2>/dev/null || echo '無記錄')"
        echo "- 防火牆規則數量: $(sudo iptables -L INPUT | grep DROP | wc -l)"
        ;;
    "log")
        echo "📜 黑名單操作日誌："
        if [ -f $LOG_FILE ]; then
            tail -20 $LOG_FILE
        else
            echo "無日誌記錄"
        fi
        ;;
    *)
        echo "🛡️ IP 黑名單管理工具"
        echo ""
        echo "用法: $0 {list|add|remove|stats|log}"
        echo ""
        echo "命令說明："
        echo "  list     - 顯示所有黑名單 IP"
        echo "  add <IP> - 添加 IP 到黑名單"
        echo "  remove <IP> - 從黑名單移除 IP"
        echo "  stats    - 顯示黑名單統計"
        echo "  log      - 顯示操作日誌"
        ;;
esac

