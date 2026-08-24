"""
Long-running daemon that scrapes ldsport.com once a day and refreshes
real_rosters_202627.py / draft_picks_data.py via refresh_ldsport_data.run().

This script IS the scheduler -- no cron, no launchd, no OS-level config,
no Claude Code involvement. Start it once and leave it running; it wakes up
once every 24 hours (at RUN_HOUR local time) and runs the refresh.

Usage:
    python3 -m src.daily_ldsport_refresh

It only runs while this process is alive, so start it under something that
survives closing the terminal, e.g.:
    nohup python3 -m src.daily_ldsport_refresh >> src/ldsport_daemon.log 2>&1 &
or inside tmux/screen. It does not restart itself after a reboot -- if the
machine restarts, restart this process the same way.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta

from src.refresh_ldsport_data import run

RUN_HOUR = 6  # local 24h clock
RUN_MINUTE = 0


def _seconds_until_next_run(now: datetime | None = None) -> float:
    now = now or datetime.now()
    target = now.replace(hour=RUN_HOUR, minute=RUN_MINUTE, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def _log(msg: str) -> None:
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}", flush=True)


def main() -> None:
    _log(f"daily_ldsport_refresh starting, will run daily at {RUN_HOUR:02d}:{RUN_MINUTE:02d} local time")
    while True:
        wait = _seconds_until_next_run()
        _log(f"sleeping {wait / 3600:.1f}h until next refresh")
        time.sleep(wait)
        _log("running refresh")
        try:
            run()
        except SystemExit:
            pass  # run() exits(1) on fetch/sanity failure; already logged by run(), keep the daemon alive
        except Exception as e:
            _log(f"refresh crashed: {e!r}")
        _log("refresh cycle complete")


if __name__ == "__main__":
    main()
