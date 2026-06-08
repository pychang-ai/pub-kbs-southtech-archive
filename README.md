# 高雄廣播電臺《南方科技城》主持人/來賓索引

> A searchable index of hosts and guests across **270 episodes** of the *South Tech City* (南方科技城) radio program on Kaohsiung Broadcasting Station (高雄廣播電臺).

**Last updated**: 2026-06-08
**Data source**: [YouTube playlist `PLuNXocnS3NOJspjOUiWqgQn5terWDMGMR`](https://www.youtube.com/playlist?list=PLuNXocnS3NOJspjOUiWqgQn5terWDMGMR)
**Channel**: [高雄廣播電臺 (Kaohsiung Broadcasting Station)](https://www.youtube.com/channel/UC8CUx-3sw0LjpmDLrupg6Ug)

---

## 摘要

| 指標 | 數量 |
|---|---:|
| 總集數 | 270 |
| 成功解析 | 262 (97.0%) |
| 無描述（已刪除/私人）| 8 |
| **唯一主持人** | **12** 位 |
| **唯一來賓** | **231** 位 |

主持人皆為**國立高雄科技大學（NKUST）**教師。來賓多為產學界專家、政府單位、研究機構代表。

---

## 索引

| 檔案 | 內容 |
|---|---|
| [`hosts.md`](hosts.md) | **12 位主持人**：含出場次數與單位變化 |
| [`guests.md`](guests.md) | **231 位來賓**：含出場次數與單位 |
| [`episodes.md`](episodes.md) | **270 集明細**：集數、上架日、標題、主持人、來賓 |
| [`data/`](data/) | 原始 CSV（含 BOM，Excel 直開）|

---

## 抽取方法

1. `yt-dlp --flat-playlist -J` 取播放清單 video ID 列表
2. `yt-dlp --skip-download --print-to-file` 平行 10 緒抓每集 description
3. Python regex 解析 `主持人：XXX（單位）` / `來賓：XXX（單位）`
4. Normalize 三種格式變形（機構+名字+職稱連寫等）

完整腳本見 [`scripts/`](scripts/)。

---

## Top 10 主持人

| # | 主持人 | 出場次數 | 主要單位 |
|---|---|---:|---|
| 1 | 羅光閔 | 68 | 國立高雄科技大學副教授兼副產學長 |
| 2 | 魏裕珍 | 64 | 國立高雄科技大學副教授兼創新創業教育中心 中心主任 |
| 3 | 蔡匡忠 | 32 | 國立高雄科技大學教授兼學務長 |
| 4 | 潘俊仁 | 31 | 國立高雄科技大學教務處副教務長兼教學發展中心主任 |
| 5 | 郭俊賢 | 24 | 國立高雄科技大學教授兼副校長 |
| 6 | 林皇耀 | 18 | 國立高雄科技大學副教授兼文化創意產業系系主任 |
| 7 | 廖婉茹 | 8 | 國立高雄科技大學營建工程系副教授兼副教務長 |
| 8 | 李憶甄 | 4 | 國立高雄科技大學 水產食品科學系教授兼主任秘書 |
| 9 | 蔡孟修 | 4 | 國立高雄科技大學模具工程系教授兼副產學長 |
| 10 | 丁國桓 | 4 | 國立高雄科技大學漁管系/海洋事務與產業管理研究所副教授 |

> 完整 12 位列表請見 [hosts.md](hosts.md)。

---

## Top 10 來賓（出場次數）

| # | 來賓 | 出場次數 | 單位 |
|---|---|---:|---|
| 1 | 黃炳照 | 4 | 國家講座兼臺科大SEED中心主任 |
| 2 | 林清和 | 4 | 輔英科大環境與生命學院院長 |
| 3 | 黃世宏 | 3 | 高雄市政府環保局副局長 \| 高雄市環保局副局長 |
| 4 | 陳凱琳 | 3 | 先進華斯科技股份有限公司總經理 \| 先進華斯複材科技股份有限公司總經理 \| 先進複材股份有限公司總經理 |
| 5 | 楊慶煜 | 2 | 國立高雄科技大學校長 |
| 6 | 羅光閔 | 2 | 國立高雄科技大學教授兼副學務長 \| 國立高雄科技大學造船及海洋工程系副教授 |
| 7 | 張饌鰆 | 2 | 財團法人高雄市覆鼎金保安宮副總幹事兼文教主任 |
| 8 | 蔡匡忠 | 2 | 國立高雄科技大學副校長 \| 東方科技大學校長 |
| 9 | 蔡美玲 | 2 | 國立高雄科技大學水產食品科學系系主任 \| 高科大海洋科技發展處處長 |
| 10 | 魏德新 | 2 | 國家同步輻射研究中心副主任 |

> 完整 231 位列表請見 [guests.md](guests.md)。

---

## 授權與聲明

| 項目 | 條款 |
|---|---|
| 程式碼（`scripts/`）| MIT License |
| 衍生資料（`data/`, `*.md` 表格）| CC BY 4.0（請註明來源：本 repo + KBS YouTube）|
| 原始節目內容版權 | © 高雄廣播電臺 — 本 repo 僅索引公開描述文字，不重製音檔 |

本 repo 為個人研究/分析用途，與 KBS、NKUST 官方無關聯。

---

*Generated with Claude Code.*
