# 贡献乐谱

[返回首页](README.md) · [格式说明](docs/SCORE-FORMAT.md) · [查看 PR](https://github.com/DZXH-TX/QinBridge-Scores/pulls)

欢迎分享新乐谱，也欢迎修正错音、节奏和标题。**乐谱文件通过 Pull Request 提交；问题、建议和使用咨询通过 [Issues](https://github.com/DZXH-TX/QinBridge-Scores/issues/new/choose) 反馈。**

## 1. 准备一份可用的乐谱

在琴桥中编辑曲目并试听，保存谱面与节奏设置，然后在「曲谱文件」页面导出 `.qinscore`。

文件需要保留标题、谱面和演奏设置。如果手工编写，可以参考[数字谱示例](examples/numbers.qinscore)、[键盘谱示例](examples/keyboard.qinscore)和[字段说明](docs/SCORE-FORMAT.md)。

- 每个文件保存一首乐谱，使用 UTF-8 JSON。
- 有来源网页时，将 HTTP(S) 链接填入 `sourceUrl`；没有链接时保留空字符串。
- 在 PR 说明中补充作者、来源、适用游戏 / 乐器和分发授权情况。不要在 JSON 中自行增加 `author`、`game` 等字段，当前格式不接受这些字段。
- 一种语言的版本即可提交，不要求同时提供中英文。

## 2. Fork 仓库并创建分支

在本仓库页面点击 **Fork**，创建到你的 GitHub 账户。使用 Git 和 Python 3.10 或更新版本，在本地克隆自己的 Fork；校验工具只使用 Python 标准库，无需额外安装依赖。

将下面的 `YOUR_NAME` 替换为你的 GitHub 用户名：

```console
git clone https://github.com/YOUR_NAME/QinBridge-Scores.git
cd QinBridge-Scores
git switch -c scores/add-my-song
```

已有 Fork 时，先与本仓库的 `main` 同步，再创建本次提交的分支。

## 3. 放入对应语言目录

```text
scores/
├── zh-CN/
│   └── 我的乐谱.qinscore
└── en-US/
    └── My Song.qinscore
```

| 内容 | 放置位置 |
| --- | --- |
| 中文标题版本 | `scores/zh-CN/` |
| 英文标题版本 | `scores/en-US/` |

文件名应便于识别，文件内的 `title` 使用对应语言。请直接放在语言目录下，不再建立子目录；文件名不要使用 `\ : * ? " < > |`，也不要以 `.` 开头。

修订已有曲目时，直接编辑原文件。若要更换文件名，应移除旧文件，并在下一步重新生成目录。

## 4. 生成目录并提交

在仓库根目录运行：

```console
python -I tools/build_catalog.py
git diff --stat
git add scores catalog.json
git commit -m "Add a score"
python -I tools/validate_scores.py --workers 4
```

`build_catalog.py` 会检查工作区的乐谱并生成 `catalog.json`，目录中的 ID、标题、路径和语言由脚本填写，不需要手工编辑。

**最后一条命令验证的是刚刚创建的 Git 提交。** 所以要先 `git commit`，再运行它；只修改文件而未提交时，它仍会读取旧版本。

如果校验失败，按提示修正乐谱，重新生成目录并提交，再次运行校验。看到类似下面的结果且命令成功退出，就可以推送：

```json
{"scores": 29, "bytes": 102400, "data_only": false}
```

这里的数量与字节数只是示意。未指定 `--base` 时，`data_only` 为 `false` 是正常的，不代表校验失败；GitHub 会在 PR 中比较变更范围。

## 5. 发起 Pull Request

```console
git push -u origin scores/add-my-song
```

回到你的 Fork，点击 **Contribute → Open pull request**。也可以从本仓库的 [New pull request](https://github.com/DZXH-TX/QinBridge-Scores/compare) 进入，选择 **compare across forks**。

- **base repository**：`DZXH-TX/QinBridge-Scores`
- **base**：`main`
- **head repository**：你的 Fork
- **compare**：`scores/add-my-song`

PR 标题可以写“新增《曲名》中文乐谱”或“修正《曲名》的节奏”。说明中写清楚：

1. 新增或修订了哪些曲目。
2. 作者、来源链接与分发授权情况。
3. 是否已在琴桥中导入、试听，以及适用的游戏 / 乐器。
4. 修订已有乐谱时，具体改了什么。

贡献乐谱时，只提交相应 `.qinscore` 和 `catalog.json`。准备好后，将草稿 PR 标记为 **Ready for review**。

<a id="checks"></a>

## 校验与合并规则

```text
发起 PR → 检查曲谱与目录 → 独立复核当前提交 → 自动批准 → 合并
```

自动流程最多使用 4 个进程并行解析曲谱。只有同时满足以下条件时，PR 才会自动批准、合并：

- 变更仅涉及 `catalog.json`、`scores/zh-CN/*.qinscore`、`scores/en-US/*.qinscore`，且不超过 200 个文件。
- 完整目录与全部曲谱一致，JSON、谱面和参数校验通过。
- PR 不是草稿，分支已更新至最新 `main`。
- 没有待处理的“请求更改”，并满足必需检查、审批和会话解决等分支保护规则。

工作流、工具、文档等变更由维护者审核。GitHub 要求首次贡献者授权运行 Actions 时，需要等待维护者批准运行。

PR 有新提交后会重新检查，旧批准失效。主分支更新后，请同步最新 `main` 到你的分支，解决冲突、重新生成目录并提交；已修复的审查意见仍需要标记为解决。如果条件满足后合并任务仍未继续，可在 Actions 中重新运行相关检查，或请维护者处理。

### 常见校验失败

| 提示 / 现象 | 处理方式 |
| --- | --- |
| `Unknown JSON fields` | 删除格式未定义的字段；来源、作者等补充信息写在 PR 说明中 |
| `Duplicate JSON key` | 同一个对象中不能重复填写同名字段 |
| `Catalogue must exactly match` | 重新运行 `build_catalog.py`，将曲谱与目录一起提交 |
| `Invalid keyboard note` / `Invalid numeric note` | 检查记谱方式与 `settings.score.notation` 是否一致 |
| `Duplicate simultaneous note` | 同一时刻的和弦不能重复触发同一个音符 |
| 数值、文件大小或分组深度超限 | 对照[格式说明与限制](docs/SCORE-FORMAT.md#limits)调整 |
| `PR must be updated with main` | 合并最新 `main`，重新生成目录并提交 |

<details>
<summary>维护者：校验实现与仓库设置</summary>

`Score checks` 使用只读权限。独立的 `workflow_run` 流程从主分支加载校验器，重新验证当前 PR 的固定提交。候选文件只从 Git blob 读取，不检出或执行 PR 中的脚本，也不读取上游工作流的产物或缓存。批准任务只接收固定 SHA 和校验结论，并在提交审批和合并时再次核对 PR。

`main` 要求 `qinbridge/score-security` 检查、一份批准及适用的 CODEOWNERS 审核；开启旧批准失效、分支保持最新和会话解决要求，禁止强推和删除。维护者保留管理员手动处理权限。

仓库允许 GitHub Actions 批准 PR，默认工作流权限保持只读。仓库的“允许自动合并”开关开放 GitHub 原生功能；当前自动流程通过 API 直接合并，无需再为每个 PR 手动启用原生自动合并。

修改校验器时运行回归测试：

```console
python -I -m unittest discover -s tools/tests -v
```

参考：[GitHub workflow_run 文档](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run) · [GitHub Actions 安全指南](https://docs.github.com/en/actions/reference/security/secure-use)。

</details>
