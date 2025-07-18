# 歌唱幸福論 - 安全腳本

## 檔案說明

### blacklist_manager.sh
IP黑名單管理工具，支援以下功能：
- `list` - 顯示當前黑名單
- `add <IP>` - 添加IP到黑名單
- `remove <IP>` - 從黑名單移除IP
- `stats` - 顯示統計資訊
- `log` - 顯示操作日誌

### blacklist_monitor.sh
自動監控腳本，每小時執行一次：
- 分析 `/var/log/auth.log` 找出重複攻擊者
- 自動添加攻擊次數>5的IP到黑名單
- 更新防火牆規則
- 記錄操作日誌

### ssh_attackers.txt
當前黑名單IP列表，包含12個惡意IP地址

## 部署狀態
- ✅ 虛擬機已部署並運行
- ✅ 防火牆規則已生效
- ✅ Cron任務已設定（每小時執行）
- ✅ 規則持久化已啟用

## 使用方法
```bash
# 在虛擬機上使用
blacklist_manager.sh list
blacklist_manager.sh add 1.2.3.4
blacklist_manager.sh stats
```

最後同步時間: 2025-07-16 22:30 UTC