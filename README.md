# AI语音插件

基于 MaiCore 的 AI 语音合成插件，支持多种音色、自动播报与命令触发，为聊天体验提供丰富的语音交互功能。

## 🎯 功能特性

- 🎵 **多种音色支持**：内置22种精选音色，包括小新、妲己、酥心御姐等
- 🤖 **智能触发**：支持关键词自动触发和命令手动触发
- 👥 **群聊专用**：仅在群聊中可用，确保使用场景合适
- ⚙️ **灵活配置**：支持配置文件自定义所有参数
- 🔧 **音色别名**：支持音色别名映射，方便用户使用
- 📝 **完善日志**：详细的错误处理和日志记录

## 📖 使用方法

### Action模式（智能触发）

当消息中包含以下关键词时，MaiCore可能会选择使用语音回复：

- "语音"、"说话"、"播报"
- "AI语音"

**示例：**
```
用户：请用语音说一下今天的天气
麦麦：[发送语音消息]
```

### Command模式（手动触发）

使用 `/voice` 命令直接生成语音：

```bash
/voice 你好，世界！              # 使用默认音色
/voice 今天天气不错 妲己         # 使用妲己音色
/voice 试试看 酥心御姐           # 使用酥心御姐音色
```

## ⚙️ 配置说明

插件启动后会自动生成 `config.toml` 配置文件，包含以下配置项：

### 插件基本配置
```toml
[plugin]
enabled = true  # 是否启用插件
```

### 组件控制
```toml
[components]
enable_ai_voice_action = true   # 是否启用Action组件（关键词触发）
enable_ai_voice_command = true  # 是否启用Command组件（命令触发）
```

### 语音配置
```toml
[voice]
default_character = "东北老妹儿"  # 默认音色

# 音色别名映射（可扩展）
[voice.alias_map]
小新 = "lucy-voice-laibixiaoxin"
妲己 = "lucy-voice-daji"
酥心御姐 = "lucy-voice-suxinjiejie"
# ... 更多音色配置
```

### 高级设置
```toml
[advanced]
text_filter_regex = "[^\\u4e00-\\u9fa5a-zA-Z0-9，。！？、,.!?:;\\s]"  # 文本过滤
log_level = "INFO"                    # 日志级别
send_text_in_private = true          # 非群聊时是否发送原始文本
```

## 🎭 音色列表

| 别名         | 音色标识                  | 风格描述     |
| ------------ | ------------------------- | ------------ |
| 小新         | lucy-voice-laibixiaoxin   | 可爱童声     |
| 猴哥         | lucy-voice-houge          | 经典角色     |
| 四郎         | lucy-voice-silang         | 温和男声     |
| 东北老妹儿   | lucy-voice-guangdong-f1   | 东北口音     |
| 广西大表哥   | lucy-voice-guangxi-m1     | 广西口音     |
| 妲己         | lucy-voice-daji           | 妩媚女声     |
| 霸道总裁     | lucy-voice-lizeyan        | 成熟男声     |
| 酥心御姐     | lucy-voice-suxinjiejie    | 温柔御姐     |
| 说书先生     | lucy-voice-m8             | 说书风格     |
| 憨憨小弟     | lucy-voice-male1          | 憨厚男声     |
| 憨厚老哥     | lucy-voice-male3          | 朴实男声     |
| 吕布         | lucy-voice-lvbu           | 威武男声     |
| 元气少女     | lucy-voice-xueling        | 活泼女声     |
| 文艺少女     | lucy-voice-f37            | 文静女声     |
| 磁性大叔     | lucy-voice-male2          | 磁性男声     |
| 邻家小妹     | lucy-voice-female1        | 清纯女声     |
| 低沉男声     | lucy-voice-m14            | 低沉男声     |
| 傲娇少女     | lucy-voice-f38            | 傲娇女声     |
| 爹系男友     | lucy-voice-m101           | 温暖男声     |
| 暖心姐姐     | lucy-voice-female2        | 温暖女声     |
| 温柔妹妹     | lucy-voice-f36            | 温柔女声     |
| 书香少女     | lucy-voice-f34            | 知性女声     |

## 🔧 技术说明

### 工作原理

1. **Action触发**：当检测到关键词时，自动调用语音合成
2. **Command触发**：用户主动使用命令触发语音合成
3. **音色解析**：支持别名和直接音色ID两种方式
4. **群聊限制**：仅在群聊环境中生效，私聊时返回原始文本

### 文件处理

- 通过 `AI_VOICE_SEND` 命令发送语音
- 支持文本过滤，移除特殊字符
- 完善的错误处理和用户提示

### 扩展开发

如需添加新音色，在 `config.toml` 的 `[voice.alias_map]` 下增加配置：

```toml
[voice.alias_map]
新音色名 = "lucy-voice-新音色ID"
```

## 🐛 故障排除

### 常见问题

1. **语音合成失败**
   - 检查是否在群聊中使用
   - 确认文本内容是否合法
   - 查看日志获取详细错误信息

2. **音色不生效**
   - 确认音色别名是否正确
   - 检查配置文件中的音色映射
   - 使用默认音色进行测试

3. **插件无响应**
   - 检查插件是否启用
   - 确认组件配置是否正确
   - 查看系统日志

### 日志查看

插件会输出详细的日志信息：

```
[ai_voice_plugin] 执行AI语音发送动作: 用户要求语音回复
[ai_voice_plugin] 音色别名 '妲己' 映射到 'lucy-voice-daji'
[ai_voice_plugin] 成功发送AI语音命令，内容："你好世界"
```

## 📋 版本信息

- **版本**：1.0.0
- **作者**：靓仔
- **依赖**：MaiCore 内置语音系统
- **许可证**：AGPL-3.0

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个插件！

### 开发建议

1. 遵循现有代码风格
2. 添加适当的日志记录
3. 完善错误处理机制
4. 更新相关文档

---

**注意**：本插件仅在群聊中可用，私聊时会返回原始文本内容。
