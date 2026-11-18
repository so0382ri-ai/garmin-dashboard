# Garmin Motivation Dashboard

Garmin のデータを可視化して、日々のトレーニングのモチベーションを上げるためのダッシュボード。

## 概要

<!-- このプロジェクトで何ができるか -->

## 機能

- [x] Garmin Connect からのデータ取得（直近30日のラン距離・スクワット/腕立て回数）
- [ ] ダッシュボード表示
- [ ] 

## セットアップ

Python 3.12 以上が必要です。

```bash
pip install -r requirements.txt
```

## 使い方

### データ取得

初回はログインしてトークンを `~/.garminconnect` に保存します（パスワードは保存しません）。

```bash
python scripts/garmin_fetch.py --login
```

2回目以降は保存済みトークンで取得します（自動実行向け）。リポジトリ直下に `garmin.json` が出力されます。

```bash
python scripts/garmin_fetch.py
```

オプション: `--days N`（取得日数、既定 30）、`--output PATH`（出力先）。
トークンの保存先は環境変数 `GARMINTOKENS` で変更できます。

> 非公式ライブラリ [garminconnect](https://pypi.org/project/garminconnect/) を使用しています。Garmin 側の仕様変更で動かなくなる場合があります。

### garmin.json の形式

```json
{
  "updatedAt": "2026-11-18T07:00:00",
  "range": { "start": "2026-10-20", "end": "2026-11-18" },
  "runs":     [{ "id": "123", "date": "2026-11-10", "km": 5.23, "name": "朝ラン" }],
  "strength": [{ "id": "456", "date": "2026-11-09", "squat": 45, "pushup": 15 }]
}
```

### ダッシュボード表示

<!-- TBD -->

## 設定

<!-- 認証情報・設定ファイルの置き場所 -->

> **注意:** `garmin.json`、`.garminconnect`、`rclone.conf` には認証情報や個人データが含まれるため、`.gitignore` でリポジトリから除外しています。

## ディレクトリ構成

```
scripts/garmin_fetch.py  Garmin からデータを取得して garmin.json を出力
requirements.txt         Python 依存パッケージ
```

## ライセンス

<!-- TBD -->
