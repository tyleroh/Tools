# Qinglong 青龙面板脚本

存放可直接导入青龙面板运行的签到 / 任务脚本。

## 脚本列表

| 脚本 | 说明 | 环境变量 | 建议定时 |
|---|---|---|---|
| `yadea_signin.py` | 雅迪智行每日签到（含积分/连续签到天数查询，结果推送青龙通知渠道） | `YADEA_TOKEN` | `30 7 * * *` |

## 使用说明

1. 青龙面板 → 脚本管理 → 新建 / 上传脚本，或直接 `ql repo` 拉取本目录。
2. 依赖安装（若镜像未自带）：`requests`、`pycryptodome`（无则自动回退 `cryptography`）。
3. 环境变量 → 新建 `YADEA_TOKEN`，值为抓包中 `Authorization: Bearer` 后面的 token；多账号用 `&` 或换行分隔。
4. 定时任务 → 添加任务，命令 `task yadea_signin.py`。

### yadea_signin.py

- 来源：qd-today 模板 `雅迪智行每日签到.har` 的 Python 复刻。
- 签名算法：AES-128-ECB，key `RFC1J02e116b45a0`，`gatewaySign = base64(AES("gatewayTimestamp=<13位毫秒>&json={}"))`。
- 响应体为 urlencode 过的 base64 密文，同 key 解密；`code=000000` 成功，`120168` 表示已签到。
- token 会过期，失效后重新抓包更新环境变量即可。

## 抓包提示

抓取 App（`YadeaApp/8.8.10`）对 `tspapph5.yadeaiot.com.cn` 的任意请求，复制请求头 `Authorization` 中 `Bearer ` 之后的部分。

## 通知（Telegram 收不到？）

脚本用青龙内置 `notify` 模块推送，**必须在青龙里配好通知渠道**才会收到消息：

1. 系统设置 → 通知设置 → 添加 → 选 Telegram → 填 `Bot Token` 与 `User ID` → 保存后点「测试」。
   - `User ID` 必须是**数字 chat_id**（群组为负数），不是 `@username`。
   - 获取方法：先给机器人发一条 `/start`，再访问
     `https://api.telegram.org/bot<TOKEN>/getUpdates`，取 `result[].message.chat.id`。
2. 或在环境变量里加 `TG_BOT_TOKEN`、`TG_USER_ID`。
3. 渠道必须处于**启用**状态；脚本不调用 `notify.send()` 则不会有任何推送。
