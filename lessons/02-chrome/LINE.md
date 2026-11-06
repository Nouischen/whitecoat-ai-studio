# 第二課｜用 Chrome 側欄操作一頁，再把兩頁交給同一段對話

```text
【白袍 AI 第二課 ①｜打開 AI，讓它幫你點網頁】

今天用電腦版 Chrome。裝你平常用的那一套，點「加到 Chrome」→「新增擴充功能」，依畫面登入。已經裝好的人直接做下一步。
Claude（需支援的付費方案）：https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
ChatGPT：https://chromewebstore.google.com/detail/chatgpt/hehggadaopoacecdllhhajmbjkdcmajg

1. 在 Chrome 打開 https://developers.openai.com/api/docs 。先停在這個英文網站。

2. 看網址列右邊，點拼圖圖示 🧩，再點「Claude」或「ChatGPT」。如果你用的 AI 圖示已經在工具列，直接點它就好。

3. 這時原來的網站還在，同一個 Chrome 視窗旁邊會多出一欄 AI 對話。看一下畫面的兩個位置：最上面寫著網站名稱的小標籤叫「分頁」；旁邊可以打字問 AI 的地方叫「側欄」。在這個分頁打開側欄，就能一邊交代 AI，一邊看它操作網頁。

4. 點側欄底下的輸入框，貼這句：
「請直接操作眼前這個網頁，點進 Quickstart，捲到『Create and export an API key』那一段就停。把畫面留給我看，不要建立金鑰。」

如果跳出網站授權，核對是 developers.openai.com，再允許這次操作。眼睛看網頁：真的跳到 Quickstart、畫面出現那行英文，就成功了。若 AI 只回覆一串步驟，告訴它「請幫我點，讓我看分頁上的結果」。

接下來要加第二頁。用 Claude 的人看 ②，用 ChatGPT 的人看 ③。學會後，也可以換成年會的「議程」和「報名」兩頁，請 AI 幫你對照場次與報名選項。
```

```text
【② 用 Claude｜把第二個網頁拉進同一組】

1. 先留著剛才的 Quickstart。點 Chrome 最上方分頁列的「＋」，在新分頁打開模型清單：https://developers.openai.com/api/docs/models 。現在上面有兩個標題，一個是 Quickstart，另一個是 Models。

2. 看最上面的分頁列，找剛才 Claude 操作的 Quickstart。它所在的彩色區段就是這次要用的群組。若 Models 已在同一段顏色裡，直接做第 4 步。

3. 把滑鼠放在上方寫著「Models」的分頁標題，按住左鍵，沿著分頁列往 Quickstart 的方向平移。把 Models 移進那段顏色裡，放在 Quickstart 旁邊，再放開左鍵。放好後，兩個標題都在同一段顏色裡。

拖不準？在「Models」標題上按右鍵，選「將分頁加入群組」，再選 Quickstart 所在的既有群組。若整排都找不到 Claude 的群組，回 Quickstart 的側欄說：「請在新的分頁打開 https://developers.openai.com/api/docs/models 」，讓 Claude 幫你開。

4. 點回 Quickstart，在剛才的 Claude 對話貼：
「請看 Quickstart 和 Models 這兩個已開啟的分頁，各列出頁名，再從各頁抄一個小標題。只能讀到一頁就告訴我。」

自己輪流點兩個分頁，對照它列的小標。兩頁的字都對得上，就學會怎麼把兩頁交給同一個 AI 了。
```

```text
【③ 用 ChatGPT｜在同一段對話選第二頁】

1. 先留著剛才的 Quickstart。點 Chrome 最上方分頁列的「＋」，在新分頁打開模型清單：https://developers.openai.com/api/docs/models 。再點上方的 Quickstart 回去。剛才的 ChatGPT 側欄是跟這一頁連在一起的。

2. 在原本的側欄輸入框打半形 @。清單出現後，找已開啟的「Models」分頁，核對網址含有 /api/docs/models，點它。送出前看一下，輸入區應能認出你選的是 Models。

3. 在同一段對話貼：
「請看原來的 Quickstart 和剛選的 Models，各列出頁名，再從各頁抄一個小標題。只能讀到一頁就告訴我。」
自己輪流點兩個分頁核對。兩個小標都能在對應網頁找到，就成功了。

如果側欄沒有列出分頁，可開 chatgpt.com，在對話輸入框旁按「＋」選已開啟的 Chrome 分頁，或輸入 @Chrome 找分頁。若一次只能選一頁，就在同一段對話先選 Quickstart，請它抄一個小標並送出；再選 Models 做一次，最後請它把兩筆並排列出來。

換成你自己的用途也一樣。比如查郵輪，先開兩個航次，請 AI「用這兩頁比較出發日和停靠港，列給我看就好」。你下次最想交給它哪兩頁？
```
