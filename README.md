# osu! Beatmap Downloader

🎵 一鍵搜尋與下載 osu! 圖譜（`.osz` 檔案）的工具，支援進階搜尋、自動下載、來源備援與下載進度顯示。

---

## ✅ 功能特色

- 🔎 搜尋 beatmap（支援關鍵字、狀態、模式與排序）
- 📂 自訂下載資料夾（預設為 `%LOCALAPPDATA%\osu!\Songs`）
- 📥 自動下載 `.osz` 圖譜檔
- 🔁 多來源下載（catboy.best & nerinyan.moe）
- 🧼 自動修正非法檔案名稱
- ⏳ 顯示下載進度條
- 🔃 自動重試與錯誤提示

---

## 🧑‍💻 使用方法（EXE）

### 1️⃣ 下載執行檔

請從此處下載最新版執行檔（osu_downloader.exe）：

👉 [下載連結](https://github.com/wayne1000901103/Osu-Automatic-download/releases/download/V1.0.0/osu.Beatmap.Downloader.exe)

---

### 2️⃣ 執行程式

1. **雙擊 `osu_downloader.exe`**
2. 首次執行會提示設定下載資料夾（預設為 `osu!\Songs` 資料夾）
3. 接著輸入搜尋條件（例如圖譜名稱、模式等）
4. 選擇要下載的圖譜
5. 程式會自動下載 `.osz` 檔案並儲存

---

## 📁 設定檔

程式會自動建立一個 `config.json` 檔案來記錄你設定的下載資料夾位置，下次執行會自動使用。

---

## ❓ 常見問題

### ❗ 程式開啟後一閃即關怎麼辦？

這種情況通常是因為：

- 程式被防毒軟體封鎖或終止

✅ 方法一：將程式加入防毒白名單
由於此 EXE 是用 Python 打包，部分防毒軟體（如 Windows Defender、Avast、Norton）可能會誤判為不明程式，直接封鎖或強制關閉。

請執行以下步驟：

1.開啟你的防毒軟體或 Windows 安全性中心

2.將 osu_downloader.exe 或其資料夾加入「排除項目」或「白名單」

3.重新執行程式
