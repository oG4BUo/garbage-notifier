# ごみ出し通知アプリ

## 概要

このアプリは、ExcelまたはCSVで管理しているごみ収集予定を読み込み、今日と明日のごみを表示し、明日のごみをWindows通知で知らせるPythonアプリです。

将来的な拡張として、自治体のごみカレンダー画像をOCRで読み取り、CSVの下書きを作る機能もあります。

## できること

- ExcelまたはCSVからごみ収集予定を読み込む
- SQLiteデータベースに予定を保存する
- 今日のごみを表示する
- 明日のごみを表示する
- 明日のごみをWindows通知で知らせる
- OCRで画像から予定表の下書きCSVを作る
- Windowsタスクスケジューラで毎日自動実行する

## ファイル構成

```text
ごみカレンダー
├─ README.md
├─ main.py
├─ config.json
├─ garbage_schedule_2026_01.xlsx
├─ garbage.db
├─ ocr_cells.py
├─ ocr_cells_read.py
├─ january.png
├─ ocr_result.csv
├─ cells
└─ cell_debug

必要なライブラリ
最初に以下をインストールします
pip install pandas openpyxl plyer easyocr opencv-python numpy

Excelの形式
予定表のExcelには、次の3列を作ります。
|    date    | garbage_type | note |
|------------|--------------|------|
| 2026-01-07 |     プラ      |     |
| 2026-01-07 |    雑がみ     |      |
| 2026-01-07 |    紙・布     |      |

列名は必ず次の名前にします。
date
garbage_type
note


同じ日に複数のごみがある場合は、1行にまとめず、複数行に分けます。
よい例:
|    date    | garbage_type | note |
|------------|--------------|------|
| 2026-01-09 |     可燃      |      |
| 2026-01-09 |    ペット     |      |
| 2026-01-09 |     金属      |      |
| 2026-01-09 |     発火     |       |


日付の表示形式
Excel上では、日付を日本語表示にしても大丈夫です。
おすすめの表示形式:
yyyy"年"m"月"d"日"
ただし、Python側では main.py の中で日付を次の形式にそろえます。
YYYY-MM-DD


config.json
config.json には、読み込む予定表ファイル名と通知設定を書きます。

json
{
  "schedule_file": "garbage_schedule_2026_01.xlsx",
  "notify_tomorrow": true
}

CSVを使う場合は、次のようにします。
json
{
  "schedule_file": "garbage_schedule_2026_01.csv",
  "notify_tomorrow": true
}


予定表を取り込む
ExcelまたはCSVを修正したら、保存してから次を実行します。
python main.py import
これで予定表の内容が garbage.db に保存されます。


データベースの中身を確認する
python main.py show

表示例:
=== データベースの中身 ===
(41, '2026-01-06', '可燃', '')
(42, '2026-01-07', 'プラ', '')
(43, '2026-01-07', '雑がみ', '')



今日・明日のごみを表示して通知する
python main.py notify
明日の予定がデータベースにある場合、Windows通知が出ます。

通知が出る条件:
config.json の notify_tomorrow が true
明日の日付の予定がデータベースにある



OCRの流れ
OCRは、自治体カレンダー画像からCSVの下書きを作るために使います。
まず、1月のカレンダー画像を次の名前で保存します。
january.png


1. カレンダー画像を日ごとに分割する
python ocr_cells.py
実行すると、cells フォルダに日ごとの画像が作られます。

cells
├─ day_01.png
├─ day_02.png
├─ day_03.png
...


2. 日ごとの画像をOCRする
python ocr_cells_read.py
実行すると、OCR結果が表示され、ocr_result.csv が作成されます。

例:
7日: ['プラ', '雑がみ']
9日: ['ペット']
16日: ['びん', '缶']



3. OCR結果を確認・修正する
ocr_result.csv をExcelで開き、足りない予定や読み間違いを手で修正します。
修正後、次のような名前で保存します。
garbage_schedule_2026_01.xlsx
その後、config.json の schedule_file をこのファイル名にします。

json
{
  "schedule_file": "garbage_schedule_2026_01.xlsx",
  "notify_tomorrow": true
}
最後に取り込みます。
python main.py import



OCRについての注意
OCRは完全ではありません。
たとえば、次のような読み間違いがあります。
| 誤認識 | 正しい文字 |
|--------|-----------|
|  フラ  |    プラ    |
|  ナラ  |    プラ    |
|  ひん  |    びん    |
| 雛かみ |    雑がみ  |
| 雄がみ |    雑がみ  |
|  ット  |    ペット  |
そのため、OCR結果は必ず人間が確認します。



Windowsタスクスケジューラ
毎日自動で通知する場合は、Windowsのタスクスケジューラを使います。
プログラム/スクリプト
Python本体の場所を指定します。
例:
C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe

Pythonの場所を確認するには、PowerShellで次を実行します。
(Get-Command python).Source

引数の追加
"c:\Users\user\Desktop\ごみカレンダー\main.py" notify

開始
c:\Users\user\Desktop\ごみカレンダー

実行タイミング
前日の夜に通知したい場合は、毎日18時などに設定します。
例:
毎日 18:00

よく使うコマンド
予定表を取り込む:
python main.py import

データベースを見る:
python main.py show

今日・明日の予定を表示して通知する:
python main.py notify

OCR用に日ごとの画像へ分割する:
python ocr_cells.py

OCR結果をCSVにする:
python ocr_cells_read.py



よくあるエラー
config.json が見つからない
main.py と同じフォルダに config.json があるか確認します。
schedule_file がありません
config.json に次の項目があるか確認します。
"schedule_file": "garbage_schedule_2026_01.xlsx"

予定表ファイルが見つからない
config.json に書いたファイル名と、実際のExcel/CSVの名前が同じか確認します。
date列がありません
ExcelまたはCSVの列名を確認します。
必要な列名:
date
garbage_type
note

通知が出ない
次を確認します。
明日の日付の予定がデータベースにあるか
config.json の notify_tomorrow が true か
Windowsの通知設定がオンか
タスクスケジューラの引数に notify が付いているか


基本の運用手順
予定表を修正したとき:
python main.py import
python main.py show

通知を手動で確認したいとき:
python main.py notify

OCRから予定表を作るとき:
python ocr_cells.py
python ocr_cells_read.py

その後、ocr_result.csv をExcelで確認・修正し、garbage_schedule_2026_01.xlsx として保存します。



メモ
このアプリでは、ExcelまたはCSVを元データとして扱います。
Excel/CSV = 正しい予定表
garbage.db = アプリが使う保存場所

Excelを変更したら、必ず次を実行します。
python main.py import
