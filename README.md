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
3. 将曲谱与目录一起提交到 `main` 分支。

目录入口：[catalog.json](https://raw.githubusercontent.com/DZXH-TX/QinBridge-Scores/main/catalog.json)。文件路径相对于仓库根目录，且必须位于 `scores/`。歌曲名称与谱面保持原样。

仓库只用于分发曲谱，不存放用户数据库、账户配置或软件安装包。曲谱的作者与来源请填写在文件的 `sourceUrl` 中；上传者应确认有权公开分发相应谱面。
