# TryHackMe 入門挑戰解題指南

本專案為「TryHackMe 入門挑戰解題指南」靜態網站，專為資安初學者設計，內容涵蓋滲透測試流程、常用工具、Web 安全、實用技巧與推薦房間等，協助新手循序漸進學習資安技能。

---

## 目錄結構

```
dist/
  ├─ index.html
  ├─ favicon.ico
  └─ assets/
      ├─ index--8nNg77_.js   # 主程式 JS
      ├─ index-UiBImJG6.css  # 主樣式 CSS
      └─ ... 其他圖片/靜態資源
```

---

## 如何本地預覽

**請勿直接用瀏覽器開啟 index.html（file://），請務必用本地伺服器！**

### 方法一：Node.js http-server
```bash
npm install -g http-server
cd dist
http-server
# 預設網址 http://localhost:8080
```

### 方法二：Python 3.x
```bash
cd dist
python -m http.server 8080
# 預設網址 http://localhost:8080
```

### 方法三：VSCode Live Server
- 右鍵 dist 資料夾 → Open with Live Server

---

## 注意事項
- 請確認 `index.html` 內的 JS/CSS 路徑為相對路徑（如 `assets/index--8nNg77_.js`）。
- 若遇到畫面空白，請開啟瀏覽器 Console 查看錯誤訊息。
- 常見錯誤：
  - 404 找不到 JS/CSS：請確認 assets 目錄存在且路徑正確。
  - CORS 或 module 錯誤：請務必用伺服器啟動，不要直接 file:// 開啟。

---

## Workflow 建議
1. 每次修改原始碼後，請重新 build 專案，確保 dist 內容為最新。
2. 預覽時請用本地伺服器（如上方說明）。
3. 修改靜態資源（如圖片、JS、CSS）後，請重新整理瀏覽器快取。
4. 若有 workflow 或狀態追蹤需求，請於本 README.md 記錄。

---

## 聯絡/貢獻
- 歡迎提出 issue 或 pull request。
- 聯絡方式：Freedom_Duke
