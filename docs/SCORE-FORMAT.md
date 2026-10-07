# 乐谱格式与示例

[返回首页](../README.md) · [贡献指南](../CONTRIBUTING.md) · [下载数字谱示例](../examples/numbers.qinscore) · [下载键盘谱示例](../examples/keyboard.qinscore)

`.qinscore` 是保存一首乐谱的 UTF-8 JSON 文件。可以用文本编辑器查看，也可以直接从琴桥导出。它保存曲目与演奏参数，不包含可执行脚本。

## 一份完整的数字谱

下面的示例与 [`examples/numbers.qinscore`](../examples/numbers.qinscore) 一致。保存为 `.qinscore` 后，可以在琴桥的「曲谱文件」页面导入。

```json
{
  "format": "qinbridge.score",
  "version": 1,
  "title": "入门练习 · 数字谱",
  "sourceUrl": "",
  "scoreText": "1 /2 /3 /4 /\n5 /6 /7 /+1 /\n[123] /(1+1) /0 /1 /",
  "settings": {
    "slotMilliseconds": 125,
    "arpeggioMilliseconds": 18,
    "gate": 0.72,
    "rhythm": {
      "bpm": 120,
      "beatsPerBar": 4,
      "beatUnit": 4,
      "unitsPerBeat": 4
    },
    "score": {
      "notation": "Numbers",
      "timing": "SlashBeats",
      "ignoreMeasureNumbers": false
    },
    "minimumTriggerIntervalMilliseconds": 150
  }
}
```

JSON 字符串中的 `\n` 表示换行。字段名区分大小写；数值不加引号，布尔值使用 `true` / `false`。不支持注释、尾随逗号、重复键或未定义字段。

## 顶层字段

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `format` | 是 | 固定为 `"qinbridge.score"` |
| `version` | 是 | 当前固定为整数 `1` |
| `title` | 是 | 非空曲名，最多 256 个字符；语言与投稿目录对应 |
| `sourceUrl` | 否 | 来源 HTTP(S) 地址，或空字符串；最多 2048 个字符 |
| `scoreText` | 是 | 非空谱面文本，至少包含一个音符 |
| `settings` | 是 | 演奏设置对象，推荐完整保留软件导出的值 |

标题、来源等元数据不接受控制字符。作者、适用游戏和分发授权情况写在 **PR 说明** 中，不要自行加入 JSON 字段。来源网址仅作为资料保存，仓库校验时不会访问它。

## 数字谱与键盘谱

`settings.score.notation` 可使用 `Numbers`、`Keyboard` 或 `Auto`。提交时推荐明确选择前两者，便于核对谱面。

| 音区 | 数字谱 | 键盘谱 |
| --- | --- | --- |
| 低音 | `-1 -2 -3 -4 -5 -6 -7` | `Z X C V B N M` |
| 中音 | `1 2 3 4 5 6 7` | `A S D F G H J` |
| 高音 | `+1 +2 +3 +4 +5 +6 +7` | `Q W E R T Y U` |

| 写法 | 数字谱示例 | 键盘谱示例 | 含义 |
| --- | --- | --- | --- |
| 单音 | `1` | `A` | 触发一个音符 |
| 和弦 | `(1+1)` | `(AQ)` | 同时触发括号内音符 |
| 琶音 | `[123]` | `[ASD]` | 依次触发方括号内音符 |
| 休止 | `0` | `0` | 占据一个休止位置；键盘谱也可写 `-` |
| 分组嵌套 | `[(1+1)(2+2)]` | `[(AQ)(SW)]` | 依次触发两组和弦 |

同一时刻不能重复同一个音符，例如 `(AA)` 无效。分组需要在同一行配对，休止和 `/` 分隔符放在分组外。

**键盘谱中的字母表示音符位置。** 软件根据当前所选乐器的按键映射演奏，文件本身不携带游戏按键配置。

## 节奏与演奏参数

`settings.score.timing` 有两种模式：

- **`SlashBeats`**：`/` 分隔每一拍，同一拍内的音符按谱面分配时长。示例 `1 /2 /3 /4 /` 表示四拍。
- **`SpaceGrid`**：按音符组和空格计算格数；连续空格会影响时间位置，不要随意压缩空白。`/` 不作为拍分隔。

`ignoreMeasureNumbers` 默认为 `false`。谱面带有行尾小节编号时，可以在确认其格式后设为 `true`；推荐使用软件试听后导出的设置。

| 字段 | 范围 / 可选值 | 说明 |
| --- | --- | --- |
| `settings.slotMilliseconds` | 20–2000 | 未提供 `rhythm` 时使用的每格毫秒数 |
| `settings.arpeggioMilliseconds` | 1–100 | 琶音间隔，单位毫秒 |
| `settings.gate` | 0.1–0.95 | 按键持续时间比例 |
| `settings.minimumTriggerIntervalMilliseconds` | 30–300 | 相邻触发的最小间隔，单位毫秒 |
| `settings.rhythm.bpm` | 1–1000 | 每分钟拍数 |
| `settings.rhythm.beatsPerBar` | 整数 1–12 | 每小节拍数 |
| `settings.rhythm.beatUnit` | `2`、`4`、`8`、`16` | 拍号分母 |
| `settings.rhythm.unitsPerBeat` | `1`、`2`、`3`、`4`、`6`、`8` | 每拍分格数 |

提供 `rhythm` 时，每格时长 `60000 / bpm / unitsPerBeat` 也必须落在 **20–2000 毫秒**之间。全部数值必须有限，不能使用 `NaN`、`Infinity` 或数值字符串。

`rhythm` 和 `score` 可以省略，但为了在其他人的软件中保留相同的演奏设置，建议像示例一样完整填写。实际节奏与按键效果请在琴桥中试听确认。

<a id="limits"></a>

## 仓库接收限制

| 项目 | 限制 |
| --- | --- |
| 单份乐谱 | 最多 4 MiB，普通且不可执行的文件 |
| 单份谱面文本 | 最多 1,000,000 个字符、100,000 个音符 |
| JSON 嵌套 / 音符分组嵌套 | 最多 12 层 / 32 层 |
| 分组展开计算量 | 最多 2,000,000 次累计分组元素处理 |
| `catalog.json` | 最多 1 MiB |
| 正式曲库 | 最多 2000 份乐谱，乐谱与目录合计最多 64 MiB |

不接受符号链接、可执行文件、脚本字段或谱面中的程序代码。正式乐谱直接放入 `scores/zh-CN/` 或 `scores/en-US/`，不能再建立子目录。

## 目录条目示例

`catalog.json` 由 `python -I tools/build_catalog.py` 生成。假设提交的文件是 `scores/zh-CN/入门练习.qinscore`，对应的**单个条目**如下：

```json
{
  "id": "scores/zh-CN/入门练习.qinscore",
  "title": "入门练习 · 数字谱",
  "file": "scores/zh-CN/入门练习.qinscore",
  "language": "zh-CN"
}
```

`id` 与 `file` 必须等于仓库相对路径，`title` 与乐谱内部标题完全一致，`language` 与目录对应。生成工具会维护完整列表和排序；不要用上面的单个条目覆盖整个目录文件。
