<div align="center">

<img src=".github/assets/qinbridge.png" alt="琴桥 QinBridge" width="104">

# 琴桥在线曲库

**QinBridge Scores** · 下载、分享，让喜欢的旋律在琴桥中响起。

<a href="https://github.com/DZXH-TX/QinBridge-Scores/actions/workflows/score-check.yml"><img src="https://github.com/DZXH-TX/QinBridge-Scores/actions/workflows/score-check.yml/badge.svg?branch=main" alt="乐谱校验状态"></a>

`.qinscore` · UTF-8 JSON · 中文 / English

[中文乐谱](scores/zh-CN) · [English scores](scores/en-US) · [贡献指南](CONTRIBUTING.md) · [格式说明](docs/SCORE-FORMAT.md) · [许可说明](LICENSE.md)

</div>

---

琴桥的独立乐谱仓库。每份 `.qinscore` 保存一首曲子的谱面、BPM、拍号和演奏设置，更新曲库无需重新安装软件；下载到本地后，也可以离线使用。

## 参与琴桥

| 🎼 提交乐谱 · Pull Request | 💬 问题反馈 · Issues |
| --- | --- |
| 分享新乐谱，或提交已有乐谱的修订。 | 反馈软件故障、功能建议、使用疑问或乐谱问题。 |
| 随 PR 提交乐谱、目录，也可附上来源与署名说明。 | 选择反馈类型，补充现象、步骤或你的想法。 |
| **[提交乐谱 PR →](https://github.com/DZXH-TX/QinBridge-Scores/compare)** | **[创建反馈 Issue →](https://github.com/DZXH-TX/QinBridge-Scores/issues/new/choose)** |

第一次贡献乐谱？从 **[贡献指南](CONTRIBUTING.md)** 开始，跟着示例完成 Fork、添加文件、生成目录和提交 PR。

## 获取乐谱

**在琴桥中下载**：打开「在线曲库」→ 刷新目录 → 选择曲目 → 下载到本地曲库。

**从仓库下载**：选择下面的入口，打开 `.qinscore` 文件后点击 **Download raw file**，再到琴桥的「曲谱文件」页面导入。

| 中文曲库 | English library | 整库下载 |
| --- | --- | --- |
| [浏览中文乐谱](scores/zh-CN) | [Browse English scores](scores/en-US) | [下载仓库 ZIP](https://github.com/DZXH-TX/QinBridge-Scores/archive/refs/heads/main.zip) |

ZIP 解压后的乐谱位于 `scores/` 中。已下载的乐谱保留在本地，刷新在线目录不会覆盖你的本地编辑。

<details>
<summary>Download instructions in English</summary>

Open **[English scores](scores/en-US)**, choose a `.qinscore` file, and click **Download raw file**. Import it from QinBridge's score-file page, or download directly from the online library in the app. Downloaded songs remain available offline.

Submit scores through **Pull Requests**. Report bugs, suggestions, or questions through **Issues**.

</details>

## 中国大陆备用下载源

GitHub 是主下载源。中国大陆无法直连时，可使用 [雨云中文镜像](https://qinbridge-scores-cn.cn-nb1.rains3.com/catalog.json)。镜像仅包含 `scores/zh-CN/*.qinscore` 和重新生成的中文 `catalog.json`；英文曲谱、`.source.json` 随谱来源说明、溯源表、源码及其他文档均不上传。

工作流 [Sync mainland score mirror](https://github.com/DZXH-TX/QinBridge-Scores/actions/workflows/sync-mainland-mirror.yml) 在 `main` 的中文曲谱更新、自动合并流程成功完成后同步，也提供 `Run workflow` 手动入口。任务从最新 `main` 构建，经校验后先上传曲谱，再发布目录，最后逐一核对公开 HTTPS 下载内容。运行串行执行，已在目录中移除的歌曲不再出现在镜像目录里；任务不会自动删除桶内旧对象。

维护者在仓库的 Actions Secrets 中配置此镜像桶的 `RAINYUN_MIRROR_ACCESS_KEY_ID` 与 `RAINYUN_MIRROR_SECRET_ACCESS_KEY`。密钥仅在上传步骤使用。镜像地址为 `https://qinbridge-scores-cn.cn-nb1.rains3.com/`，S3 端点为 `https://cn-nb1.rains3.com`。

## 写出第一份乐谱

推荐先在琴桥中编辑、试听并导出，再提交到仓库。也可以从下面的示例开始：

| 文档 / 示例 | 你能找到什么 |
| --- | --- |
| [贡献指南](CONTRIBUTING.md) | 文件放在哪里、如何更新目录、怎样发起 PR |
| [格式说明](docs/SCORE-FORMAT.md) | 完整 JSON 示例、数字谱与键盘谱、节奏参数 |
| [数字谱示例](examples/numbers.qinscore) | 可导入的入门练习，包含单音、和弦、琶音与休止 |
| [键盘谱示例](examples/keyboard.qinscore) | 同一练习的键盘记谱版本 |

示例放在 `examples/`，供阅读和导入练习，不计入正式在线曲库。

## 问题与建议

此仓库的 Issues 同时接收 **琴桥软件** 与 **在线曲库** 的反馈。提交前可先[搜索已有反馈](https://github.com/DZXH-TX/QinBridge-Scores/issues)，相同问题可以补充到现有讨论中。

| 反馈内容 | 入口 |
| --- | --- |
| 软件报错、无法导入、下载失败、演奏异常，或某份乐谱有误 | [报告问题](https://github.com/DZXH-TX/QinBridge-Scores/issues/new?template=01-bug-report.yml) |
| 新功能、操作体验、界面或曲库改进建议 | [提出建议](https://github.com/DZXH-TX/QinBridge-Scores/issues/new?template=02-feature-request.yml) |
| 不清楚某项设置、格式规则或贡献步骤 | [使用咨询](https://github.com/DZXH-TX/QinBridge-Scores/issues/new?template=03-question.yml) |

报告故障时，请尽量提供琴桥版本、Windows 版本、复现步骤和相关截图；乐谱问题请附上文件名或链接。

## 校验与合并

提交 PR 后，GitHub Actions 会并行检查 JSON 格式、谱面、参数范围和目录一致性。**仅修改乐谱、目录及可选随谱来源说明，通过检查且满足分支保护规则的非草稿 PR，会由机器人批准并合并。**

校验器只将乐谱作为数据读取，不执行提交中的脚本。工作流、校验器、文档等变更由维护者审核。具体范围、限制和失败处理见[贡献指南](CONTRIBUTING.md#checks)。

## 许可与来源

| 对象 | 使用规则 |
| --- | --- |
| 仓库工具与 CI 代码 / 配置 | [标准 MIT](LICENSES/MIT.txt) |
| 本项目原创文档与示例 | [标准 CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| 正式乐谱 | 按各曲目的实际授权；CC 是可选项，CI 不要求或核验 CC |
| 琴桥软件本体 | [闭源专有软件，仅通过微软商店分发](SOFTWARE-LICENSE.md) |

开发者/发布者：**DZXH CR Tech**<br>
GitHub 账号：**DZXH-TX**<br>
说明：DZXH-TX 与 DZXH CR Tech 为同一开发者的 GitHub 账号与微软商店开发者身份。两份标准许可的适用范围见[许可说明](LICENSE.md)。

现有 28 份乐谱的出处、谱面对照和发现的授权声明，记录在[乐谱溯源表](docs/SCORE-PROVENANCE.md)。找到出处不等于取得授权，历史乐谱不会自动套用 CC。

---

请在乐谱的 `sourceUrl` 中保留来源链接，并在 PR 中说明作者、来源及分发授权情况。只提交你有权公开分享的乐谱。

[曲库目录](catalog.json) · [隐私说明](PRIVACY.md) · [许可说明](LICENSE.md) · [软件条款](SOFTWARE-LICENSE.md) · [查看 Pull Requests](https://github.com/DZXH-TX/QinBridge-Scores/pulls)
