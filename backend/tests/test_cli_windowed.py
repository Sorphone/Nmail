"""窗口化启动回归（PyInstaller console=False）：sys.stdout/stderr 为 None 时不得崩。

2026-10-13 实踩：窗口化冻结构建里 sys.stdout 是 None，uvicorn 0.54 的
ColourizedFormatter.__init__ 直接调 sys.stdout.isatty() → AttributeError，
被 logging dictConfig 包成 `ValueError: Unable to configure formatter 'default'`，
双击 exe 只弹「Nmail 启动失败」（终端渠道 sys.stdout 非 None，从不复现）。
入口 cli.main 现在第一件事就是 ensure_std_streams()，本文件守住这道护栏。
"""
from __future__ import annotations

import os
import sys

import uvicorn

from app import cli


def test_ensure_std_streams_fills_none(monkeypatch):
    """两个流为 None（窗口化）时接到 devnull；非 None 时不得改写。"""
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)

    cli.ensure_std_streams()

    assert sys.stdout is not None and sys.stderr is not None
    assert sys.stdout.name == os.devnull
    assert sys.stderr.name == os.devnull


def test_uvicorn_formatter_constructible_after_guard(monkeypatch):
    """护栏生效后 uvicorn 的彩色 formatter 能构造出来——这正是原崩溃点。"""
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)

    cli.ensure_std_streams()

    uvicorn.logging.DefaultFormatter()  # 未接 devnull 时抛 AttributeError
    uvicorn.logging.AccessFormatter('%(client_addr)s')  # 同理，uvicorn.access 用
