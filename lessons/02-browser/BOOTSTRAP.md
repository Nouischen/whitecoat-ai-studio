# 給 AI：準備第二課教材

教材版本：1.1.0；沿用第一課資料夾格式 1。使用繁體中文，純文字一律以 UTF-8 讀寫。只準備本課教材，不安裝程式、擴充功能或開發環境，不新增 AGENTS.md、CLAUDE.md 或全域設定。

## 先確認原工作室

用現有檔案工具確認學員已選取的完整工作室路徑，確認末層資料夾是學員選定的「我的AI工作室」；若在整個「文件」、下載或其他目錄就停下，請學員重選。只看該位置第一層，讀「開始這裡.md」「課程規則.md」「課程進度.md」。四個根目錄檔案與四個既有資料夾沿用，不另造平行工作室，不掃其他私人位置。

未選工作室就請學員在桌面程式選取第一課的工作室。若根本沒有工作室，或缺「課程規則.md」等必要入口，列明缺件，用現有讀取工具取得第一課固定準備指令：
https://raw.githubusercontent.com/Nouischen/whitecoat-ai-studio/v1.0.1/BOOTSTRAP.md

依第一課指令只補必要缺件，保留已有內容；無法取得時提供同一網址請學員打開交由 AI 讀取，仍失敗則請主持人協助。不憑空猜規則、不假造個人資料或工作室，不把第一課進度改成完成。已有工作室與規則就可先做共同練習，不要求第一課全部過關。

## 六份教材：逐一補缺

以下目的路徑都相對於已選工作室。來源固定 v1.1.0，不改用 main、latest 或其他版本。使用現有 HTTP 下載／網頁純文字讀取與檔案工具，從各列完整網址取得完整文字；不下載整個 repo 或壓縮包。

| 內容 | 目的路徑 | 固定純文字下載網址 |
|---|---|---|
| 新手入口 | 工作模板/02-瀏覽器教材/README.md | https://raw.githubusercontent.com/Nouischen/whitecoat-ai-studio/v1.1.0/lessons/02-browser/README.md |
| 三天步驟 | 工作模板/02-瀏覽器教材/TASKS.md | https://raw.githubusercontent.com/Nouischen/whitecoat-ai-studio/v1.1.0/lessons/02-browser/TASKS.md |
| 共同文章 | 工作模板/02-瀏覽器教材/materials/practice-article.md | https://raw.githubusercontent.com/Nouischen/whitecoat-ai-studio/v1.1.0/lessons/02-browser/materials/practice-article.md |
| 核對答案 | 工作模板/02-瀏覽器教材/materials/expected-results.md | https://raw.githubusercontent.com/Nouischen/whitecoat-ai-studio/v1.1.0/lessons/02-browser/materials/expected-results.md |
| 資料卡範本 | 工作模板/02-瀏覽器教材/templates/source-card.md | https://raw.githubusercontent.com/Nouischen/whitecoat-ai-studio/v1.1.0/lessons/02-browser/templates/source-card.md |
| 填寫示範 | 工作模板/02-瀏覽器教材/examples/completed-card.md | https://raw.githubusercontent.com/Nouischen/whitecoat-ai-studio/v1.1.0/lessons/02-browser/examples/completed-card.md |

1. 先檢查目的路徑及父資料夾，解析後都須留在已選工作室。遇到連向外部位置的檔案連結、路徑衝突或無寫入權限，停該項並回報。只建立缺少的教材子資料夾。
2. 每個缺件先下載到工具允許的本次暫存位置；記住暫存路徑，不把暫存當正式成果。不要刪除任何檔案。
3. 檢查 HTTP 成功、可完整以 UTF-8 讀取、不是 HTML 錯誤頁／登入頁／截斷預覽。檢查標題與結尾：README 為第二課、TASKS 有三天與中斷接續；文章含 WC02-READ-01，答案含核對表，範本含來源／原文／核對／讀後整理，範例明標共同練習。404 或內容不符就停止該項，不自編替代教材。
4. 檢查合格才複製完整純文字到表列目的路徑，維持相對路徑及檔名，不執行下載內容。不安裝 Python、Node.js、Git，不要求擴權。平台必要核准依正常提示處理，組織禁用就回報。
5. 寫入時採遇同名即略過的新增方式。任何既有同名檔都保留，包含空檔、不同版本或內容不同的檔。可與固定來源比對並回報「相同／不同／尚無法確認」；不同或空檔不能算可用教材，不覆蓋、刪除或自動合併。其他正常缺件可繼續補。遇衝突且暫時不處理時，可從固定網址讀 TASKS 做共同練習，本機教材仍標待補。

## 從目的位置讀回

重新讀取六份目的檔，新增檔與暫存原文逐一比對。回報每份「已新增且讀回／原檔相同已保留／衝突／缺件」及實際路徑；只讀到部分不可報完整。引用「課程規則.md」一條原文，並讀出共同文章標題，證明選對位置與編碼。

只準備教材不代表瀏覽器練習完成。教材可用後讀 TASKS，從進度接續；第一次從第一天開始。START 是線上瀏覽器入口，不在上述六份下載檔中，不額外補成第七份。

## 下載失敗才用的手動備援

先指出失敗的是哪一個檔案或工具。若 AI 仍能讀公開網址與存檔，讓 AI 自行改用表中固定 Raw 網址讀完整純文字、暫存檢查後補缺，學員不搬提示詞。

AI 確實無法下載時，學員可照以下操作；這只是在準備素材：

1. 用一般瀏覽器打開教材頁：https://github.com/Nouischen/whitecoat-ai-studio/tree/v1.1.0/lessons/02-browser 。依上表逐個點檔案；materials、templates、examples 要先點進同名資料夾。也可直接開表中的完整 Raw 網址。
2. 在檔案頁點 Raw，再選 Download raw file／下載；若直接顯示純文字，可用「另存新檔」，或全選複製完整純文字到純文字編輯器後以 UTF-8 儲存。不要複製 GitHub 網頁排版、導覽按鈕或只複製一段。
3. 在原工作室建立缺少的「工作模板/02-瀏覽器教材/」及表中子資料夾，逐份儲存到表列目的路徑。檔名原樣保留，確認沒有多出 .txt；不要存成 Word 或網頁檔。遇同名檔就取消覆蓋並回報。
4. 回桌面對話告訴 AI「我已手動放好素材，請按 BOOTSTRAP 的讀回步驟逐份檢查」，由 AI 用檔案工具檢查六份完整內容。若工具連檔案也讀不到，就保持「素材待確認」，請主持人協助。

若頁面不存在或 Raw 回傳錯誤，請回報主持人，不換版也不拿錯誤頁存成教材。備援成功後只記「素材已備妥，瀏覽器練習未完成」，接下來仍須由 AI 用瀏覽器開 START、點連結並核對文章；人工開頁與 HTTP 下載都不能代替。
