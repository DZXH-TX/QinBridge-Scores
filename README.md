# 琴桥在线曲库 · QinBridge Scores

用于琴桥 QinBridge 的独立曲谱下载仓库。首批包含 14 首曲谱的中文、英文版本，共 28 个文件。每首曲谱采用 `.qinscore` 文件，保留谱面、BPM、拍号和触发间隔，更新曲库无需重新安装软件。

## 下载 / Download

- 在琴桥的「在线曲库」页面刷新目录，选择曲谱后下载到本地曲库。
- 也可在 [中文曲谱](scores/zh-CN) 或 [English scores](scores/en-US) 目录打开文件，点击 **Download raw file**，然后从琴桥的「曲谱文件」页面导入。
- [下载全部曲谱 ZIP](https://github.com/DZXH-TX/QinBridge-Scores/archive/refs/heads/main.zip)

Downloads are saved as local songs. Existing local edits are preserved, and downloaded songs remain available offline.

## 维护目录

1. 从琴桥导出正式的 `.qinscore` 文件，放进 `scores/zh-CN/` 或 `scores/en-US/`。文件内 `title` 使用对应语言。
2. 运行 `python tools/build_catalog.py`，更新 `catalog.json`。
3. 将曲谱与目录一起提交到新分支，向 `main` 发起 PR。检查通过的纯曲谱 PR 会自动批准并合并。

目录入口：[catalog.json](https://raw.githubusercontent.com/DZXH-TX/QinBridge-Scores/main/catalog.json)。文件路径相对于仓库根目录，且必须位于 `scores/`。歌曲名称与谱面保持原样。

仓库只用于分发曲谱，不存放用户数据库、账户配置或软件安装包。曲谱的作者与来源请填写在文件的 `sourceUrl` 中；上传者应确认有权公开分发相应谱面。

## PR 校验与自动合并

- GitHub Actions 使用最多 4 个独立进程并行解析 `.qinscore` JSON，只接受规定的数据字段、谱面语法和设置范围。拒绝重复键、未知字段、非有限数值、脚本内容、符号链接和可执行文件。
- 每个曲谱最多 4 MiB，目录最多 1 MiB，最多 2000 首，合计最多 64 MiB；JSON 嵌套最多 12 层，音符分组最多 32 层、10 万个音符，并限制分组展开计算量。
- `catalog.json` 必须与全部曲谱的路径、标题、语言和排序完全一致。曲谱来源只接受空值或 HTTP(S) 地址，校验时不访问来源网址。
- 只有仅修改 `catalog.json`、`scores/zh-CN/*.qinscore`、`scores/en-US/*.qinscore` 且不超过 200 个文件的非草稿 PR，才会自动批准和 squash 合并。工作流、校验器、文档等变更交由维护者审核。
- `Score checks` 使用只读权限；独立的 `workflow_run` 流程从主分支加载校验器，再次验证当前 PR 的固定提交。候选文件只从 Git blob 读取，从不检出或执行 PR 中的脚本，也不读取上游工作流的产物或缓存。具有写权限的批准任务只接收固定 SHA 和校验结论。
- `main` 要求 `qinbridge/score-security` 检查、一份批准及适用的 CODEOWNERS 审核，旧批准随新提交失效，分支必须更新至最新 `main`，禁止强推和删除。维护者保留管理员手动处理权限；自动流程不会绕过保护规则，也不会覆盖人工的“请求更改”。

本地维护曲谱仓库时，可运行以下命令；这些校验只属于曲谱 Git 仓库，不涉及琴桥客户端：

```console
python -I tools/build_catalog.py
python -I -m unittest discover -s tools/tests -v
python -I tools/validate_scores.py --workers 4
```

最后一条验证当前 **Git 提交**，而不是未提交的工作区。Actions 固定验证 PR 的 head SHA；PR 或主分支发生变化后需要重新检查。首次贡献者的 Actions 运行如被 GitHub 要求授权，由维护者在 GitHub 中批准运行。

仓库设置需允许 GitHub Actions 批准 PR，默认工作流权限保持只读。安全流程参考 [GitHub workflow_run 文档](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run) 和 [GitHub Actions 安全指南](https://docs.github.com/en/actions/reference/security/secure-use)。
