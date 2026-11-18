#!/usr/bin/env python3
"""Garmin Connect から直近のラン距離・スクワット/腕立て回数を取得し garmin.json に保存する。

使い方(リポジトリのルートで実行):
  初回(ログインしてトークンを保存):  python scripts/garmin_fetch.py --login
  2回目以降(自動実行用):            python scripts/garmin_fetch.py
  取得日数を変える:                  python scripts/garmin_fetch.py --days 14
  出力先を変える:                    python scripts/garmin_fetch.py --output path/to/garmin.json

必要: Python 3.12 以上 / pip install garminconnect
※ 非公式ライブラリを使用しています。Garmin側の仕様変更で動かなくなる場合があります。
"""

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from getpass import getpass
from pathlib import Path

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

# トークン(ログインの鍵)の保存先。パスワードは保存しない。
TOKEN_DIR = str(Path(os.getenv("GARMINTOKENS", "~/.garminconnect")).expanduser())
# 既定の出力先: リポジトリのルートの garmin.json(.gitignore で除外済み)
DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "garmin.json"
DEFAULT_DAYS = 30

# Garminの種目カテゴリ名 → ダッシュボードの項目
EXERCISE_MAP = {"SQUAT": "squat", "PUSH_UP": "pushup"}


def login(interactive: bool) -> Garmin:
    """保存済みトークンでログイン。--login 指定時のみメール/パスワードを聞く。"""
    try:
        api = Garmin()
        api.login(TOKEN_DIR)
        return api
    except GarminConnectTooManyRequestsError:
        sys.exit("アクセス制限中です。しばらく時間をおいて再実行してください。")
    except (GarminConnectAuthenticationError, GarminConnectConnectionError, FileNotFoundError):
        if not interactive:
            sys.exit("保存済みトークンが無効です。'python scripts/garmin_fetch.py --login' で再ログインしてください。")

    email = input("Garminのメールアドレス: ").strip()
    password = getpass("パスワード(表示されません): ")
    api = Garmin(email=email, password=password,
                 prompt_mfa=lambda: input("2段階認証コード: ").strip())
    api.login(TOKEN_DIR)
    print(f"ログイン成功。トークンを保存しました: {TOKEN_DIR}")
    return api


def type_key(activity: dict) -> str:
    return (activity.get("activityType") or {}).get("typeKey", "")


def count_reps(sets_response: dict) -> dict:
    """筋トレ1回分のセット一覧から、種目ごとの合計回数を数える。"""
    totals = {"squat": 0, "pushup": 0}
    for s in (sets_response or {}).get("exerciseSets") or []:
        if s.get("setType") != "ACTIVE":  # 休憩セットは除外
            continue
        reps = s.get("repetitionCount") or 0
        for ex in s.get("exercises") or []:
            key = EXERCISE_MAP.get(ex.get("category", ""))
            if key:
                totals[key] += reps
                break
    return totals


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--login", action="store_true", help="初回ログインを行う")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS,
                        help=f"何日分さかのぼって取得するか(既定: {DEFAULT_DAYS})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"出力先(既定: {DEFAULT_OUTPUT})")
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days は 1 以上を指定してください")

    api = login(interactive=args.login)

    end = date.today()
    start = end - timedelta(days=args.days - 1)
    activities = api.get_activities_by_date(start.isoformat(), end.isoformat())

    runs, strength = [], []
    for a in activities:
        tk = type_key(a)
        day = (a.get("startTimeLocal") or "")[:10]
        if "running" in tk:  # running / treadmill_running / trail_running など
            runs.append({
                "id": str(a["activityId"]),
                "date": day,
                "km": round((a.get("distance") or 0) / 1000, 2),
                "name": a.get("activityName") or "ラン",
            })
        elif tk == "strength_training":
            time.sleep(1)  # アクセスしすぎ防止
            try:
                sets = api.get_activity_exercise_sets(a["activityId"])
            except GarminConnectTooManyRequestsError:
                sys.exit("アクセス制限中です。しばらく時間をおいて再実行してください。")
            except GarminConnectConnectionError as e:
                # 1件の失敗で全体を止めない
                print(f"警告: 筋トレ {a['activityId']} のセット取得に失敗: {e}", file=sys.stderr)
                continue
            strength.append({"id": str(a["activityId"]), "date": day, **count_reps(sets)})

    runs.sort(key=lambda r: r["date"])
    strength.sort(key=lambda r: r["date"])

    data = {
        "updatedAt": datetime.now().isoformat(timespec="seconds"),
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "runs": runs,
        "strength": strength,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"保存しました: {args.output}(ラン {len(runs)}件 / 筋トレ {len(strength)}件)")


if __name__ == "__main__":
    main()
