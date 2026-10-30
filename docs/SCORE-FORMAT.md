# 乐谱格式与示例

[返回首页](../README.md) · [贡献指南](../CONTRIBUTING.md) · [下载数字谱示例](../examples/numbers.qinscore) · [下载键盘谱示例](../examples/keyboard.qinscore) · [下载文件控制示例](../examples/file-controlled.qinscore)

`.qinscore` 是保存一首乐谱的 UTF-8 JSON 文件。可以用文本编辑器查看，也可以直接从琴桥导出。它保存曲目与演奏参数；`version: 2` 的文件还必须携带“文件控制播放参数”（`playbackControl`）。这些都是声明式数据，不包含也不执行 Lua、JavaScript 等脚本。

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

JSON 字符串中的 `\n` 表示换行。字段名区分大小写；数值不加引号，布尔值使用 `true` / `false`。不支持注释、尾随逗号、重复键或未定义字段；`playbackControl` 仅用于 v2；`midi` 仅用于 v3。各版本禁止混用这些字段，包括显式 `null`；其余未定义字段仍然一律拒绝。

## 顶层字段

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `format` | 是 | 固定为 `"qinbridge.score"` |
| `version` | 是 | 普通文字谱为整数 `1`；带 `playbackControl` 的文字谱为整数 `2`；携带 MIDI 数据为整数 `3` |
| `title` | 是 | 非空曲名，最多 256 个字符；语言与投稿目录对应 |
| `sourceUrl` | 否 | 来源 HTTP(S) 地址，或空字符串；最多 2048 个字符 |
| `scoreText` | 是 | v1/v2 为非空谱面文本；v3 导出为空字符串，音符读取自 `midi` |
| `settings` | 是 | 演奏设置对象，推荐完整保留软件导出的值；也是可编辑设置的初始值与未接管字段的基线，必须自身有效 |
| `playbackControl` | 仅 v2 | 文件控制播放参数对象；v2 必须出现且至少一个字段，v1 不得出现。见[文件控制播放参数](#playback-control) |
| `midi` | 仅 v3 | 原始 MIDI 音符、速度、拍号及音轨数据；必填，不能与 `playbackControl` 并用 |

标题、来源等元数据不接受控制字符。作者、适用游戏和分发授权情况写在 **PR 说明** 或可选的[随谱来源说明](#source-notes)中，不要自行加入 `.qinscore` 字段。来源网址仅作为资料保存，仓库校验时不会访问它。

## MIDI v3（琴桥 0.12.0 起）

[完整 MIDI 示例](../examples/midi.qinscore)是用于说明协议的单音测试数据，不是正式曲库作品。MIDI 导出保留原始 tick、音高和时长，不转换为有损文字谱。`settings.score` 必须使用 `notation: "Midi"`、`timing: "SlashBeats"`；通用 `settings` 仍须满足既有范围，实际速度和拍号读取自 `midi`。

| `midi` 字段 | 校验规则 |
| --- | --- |
| `ticksPerQuarterNote` | 整数 1–32767 |
| `durationTicks` | 正整数，不超过 2 的 40 次方 |
| `notes` | 1–100000 项 `{pitch,tick,length,track,channel,velocity}`；音高 0–127、通道 0–15、力度 1–127；起点和正时长不得越过全曲结尾 |
| `tracks`、`selectedTracks` | 非空音轨 `{index,name}` 列表与非空所选索引列表；索引不得重复，引用的音轨必须存在 |
| `tempos` | 非空 `{tick,microsecondsPerQuarter}`；首点 tick 0，后续严格递增且不超过全曲结尾；微秒值 1–16777215 |
| `meters` | 非空 `{tick,numerator,denominator}`；时间顺序同上；分子 1–255，分母为 1–128 中的 2 的幂 |
| `transposeSemitones` | 可选，整数 −24–24，缺省 0 |
| `ignoredExpressionEvents`、`unpairedNoteEvents` | 可选，非负 32 位整数，缺省 0 |

至少有一个所选音轨包含非打击乐音符（`channel != 9`）。所有层级严格拒绝未知字段、重复 JSON 键、错误数值类型及非有限值。JSON 文件仍限制为 4 MiB；最多 100000 个音符不代表全部能装进此大小限制。`catalog.json` 继续使用版本 1；v1/v2 的解析和安全规则保持原样。校验器只读取数据，不调用 MIDI 播放器或执行文件内容。

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

`settings` 始终是有效基线：即使某些字段被 `playbackControl` 接管，这些字段在 `settings` 中的值仍必须满足上表范围。未接管项以它作为初始值；已接管项始终使用控制值。

<a id="playback-control"></a>

## 文件控制播放参数（可选，v2）

`playbackControl` 是 `version: 2` 独有的顶层对象，让乐谱文件接管部分播放参数。它是声明式数据，不是 Lua / JavaScript 等可执行脚本；播放、预览和摘要都按同一优先级取值：

> 文件中的 `playbackControl` 覆盖值 > 当前可编辑设置（初值为 `settings`）

只有 `playbackControl` 中出现的字段会被接管并在界面中锁定，未出现的字段仍可编辑。`beatsPerBar`（拍号分子）和 `beatUnit`（拍号分母）分别独立控制。仅当 `playbackControl.timing` 存在时，节奏读取方式显示“由脚本控制”；底层真实计时模式仍取 `timing` 枚举值（`SpaceGrid` 或 `SlashBeats`），“脚本”仅是界面文案，不会执行任何脚本。

### 版本规则

- `version: 1` 的普通文件仍然可以读取；v1 中出现 `playbackControl`（包括 `null`）一律无效。
- 带 `playbackControl` 的文件必须是 `version: 2`；v2 缺失 `playbackControl`、值为 `null` 或空对象 `{}` 都无效。
- 无文件控制的导出保持 `version: 1`；含文件控制的导出为 `version: 2`。新版客户端在导入、曲库保存和导出时完整保留控制内容；旧版客户端会因版本 2 明确拒绝该文件，不能偷偷降级为 v1 或移除控制字段。
- 固定参数控制需要琴桥 0.10.0 起；小节变速 `tempoMap` 需要 0.11.0 起。两种都使用 `version: 2`。旧版客户端会明确拒绝不认识的字段，不能为兼容旧版而删掉变速表。当前为本地测试包，不代表已发布到商店。

### 字段

除版本规则外，`playbackControl` 还要求：至少出现一个字段；已提供字段不能为 `null`；未知字段、重复键、数值字符串、`NaN`/`Infinity` 等非有限数、把布尔值当数值、错误枚举均拒绝。

| 字段 | 类型 | 范围 / 可选值 |
| --- | --- | --- |
| `playbackControl.bpm` | 数值（double） | 1–1000 |
| `playbackControl.tempoMap` | 非空数组 | 小节变速点；与同一控制对象中的 `bpm` 互斥 |
| `playbackControl.beatsPerBar` | 整数 | 1–12 |
| `playbackControl.beatUnit` | 整数 | `2`、`4`、`8`、`16` |
| `playbackControl.unitsPerBeat` | 整数 | `1`、`2`、`3`、`4`、`6`、`8` |
| `playbackControl.timing` | 字符串 | 精确等于 `SpaceGrid` 或 `SlashBeats` |
| `playbackControl.arpeggioMilliseconds` | 数值 | 1–100 |
| `playbackControl.minimumTriggerIntervalMilliseconds` | 数值 | 30–300 |
| `playbackControl.gate` | 数值 | 0.1–0.95 |
| `playbackControl.ignoreMeasureNumbers` | 布尔 | `true` / `false` |

“数值”表示 JSON 数字，可以是整数或小数，但不能加引号，也不能写成 `true`/`false`；“整数”字段不接受小数。全部数值必须有限。

`settings` 本身必须始终有效，作为未接管字段和可编辑设置的基线。若接管了 `bpm`，使用控制值；有 `tempoMap` 时，初始 BPM 取首点。两者都没有时使用有效基线的 BPM：`rhythm` 为对象时，省略的 `bpm` 默认为 120；整个 `rhythm` 省略或为 `null` 时，按 `60000 / slotMilliseconds / 4` 推导 BPM，每拍分格默认为 4。每个控制字段逐项覆盖，合并后的每格时长 `60000 / bpm / unitsPerBeat` 仍必须落在 **20–2000 毫秒**之间；变速表每个端点同样检查。例如 `bpm: 90`、`unitsPerBeat: 4` 对应每格约 166.67 毫秒。

完整示例见 [`examples/file-controlled.qinscore`](../examples/file-controlled.qinscore)（自编短音阶，只接管部分字段）：

```json
"version": 2,
"playbackControl": {
  "bpm": 90,
  "timing": "SlashBeats",
  "gate": 0.6,
  "arpeggioMilliseconds": 12,
  "minimumTriggerIntervalMilliseconds": 120
}
```

未携带 `playbackControl` 的普通文件保持 `version: 1`，行为不变。`catalog.json` 仍为 `version: 1`，目录条目只包含 `id`、`title`、`file`、`language`，不携带 `playbackControl`；客户端从乐谱文件本身读取控制内容。

### 按小节变速 tempoMap（仍为 v2）

完整四小节示例见 [`examples/tempo-map.qinscore`](../examples/tempo-map.qinscore)。变速表位于 `playbackControl.tempoMap`，每个点只允许 `atBar`、`bpm`、`curveToNext`：

```json
"tempoMap": [
  { "atBar": 1, "bpm": 100, "curveToNext": "hold" },
  { "atBar": 2, "bpm": 100, "curveToNext": "linearBpm" },
  { "atBar": 3, "bpm": 80, "curveToNext": "linearBpm" },
  { "atBar": 4, "bpm": 100, "curveToNext": "hold" }
]
```

- `atBar` 必填，范围 1–2147483647 的整数，首点必须为 1，后续严格递增。按累计拍数与有效 `beatsPerBar` 定位，不按换行、空行或手写编号定位。在 4/4 中第 2 小节是累计 4 拍处；`SlashBeats` 每段计一拍，`SpaceGrid` 每格计 `1 / unitsPerBeat` 拍。
- `bpm` 必填，范围 1–1000；BPM 仍按拍号分母计拍，例如 6/8 数八分音符。各端点必须满足有效格长限制。
- `curveToNext` 省略时为 `hold`：维持本点速度，到下一点直接切换。`linearBpm`：从本点到下一点，BPM 随拍位线性改变；目标更低即渐慢，更高即渐快。值区分大小写，最后一点必须为 `hold`。
- 变速点不得超出谱面总拍数。完整结尾可使用下一小节起点作为渐变终点，例如 69 小节谱的第 70 小节起点；终点不添加时长。部分小节结尾不能引用其后的边界。
- `tempoMap` 和同一 `playbackControl.bpm` 互斥。`settings` 仍保留合法基线。变速表接管 BPM，界面显示“由脚本控制”；其他参数是否锁定取决于各自是否被接管。
- 空数组、空点、重复小节、乱序、未知字段、`null`、表达式、缺失必填值均无效。每个点同样禁止重复 JSON 键、数值字符串及非有限数。

客户端对 `60000 / BPM(拍位)` 做积分得到毫秒时间，不以端点平均 BPM 近似。起音、休止、按键时长、预览和小节进度使用同一换算，暂停续播不会从曲首重启变速。触发下限、琶音间隔、鼠标提前量依然是实际毫秒，不随 BPM 缩放。播放期间修改文件不会改动已编译时间轴。

格式仍是 v2 的声明式脚本控制，无 Lua/JS、循环或外部执行。0.10.0 会因未知字段拒绝此扩展；应使用 0.11.0 起的客户端，并先更新仓库校验器再提交正式变速谱。

<a id="limits"></a>

## 仓库接收限制

| 项目 | 限制 |
| --- | --- |
| 单份乐谱 | 最多 4 MiB，普通且不可执行的文件 |
| 可选随谱来源说明 | 每份最多 64 KiB，普通且不可执行的 JSON 文件 |
| 单份谱面文本 | 最多 1,000,000 个字符、100,000 个音符 |
| JSON 嵌套 / 音符分组嵌套 | 最多 12 层 / 32 层 |
| 分组展开计算量 | 最多 2,000,000 次累计分组元素处理 |
| `catalog.json` | 最多 1 MiB |
| 正式曲库 | 最多 2000 份乐谱；乐谱、目录与随谱来源说明合计最多 64 MiB |

不接受符号链接、可执行文件、脚本字段或谱面中的程序代码。正式乐谱直接放入 `scores/zh-CN/` 或 `scores/en-US/`，不能再建立子目录。

`playbackControl` 是声明式数据，不是脚本字段；界面上的“由脚本控制”只是文案，机器人只校验数据，不执行乐谱内容。仓库先由维护者合并校验器/基础设施对 v2 的支持，之后才接收 v2 正式曲谱 PR；这类基础设施变更不会被自动批准或合并。`catalog.json` 仍为 `version: 1`，目录格式无需改变。

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

<a id="source-notes"></a>

## 可选的来源与署名说明

对 `scores/zh-CN/曲名.qinscore`，可添加同目录的 `曲名.qinscore.source.json`。这是 Git 仓库中的配套资料，不改变 `.qinscore` 格式，不进入在线曲库目录，也不要求客户端读取。

```json
{
  "sourceUrl": "https://github.com/DZXH-TX/QinBridge-Scores/blob/main/examples/numbers.qinscore",
  "sourceTitle": "入门练习 · 数字谱",
  "author": "DZXH CR Tech（GitHub：DZXH-TX）",
  "credit": "本项目的入门音阶示例",
  "notes": "包含单音、和弦、琶音与休止。"
}
```

对应可下载示例见 [`numbers.qinscore.source.json`](../examples/numbers.qinscore.source.json)。

| 可选字段 | 内容 | 最多字符数 |
| --- | --- | --- |
| `sourceUrl` | HTTP(S) 来源链接，或空字符串 | 2048 |
| `sourceTitle` | 原帖 / 原稿标题 | 256 |
| `author` | 谱面作者或发布者；可写明身份 | 256 |
| `credit` | 原曲、原编配等补充署名 | 2048 |
| `license` | 作者选择的许可或原始许可声明，允许省略或留空 | 2048 |
| `notes` | 谱面对照、修改记录或其他说明 | 4096 |

所有值均使用普通单行字符串，不接受脚本字段、嵌套对象、重复键或控制字符。说明必须有同名对应乐谱，不能用任意 JSON 文件名代替。CI 会同时检查说明的 JSON 安全格式、文件模式和资源限制。

**CI 不要求 `license`，也不验证它是否为 CC、许可是否有效或投稿人是否获得授权。** 如果作者自愿且有权使用 CC BY-SA 4.0，可以在 `license` 中注明名称与官方链接；不填该字段同样可以通过检查和自动合并。具体许可范围见[许可说明](../LICENSE.md)。

`build_catalog.py` 只生成乐谱目录。来源说明随 Git 提交，由 `validate_scores.py` 和 CI 校验，无需为说明文件生成目录条目。

来源说明不承载播放参数；文件控制只写在 `.qinscore` 的 `playbackControl` 中。
