# 凰羽選宅 Facebook 粉絲專頁週末自動發文系統

此系統旨在自動化「凰羽選宅」Facebook 粉絲專頁的週末貼文發佈，利用 GitHub Actions 進行排程，並透過 Meta Graph API 進行發文，確保符合 Meta 平台規範。

## 一、設定 GitHub Secrets

為了安全地管理 Facebook API 憑證，請在您的 GitHub Repository 中設定以下 Secrets：

1.  `FB_PAGE_ID_HUANGYU`: 凰羽選宅粉絲專頁的 Page ID (例如：`110923925432843`)
2.  `FB_PAGE_TOKEN_HUANGYU`: 凰羽選宅粉絲專頁的 Access Token。請確保此 Token 具有發文權限。
3.  `FB_GRAPH_API_VERSION`: Meta Graph API 的版本 (例如：`v21.0`)。如果未設定，系統將預設使用 `v21.0`。

**重要安全提示：**
*   請勿將任何 Token 資訊直接寫入程式碼、README、log 檔案或 GitHub Actions 的 log 輸出中。
*   Token 只能從 GitHub Secrets 中讀取。
*   在任何顯示 Token 的情境下 (例如錯誤訊息或檢查 Token 的指令輸出)，Token 都必須被遮罩處理 (例如：`EAAB************abcd`)。

## 二、貼文內容資料夾結構

請依照以下結構放置您的貼文內容：

```
posts/
└─ huangyu/
   ├─ saturday_money_class/  # 週六屋主小教室貼文
   │  ├─ post_001.txt
   │  ├─ post_001.png
   │  ├─ post_002.txt
   │  └─ post_002.png
   │
   └─ sunday_cleanup/  # 週日看屋整理術貼文
      ├─ post_001.txt
      ├─ post_001.jpg
      ├─ post_002.txt
      └─ post_002.jpg
```

*   `.txt` 檔案包含貼文的文字內容。
*   同名的 `.png`、`.jpg` 或 `.jpeg` 檔案將作為貼文的配圖。如果沒有圖片，系統將發佈純文字貼文並顯示警告。

## 三、如何新增貼文

1.  在 `posts/huangyu/saturday_money_class/` 或 `posts/huangyu/sunday_cleanup/` 資料夾中，新增一組 `.txt` 檔案和 (可選的) 同名圖片檔案 (例如：`post_003.txt` 和 `post_003.png`)。
2.  系統會自動尋找尚未發佈的貼文並依序發佈。

## 四、手動執行 GitHub Actions 測試

您可以透過 GitHub Actions 介面手動觸發 `fb-huangyu-weekend-post.yml` workflow 進行測試：

1.  進入您的 GitHub Repository，點擊 `Actions` 分頁。
2.  在左側選單中找到 `FB Huangyu Weekend Auto Post`。
3.  點擊 `Run workflow` 按鈕。
4.  您可以選擇 `category` (saturday_money_class 或 sunday_cleanup) 和 `publish` (true 或 false)。
    *   選擇 `publish: false` 將執行 `dry-run`，模擬發文過程而不實際發佈。
    *   選擇 `publish: true` 將實際發佈貼文。

## 五、確認台灣時間排程

GitHub Actions 的 `schedule` 使用 UTC 時間。本系統已設定以下排程：

*   **週六屋主小教室**: 台灣時間每週六晚上 8:00 (UTC 時間 `0 12 * * 6`)
*   **週日看屋整理術**: 台灣時間每週日下午 5:00 (UTC 時間 `0 9 * * 0`)

您可以參考 `repo/.github/workflows/fb-huangyu-weekend-post.yml` 檔案中的 `cron` 設定來確認或調整排程。

## 六、查看 Log 與 posted_history

每次 GitHub Actions 執行後，都會上傳 `logs/` 資料夾和 `posted_history.json` 作為 Artifacts。您可以透過以下方式查看：

1.  進入您的 GitHub Actions 執行紀錄頁面。
2.  在頁面下方找到 `Artifacts` 區塊。
3.  下載 `fb-huangyu-post-logs` Artifact，其中包含 `logs/` 和 `posted_history.json`。

`posted_history.json` 記錄了所有已發佈貼文的詳細資訊，包括 `page`、`category`、`post_key`、`published_at`、`facebook_post_id` 和 `status`。

## 七、如何更新 Facebook Token

當您的 Facebook Page Token 過期或需要更新時，請按照以下步驟操作：

1.  前往 Meta Developers 平台，重新生成一個新的 Page Access Token。
2.  進入您的 GitHub Repository 設定，點擊 `Secrets and variables` -> `Actions`。
3.  編輯 `FB_PAGE_TOKEN_HUANGYU` 這個 Secret，將其值更新為新的 Token。

**請記住，絕對不要將 Token 直接貼到任何公開或非安全的地方。**

## 八、避免重複發文

系統會維護一個 `posted_history.json` 檔案，記錄所有已成功發佈的貼文。在發文前，系統會檢查此檔案，確保同一 `page`、`category` 和 `post_key` 的貼文不會被重複發佈。

如果該分類下沒有新的未發佈貼文，系統將顯示「目前沒有可發佈的新貼文」的訊息，而不會報錯。

## 九、Token 不會出現在 Log

本系統已實作 Token 遮罩機制，確保 `FB_PAGE_TOKEN_HUANGYU` 不會以完整形式出現在任何 log 輸出中，包括 GitHub Actions 的 log 和錯誤訊息。在任何需要顯示 Token 的情況下，都會以 `EAAB************abcd` 這樣的遮罩形式呈現，以保護您的憑證安全。
