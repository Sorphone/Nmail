"""pytest 共享夹具：把数据目录指到一次性临时目录，绝不触碰真实用户数据。

必须在任何 app 模块导入前设置环境变量（get_data_dir/get_db_path 按调用时读）。

⚠️ 这里**必须无条件覆盖**，不能用 setdefault：shell 里若已导出 `NMAIL_DATA_DIR`
（本机是常态——`D:\\Nmail\\NmailData` 就设在用户级环境变量里），setdefault 会让
整轮测试直接跑在**真实邮箱库**上。2026-10-13 实惨：一次全量 pytest 把用户两个
真实账号连同 8000 余封邮件缓存级联删除（test_account_cleanup 会遍历账号逐个
DELETE），只能事后从空闲页雕刻找回。改回 setdefault = 重新打开这个坑。
"""
from __future__ import annotations

import os
import tempfile

_PYTEST_DATA_DIR = tempfile.mkdtemp(prefix="nmail-pytest-")
os.environ["NMAIL_DATA_DIR"] = _PYTEST_DATA_DIR

# 双保险：夹具目录必须是临时目录，否则就地失败（宁可测试跑不起来，也不碰真实库）
assert "nmail-pytest-" in _PYTEST_DATA_DIR, _PYTEST_DATA_DIR
