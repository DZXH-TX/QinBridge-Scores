# 许可说明

开发者/发布者：**DZXH CR Tech**<br>
GitHub 账号：**DZXH-TX**<br>
说明：DZXH-TX 与 DZXH CR Tech 为同一开发者的 GitHub 账号与微软商店开发者身份。

Copyright (c) 2026 DZXH CR Tech<br>
更新日期：2026-10-08

其他贡献者及第三方权利人保留各自权利。

## 先确认使用的是哪一部分

| 内容 | 适用许可 / 规则 |
| --- | --- |
| `tools/` 中的工具与测试代码，`.github/workflows/`、`.github/ISSUE_TEMPLATE/`、`.github/CODEOWNERS`、`.gitignore` 中的本项目代码与配置 | 标准 [MIT License](LICENSES/MIT.txt) |
| `README.md`、`CONTRIBUTING.md`、`PRIVACY.md`、`docs/` 中本项目原创说明文字，以及 `examples/` 中本项目原创示例 | 标准 [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt)，仅覆盖本项目有权授权的部分 |
| `scores/` 中的正式乐谱及随谱来源说明 | 按每份作品的实际声明与权利人授权；**CC BY-SA 4.0 是可选项，不是投稿条件** |
| `catalog.json` | 曲库索引；列入索引不代表其中乐谱已获得任何统一许可 |
| 琴桥软件本体、专有程序与安装包 | [琴桥专有软件使用与分发条款](SOFTWARE-LICENSE.md)：闭源，仅经开发者的 Microsoft Store 官方条目分发 |
| 琴桥名称、图标及品牌素材，包括 `.github/assets/qinbridge.png` | 不随上述 MIT 或 CC 许可授予品牌素材使用权；依法允许的识别、引用不受影响 |

`LICENSES/` 保存标准许可证正文。MIT 仅填写版权年份和署名；CC 正文直接采用 Creative Commons 官方文本，没有加入自定义限制。本文件是适用范围说明，不修改两份标准许可证。

## 使用 MIT 工具代码

MIT 允许使用、复制、修改、分发和商业利用这些工具代码。再分发时保留 MIT 正文要求的版权与许可声明；具体条件及免责条款见[完整文本](LICENSES/MIT.txt)。

本仓库开放工具代码的授权不覆盖琴桥软件本体，也不表示所有乐谱采用 MIT。

## 使用 CC BY-SA 4.0 内容

对于明确采用 CC BY-SA 4.0 的内容，可以在遵守条款的条件下分享、改编及商业利用。分享时保留适用的署名、来源及许可信息，注明修改；公开分享改编内容时依标准许可履行相同方式共享要求。

原始项目文档与示例的署名为 **DZXH CR Tech**（GitHub 账号：**DZXH-TX**），来源为[本仓库](https://github.com/DZXH-TX/QinBridge-Scores)。另有署名的内容应保留相应创作者、贡献者与来源记录。

许可一经有效授予，不能通过随后修改仓库说明撤回已经授予的 CC 权利。软件的商店分发限制不适用于按 MIT 或 CC 合法取得的独立工具、文档及内容。以上是阅读指引，具体以 [CC BY-SA 4.0 标准正文](LICENSES/CC-BY-SA-4.0.txt)为准。

## 乐谱采用什么许可？

乐谱作者可以选择 CC BY-SA 4.0、其他适用许可，或不在投稿中填写许可字段。**未填写不等于 CC，也不等于自动取得再分发、改编或商业使用授权。** 用户应依据实际权利人的许可使用。

只有原创作者或有权作出相应授权的人，才能为作品声明 CC 许可。转写为键盘谱、改编曲目或仅提供来源链接，不会自动取得原曲及原编配的版权。提交者应确认自己有权公开提交该内容，并保留已有署名与许可要求。

现有 28 份正式曲谱不因本次添加许可证而统一变为 CC 内容。其出处、匹配证据与发现的授权声明见[现有乐谱溯源记录](docs/SCORE-PROVENANCE.md)；谱面来源和许可状态分别记录。

可以使用可选的 `曲名.qinscore.source.json` 保存来源、署名及许可文字，写法见[格式说明](docs/SCORE-FORMAT.md#source-notes)。它与对应乐谱放在同一目录，不进入软件曲库目录。

## CI 的检查范围

CI 检查数据结构、谱面、路径、文件大小、目录一致性，以及随谱说明是否对应真实乐谱。**CI 不要求填写 `license`，不要求使用 CC，不核验授权真伪，也不会仅因缺少 CC 标记而拒绝或停止自动合并。**

公开展示作品、自动校验通过或自动合并，都不代替权利人的授权。来源或署名需要更正时，可通过 [Issues](https://github.com/DZXH-TX/QinBridge-Scores/issues/new/choose) 提供作品链接和更正依据。

## 原文与相关说明

- [MIT 官方文本](https://opensource.org/license/mit)
- [CC BY-SA 4.0 官方正文](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en) · [官方纯文本](https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt)
- [Creative Commons FAQ](https://creativecommons.org/faq/)
- [琴桥软件使用与分发条款](SOFTWARE-LICENSE.md)
