import os
import sys
import argparse

# プロジェクトルートのパス指定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tasks.snapshot_task import run_snapshot
from src.tasks.ranking_task import run_ranking
from src.tasks.daily_report_task import run_daily_report

def main():
    parser = argparse.ArgumentParser(description="Commodity Bot Controller")
    parser.add_argument("--mode", type=str, choices=["snapshot", "ranking", "daily_report"], required=True)
    args = parser.parse_args()

    print(f"[START] モード実行: {args.mode}")

    if args.mode == "snapshot":
        run_snapshot()
    elif args.mode == "ranking":
        run_ranking()
    elif args.mode == "daily_report":
        run_daily_report()

    print(f"[END] 処理完了: {args.mode}")

if __name__ == "__main__":
    main()
