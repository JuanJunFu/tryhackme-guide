
# Kali Linux SSH 開啟指南

本指南將協助你在 Kali Linux 上安裝、啟用並設定 SSH（Secure Shell）服務。

---

## ✅ 一、安裝 SSH Server（若尚未安裝）

```bash
sudo apt update
sudo apt install openssh-server -y
```

---

## ✅ 二、啟用 SSH 服務

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

檢查服務狀態：

```bash
sudo systemctl status ssh
```

---

## ✅ 三、設定 SSH 允許 root 登入（可選、⚠️不建議正式環境開啟）

編輯 SSH 設定檔：

```bash
sudo vim /etc/ssh/sshd_config
```

確認以下設定存在：

```bash
PermitRootLogin yes
PasswordAuthentication yes
```

儲存後重新啟動服務：

```bash
sudo systemctl restart ssh
```

---

## ✅ 四、查詢 IP 位址（供遠端登入）

```bash
ip a
```

記下內網或外網 IP。

---

## ✅ 五、從其他裝置登入 Kali SSH

```bash
ssh 使用者帳號@Kali_IP
```

例如：

```bash
ssh root@192.168.56.101
```

Windows 用戶可使用 [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)。

---

## ✅ 六、防火牆與 NAT 注意事項

若有啟用 `ufw` 防火牆，請開啟 22 埠：

```bash
sudo ufw allow 22/tcp
```

虛擬機用戶需確認 NAT 或橋接網路設定正確，才能從主機連線進 Kali。

---

