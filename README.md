# Garmin Motivation Dashboard

Garmin のデータを可視化して、日々のトレーニングのモチベーションを上げるためのダッシュボード。

## 概要

<!-- このプロジェクトで何ができるか -->

## 機能

- [x] Garmin Connect からのデータ取得（直近30日のラン距離・スクワット/腕立て回数）
- [x] 毎晩 23:00 の自動取得（macOS LaunchDaemon）
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

### 自動実行（macOS）

`scripts/run.sh` が取得スクリプトを実行し、結果を `logs/fetch.log` に追記します。
LaunchDaemon で毎晩 23:00 に実行するには次の手順で設置します。

1. 先に `python scripts/garmin_fetch.py --login` でトークンを保存し、`./scripts/run.sh` が手動で成功することを確認する。
2. リポジトリは `~/garmin-dashboard` に置く（`~/Documents`・`~/Desktop`・`~/Downloads` の下は macOS のプライバシー保護で launchd から読めないため避ける）。
3. ひな形の `YOUR_USERNAME` を自分のユーザー名に置き換えて設置する。

```bash
sed "s/YOUR_USERNAME/$(whoami)/g" scripts/com.example.garmin-dashboard.plist | sudo tee /Library/LaunchDaemons/com.example.garmin-dashboard.plist > /dev/null
sudo chown root:wheel /Library/LaunchDaemons/com.example.garmin-dashboard.plist
sudo chmod 644 /Library/LaunchDaemons/com.example.garmin-dashboard.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.example.garmin-dashboard.plist
```

動作確認（今すぐ1回実行）:

```bash
sudo launchctl kickstart system/com.example.garmin-dashboard
tail logs/fetch.log
```

停止・削除:

```bash
sudo launchctl bootout system/com.example.garmin-dashboard
sudo rm /Library/LaunchDaemons/com.example.garmin-dashboard.plist
```

- リポジトリを別の場所に置いた場合は、plist 内の `/Users/YOUR_USERNAME/garmin-dashboard` も書き換えてください。
- 使う Python は `PYTHON` 環境変数 → `.venv/bin/python` → `python3` の順で探します。
- Mac がスリープ中に 23:00 を過ぎた場合は、復帰後に1回実行されます。電源が切れていた場合は実行されません。
- トークンが切れると `logs/fetch.log` に再ログインの案内が出ます。`--login` で取り直してください。

### ダッシュボード表示

<!-- TBD -->

## 設定

<!-- 認証情報・設定ファイルの置き場所 -->

> **注意:** `garmin.json`、`.garminconnect`、`rclone.conf` には認証情報や個人データが含まれるため、`.gitignore` でリポジトリから除外しています。

## ディレクトリ構成

```
scripts/garmin_fetch.py  Garmin からデータを取得して garmin.json を出力
scripts/run.sh           取得スクリプトを実行してログを残す（自動実行用）
scripts/com.example.garmin-dashboard.plist  毎晩 23:00 に run.sh を実行する LaunchDaemon のひな形
requirements.txt         Python 依存パッケージ
```

## ライセンス

<!-- TBD -->
