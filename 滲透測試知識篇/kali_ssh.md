
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


---

## ✅ 七、新增使用者帳號（建議不要直接使用 root 登入）

```bash
sudo adduser 新使用者名稱
```

例如：

```bash
sudo adduser kaliuser
```

加入 sudo 群組（具有管理者權限）：

```bash
sudo usermod -aG sudo kaliuser
```

你可以用這個新帳號登入：

```bash
ssh kaliuser@Kali_IP
```

## ✅ 六、防火牆與 NAT 注意事項

若有啟用 `ufw` 防火牆，請開啟 22 埠：

```bash
sudo ufw allow 22/tcp
```

虛擬機用戶需確認 NAT 或橋接網路設定正確，才能從主機連線進 Kali。

---


---

## ✅ 七、建立新使用者並設定密碼

以 `newuser` 為例：

```bash
sudo adduser newuser
```

系統會提示輸入密碼與其他使用者資訊。

或直接以指令加上密碼（⚠️不建議明文執行，僅供測試用途）：

```bash
sudo useradd -m -s /bin/bash newuser
echo "newuser:你的密碼" | sudo chpasswd
```

---

## ✅ 八、為新使用者設定 SSH 公私鑰登入方式

### 1. 使用 ssh-keygen 產生金鑰（在客戶端執行）

```bash
ssh-keygen -t rsa -b 4096 -C "newuser@kali"
```

將會產生：

- 私鑰：`~/.ssh/id_rsa`
- 公鑰：`~/.ssh/id_rsa.pub`

---

### 2. 將公鑰複製到 Kali 的新使用者帳號中（在客戶端執行）

```bash
ssh-copy-id newuser@KALI_IP
```

或手動做法（在 Kali 執行）：

```bash
sudo mkdir -p /home/newuser/.ssh
sudo nano /home/newuser/.ssh/authorized_keys  # 將公鑰貼上
sudo chown -R newuser:newuser /home/newuser/.ssh
sudo chmod 700 /home/newuser/.ssh
sudo chmod 600 /home/newuser/.ssh/authorized_keys
```

---

### 3. 測試 SSH 連線

```bash
ssh newuser@KALI_IP
```

如果金鑰正確且設定無誤，應可無密碼登入。

---

## ✅ 九、Windows 使用者透過金鑰 SSH 連線至 Kali

### 1. 產生金鑰（使用 Windows 內建 OpenSSH）

打開 PowerShell 或 CMD：

```powershell
ssh-keygen -t rsa -b 4096 -C "newuser@windows"
```

預設會將金鑰儲存於：

```
C:\Users\你的名稱\.ssh\id_rsa
C:\Users\你的名稱\.ssh\id_rsa.pub
```

---

### 2. 複製公鑰到 Kali（手動或使用 ssh-copy-id for Windows）

手動方式：

1. 開啟 `id_rsa.pub` 並複製內容
2. 在 Kali 上執行：

```bash
sudo mkdir -p /home/newuser/.ssh
sudo nano /home/newuser/.ssh/authorized_keys
# 貼上剛剛複製的公鑰內容
sudo chown -R newuser:newuser /home/newuser/.ssh
sudo chmod 700 /home/newuser/.ssh
sudo chmod 600 /home/newuser/.ssh/authorized_keys
```

---

### 3. Windows 測試 SSH 連線（使用金鑰）

打開 PowerShell 或 CMD：

```powershell
ssh -i C:\Users\你的名稱\.ssh\id_rsa newuser@KALI_IP
```

---

如果一切設定正確，你應該可以不需輸入密碼，直接登入 Kali。

---
