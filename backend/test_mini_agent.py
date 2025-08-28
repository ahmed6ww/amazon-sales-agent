#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.local_agents.research.mini_agent import MiniResearchRunner


def main():
    asin_or_url = sys.argv[1] if len(sys.argv) > 1 else "B08KT2Z93D"
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set; agent run will fail. Set it and retry.")
        return

    runner = MiniResearchRunner()
    res = runner.run(asin_or_url)
    print(res["final_output"])


if __name__ == "__main__":
    main() 