# 滲透測試知識篇 - 網路攻擊鏈教學網站

## 📖 專案介紹

這是一個專業的滲透測試教學網站，深入介紹由 Lockheed Martin Inc. 於 2011 年提出的 **網路攻擊鏈 (Cyber Kill Chain)** 模型。本網站以繁體中文呈現完整的 APT (Advanced Persistent Threat) 攻擊流程，適合資安從業人員、滲透測試工程師以及資安初學者學習使用。

### 🎯 教學內容

- **網路攻擊鏈七大階段**：從偵蒐到最終目標達成的完整攻擊流程
- **攻擊成功三大核心條件**：有弱點、可利用、無防護
- **實際案例研究**：WinRAR CVE-2023-40477 漏洞詳細分析
- **社交工程技術**：包含 Excel 釣魚、SVG 攻擊等最新手法
- **滲透後作業**：權限提升、持久化、清除軌跡等技術
- **防禦與鑑識工具**：日誌分析、惡意程式檢測工具介紹

### 🛡️ 使用聲明

**⚠️ 重要提醒：本網站僅供教育用途！**

- 所有內容僅用於學術研究和防禦性資安訓練
- 請勿將相關技術用於任何非法活動
- 使用者需承擔使用本知識的法律責任
- 建議在受控環境中進行學習和實驗

## 🚀 快速開始

### 📋 系統需求

#### 基本需求（Python 方法）
- **Python**: 3.x 版本（大多數系統已預裝）
- **瀏覽器**: Chrome、Firefox、Safari、Edge 現代瀏覽器

#### 進階開發需求（Vite 方法）
- **Node.js**: 16.x 或更高版本
- **pnpm**: 8.x 或更高版本（推薦）
- **瀏覽器**: Chrome、Firefox、Safari、Edge 現代瀏覽器

### 📦 安裝依賴

```bash
# 使用 pnpm 安裝依賴（推薦）
pnpm install

# 或使用 npm
npm install

# 或使用 yarn
yarn install
```

### 🔧 啟動網站

#### 方法一：使用 Python 簡易伺服器（推薦）

```bash
# Python 3.x
python -m http.server 8000

# Python 2.x（舊版本）
python -m SimpleHTTPServer 8000

# 指定其他埠號
python -m http.server 3000
```

啟動後，開啟瀏覽器訪問：
- **本地地址**: http://localhost:8000
- **網路地址**: http://192.168.x.x:8000

#### 方法二：使用 Vite 開發伺服器

```bash
# 啟動開發伺服器
pnpm dev

# 或使用 npm
npm run dev
```

開發伺服器啟動後，開啟瀏覽器訪問：
- **本地地址**: http://localhost:5173
- **網路地址**: http://192.168.x.x:5173

### 🏗️ 建構專案

```bash
# 建構生產版本
pnpm build

# 或使用 npm
npm run build
```

建構完成後，所有文件將生成在 `dist/` 目錄中。

### 📱 本地預覽建構結果

```bash
# 預覽建構結果
pnpm preview

# 或使用 npm
npm run preview
```

## 📁 專案結構

```
滲透測試知識篇/
├── index.html              # 主要頁面
├── style.css              # 樣式文件
├── script.js              # 互動邏輯
├── package.json           # 專案配置
├── pnpm-lock.yaml         # 依賴鎖定文件
├── template_config.json   # 模板配置
├── README.md              # 說明文件
└── 圖片資源/
    ├── cyber-kill-chain.png         # 英文版攻擊鏈圖
    ├── cyber-kill-chain-chinese.png # 中文版攻擊鏈圖
    └── cyber-kill-chain-new.png     # 新版攻擊鏈圖
```

## 🎨 功能特色

### 📊 互動式學習體驗
- **分頁式介面**：七大攻擊階段逐步學習
- **視覺化流程圖**：中英文對照的攻擊鏈圖表
- **程式碼範例**：實際的攻擊指令和防禦技術
- **響應式設計**：支援桌面、平板、手機瀏覽

### 🔍 深度技術內容
- **詳細漏洞分析**：CVE-2023-40477 完整復現流程
- **最新攻擊手法**：SVG 漏洞、Excel 釣魚等前沿技術
- **企業環境模擬**：真實網路環境的攻擊場景
- **防禦策略指南**：對應每個攻擊階段的防禦建議

### 🛠️ 技術規格
- **HTML5**: 語義化標籤與現代化結構
- **CSS3**: Flexbox、Grid 布局與動畫效果
- **Vanilla JavaScript**: 純原生 JS 實現互動功能
- **Vite**: 快速開發構建工具
- **Font Awesome**: 豐富的圖示庫

## 🔧 自定義配置

### 修改網站內容
1. 編輯 `index.html` 修改頁面內容
2. 修改 `style.css` 調整樣式和布局
3. 更新 `script.js` 調整互動行為

### 添加新的攻擊階段
1. 在 `index.html` 中的 `.stages-content` 區塊添加新的 `.stage-card`
2. 在 `.stage-navigation` 添加對應的導航按鈕
3. 在 `script.js` 中更新階段切換邏輯

### 更新圖片資源
將新的圖片放置在專案根目錄，並在 HTML 中更新對應的路徑。

## 🌐 部署說明

### 靜態文件部署
1. 執行 `pnpm build` 建構專案
2. 將 `dist/` 目錄中的所有文件上傳到 Web 伺服器
3. 配置伺服器指向 `index.html`

### 支援的部署平台
- **Netlify**: 拖拽部署或 Git 整合
- **Vercel**: 自動構建和部署
- **GitHub Pages**: 靜態文件託管
- **Firebase Hosting**: Google 雲端託管
- **傳統 Web 主機**: 任何支援靜態文件的主機

## 🐛 常見問題

### Q: Python 伺服器無法啟動？
A: 請確認：
- 系統是否已安裝 Python：`python --version` 或 `python3 --version`
- 是否在正確的專案目錄中執行指令
- 埠號是否被其他程式佔用：`netstat -an | findstr :8000`（Windows）或 `lsof -i :8000`（macOS/Linux）
- 嘗試更換埠號：`python -m http.server 3000`

### Q: Vite 開發伺服器無法啟動？
A: 請確認：
- Node.js 版本是否符合要求（16.x+）
- 是否正確安裝了依賴：`pnpm install`
- 埠號 5173 是否被其他程式佔用

### Q: 圖片無法正常顯示？
A: 檢查：
- 圖片文件是否存在於正確路徑
- 圖片文件名稱是否正確（區分大小寫）
- 瀏覽器開發者工具中的網路請求狀態

### Q: JavaScript 功能異常？
A: 請：
- 開啟瀏覽器開發者工具檢查控制台錯誤
- 確認瀏覽器版本支援現代 JavaScript 語法
- 清除瀏覽器快取重新載入

## 📚 學習建議

### 初學者路徑
1. **基礎概念**：先閱讀首頁的 APT 和攻擊鏈介紹
2. **核心條件**：理解「有弱點、可利用、無防護」三大條件
3. **七大階段**：逐步學習每個攻擊階段的技術細節
4. **實際案例**：深入研究 [WinRAR CVE-2023-40477案例]  (https://cloud.tencent.cn/developer/article/2324062?policyId=1004)
5. **防禦工具**：了解對應的防禦和檢測技術

### 進階學習
1. **動手實驗**：在受控環境中復現相關技術
2. **延伸閱讀**：參考網站中提到的工具和技術文件
3. **持續更新**：關注最新的 CVE 和攻擊技術趨勢

## 🤝 貢獻指南

歡迎提交問題回報和改進建議：

1. **Fork** 專案
2. 創建 **feature 分支**：`git checkout -b feature/amazing-feature`
3. **提交** 變更：`git commit -m 'Add some amazing feature'`
4. **推送** 到分支：`git push origin feature/amazing-feature`
5. 開啟 **Pull Request**

## 📄 版權說明

- 網站內容基於 Lockheed Martin Inc. 的 Cyber Kill Chain 模型
- 技術資料來源於公開的資安研究和文獻
- 程式碼採用 ISC 授權條款
- 僅供教育和學術研究使用

## 📞 聯絡資訊

如有任何技術問題或建議，歡迎透過以下方式聯絡：

- **專案Issues**: 在 GitHub 上提交問題
- **技術討論**: 在相關的資安社群中討論

---

**⚠️ 免責聲明**: 本專案提供的所有技術內容僅供學習和研究使用。使用者必須遵守當地法律法規，不得將相關技術用於任何非法活動。開發者不承擔因誤用本專案內容而產生的任何法律責任。

---

*最後更新：2024年12月* 
