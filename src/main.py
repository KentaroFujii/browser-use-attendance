#!/usr/bin/env python3
"""
勤怠管理システム自動確認プログラム
メインエントリーポイント
"""

import asyncio
from dotenv import load_dotenv
from core.browser_agent import AttendanceAgent

# 環境変数を読み込み
load_dotenv()

def main():
    """
    メインエントリーポイント
    """
    agent = AttendanceAgent()
    asyncio.run(agent.run())


if __name__ == "__main__":
    main()
