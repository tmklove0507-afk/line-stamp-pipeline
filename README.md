# line-stamp-pipeline

LINEスタンプの「仕上げ」を自動化するパイプライン。
AI生成した白背景イラストを、**透過処理 → 文字合成 → LINE規格リサイズ → ZIP化**まで一括で処理する。

## できること / できないこと

- ✅ できる：スタンプ画像の仕上げ一式（このリポジトリの範囲）
  - 四隅フラッドフィルで白背景だけを透過
  - 丸ゴシック太字（Zen Maru Gothic Bold）で言葉を合成
  - LINE規格にリサイズ：スタンプ最大370×320（縦横とも偶数）／メイン240×240／タブ96×74
  - 出品用ZIP（`stamps.zip`）を作成
- ❌ できない：LINEクリエイターズマーケットへのアップロードと審査リクエスト
  - 出品用の公式APIがないため、ここは手作業（数分）。申請時は「AIの使用」の申告が必要
  - 審査通過後の販売開始は、クリエイターズマーケット側の「自動で販売を開始」設定で半自動化できる

## 使い方（ローカル）

```bash
pip install -r requirements.txt
```

フォント：`tools/fonts/ZenMaruGothic-Bold.ttf` を配置する（Google Fonts配布、SIL Open Font License。GitHub Actionsでは自動取得するので不要）。

`mapping.json` を用意する：

```json
[
  {"num": 1, "src": "path/to/img1.webp", "text": "おはよう"},
  {"num": 2, "src": "path/to/img2.webp", "text": "ありがとう"}
]
```

実行：

```bash
python3 tools/finish_stamps.py --map mapping.json --out build/set1 --base path/to/base.png
```

- `--base`：メイン画像／タブ画像の元になるイラスト（省略可）
- 出力：`01.png`〜（370×320以内）、`main.png`（240×240）、`tab.png`（96×74）、`stamps.zip`

## 使い方（GitHub Actions）

1. `sets/<セット名>/` に元画像と `mapping.json` を置いてコミットする（`mapping.json` の `src` はリポジトリ相対パスで書く）
2. Actionsタブ → **finish-stamps** → Run workflow → `set_dir` に `sets/<セット名>` を入力（メイン／タブの元画像がある場合は `base` にそのパスも入力）
3. 実行が終わったら Artifacts から `stamps.zip` をダウンロードする
4. LINEクリエイターズマーケットに手動でアップロードし、AI使用を申告して審査リクエストを送る

## 実績

このパイプラインで4セットを制作。

- 第1弾「ダルかわ夫婦の子育て連絡スタンプ」（完成・未登録）
- 第2弾 ほのぼの系（完成・未登録）
- アニメ系「ふんわり彼女と黒子猫の毎日スタンプ」（販売中）
- ぷにずかん「かくれもちの変身スタンプ」（販売中）
