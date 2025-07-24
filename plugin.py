"""
AI语音插件

基于 MaiCore 的 AI 语音合成插件，支持多种音色、自动播报与命令触发。

功能特性：
- 支持多种音色（小新、妲己、酥心御姐等）
- Action自动触发和Command手动触发两种模式
- 仅群聊可用，确保使用场景合适
- 音色别名映射，方便用户使用
- 完善的错误处理和日志记录

使用方法：
- Action触发：发送包含"语音"、"说话"等关键词的消息
- Command触发：/voice 你好世界 [音色]

配置说明：
- 启动后自动生成 config.toml 配置文件
- 可自定义默认音色、启用/禁用组件等
- 支持扩展音色别名映射

作者：靓仔
版本：1.0.0
"""

from typing import List, Tuple, Type, Dict, Any, Optional
from src.common.logger import get_logger
from src.plugin_system import (
    BasePlugin, register_plugin, BaseAction,
    ComponentInfo, ActionActivationType, ChatMode,
    BaseCommand
)
from src.plugin_system.base.config_types import ConfigField
from src.plugin_system.apis import send_api
import re

logger = get_logger("ai_voice_plugin")

# ===== 音色别名映射 =====
# 可在配置文件中扩展更多音色
VOICE_ALIAS_MAP = {
    "小新": "lucy-voice-laibixiaoxin",
    "猴哥": "lucy-voice-houge",
    "四郎": "lucy-voice-silang",
    "东北老妹儿": "lucy-voice-guangdong-f1",
    "广西大表哥": "lucy-voice-guangxi-m1",
    "妲己": "lucy-voice-daji",
    "霸道总裁": "lucy-voice-lizeyan",
    "酥心御姐": "lucy-voice-suxinjiejie",
    "说书先生": "lucy-voice-m8",
    "憨憨小弟": "lucy-voice-male1",
    "憨厚老哥": "lucy-voice-male3",
    "吕布": "lucy-voice-lvbu",
    "元气少女": "lucy-voice-xueling",
    "文艺少女": "lucy-voice-f37",
    "磁性大叔": "lucy-voice-male2",
    "邻家小妹": "lucy-voice-female1",
    "低沉男声": "lucy-voice-m14",
    "傲娇少女": "lucy-voice-f38",
    "爹系男友": "lucy-voice-m101",
    "暖心姐姐": "lucy-voice-female2",
    "温柔妹妹": "lucy-voice-f36",
    "书香少女": "lucy-voice-f34"
}

# ===== Action组件 =====
class AiVoiceAction(BaseAction):
    """
    AI语音合成并发送（Action）
    适用场景：LLM判断需要语音播报、用户指定关键词时自动播报。
    """
    action_name = "ai_voice_action"
    action_description = "将文本内容转换为AI语音并发送到当前聊天。支持自定义音色。"
    action_parameters = {
        "text": "要转换为AI语音并发送的文本内容，必填。",
        "character": "AI语音的音色或角色，可选，如小新、妲己、酥心御姐等。"
    }
    action_require = [
        "当用户要求你用语音回应时使用",
        "当你想用语音播报重要信息时使用",
        "当你想让回答更生动活泼时使用",
        "当用户指定音色要求你用语音回应时使用"
    ]
    associated_types = ["command", "text"]
    focus_activation_type = ActionActivationType.KEYWORD
    normal_activation_type = ActionActivationType.ALWAYS
    activation_keywords = ["语音", "说话", "播报", "AI语音"]
    keyword_case_sensitive = False
    mode_enable = ChatMode.ALL
    parallel_action = False

    async def execute(self) -> Tuple[bool, str]:
        """执行AI语音合成与发送（仅限群聊）"""
        logger.info(f"{self.log_prefix} 执行AI语音发送动作: {getattr(self, 'reasoning', '')}")
        text_to_speak = self.action_data.get("text")
        character = AiVoicePlugin.resolve_voice_character(
            self.action_data.get("character"),
            self.get_config
        )
        if text_to_speak:
            text_to_speak = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9，。！？、,.!?:;\s]", "", text_to_speak)
        chat_stream = self.chat_stream
        if not getattr(chat_stream, 'group_info', None):
            logger.error(f"{self.log_prefix} AI语音功能仅支持群聊使用。")
            await send_api.text_to_user(
                text=text_to_speak,
                user_id=chat_stream.user_info.user_id
            )
            return False, "AI语音功能仅支持群聊使用。"
        if not text_to_speak:
            logger.error(f"{self.log_prefix} AI语音发送参数不完整，需要 'text' 内容。")
            await send_api.text_to_group(
                text="生成语音失败：需要提供要说的话。",
                group_id=chat_stream.group_info.group_id
            )
            return False, "AI语音发送参数不完整，需要 'text' 内容。"
        command_args: Dict[str, Any] = {"text": text_to_speak}
        if character:
            command_args["character"] = character
        try:
            success = await self.send_command(
                command_name="AI_VOICE_SEND",
                args=command_args,
                storage_message=False
            )
            if success:
                logger.info(f"{self.log_prefix} 成功发送AI语音命令，内容：\"{text_to_speak}\"")
                return True, f"成功发送AI语音消息：\"{text_to_speak}\" (音色：{character})"
            else:
                logger.error(f"{self.log_prefix} AI语音命令发送失败")
                await send_api.text_to_group(
                    text="AI语音命令发送失败",
                    group_id=chat_stream.group_info.group_id
                )
                return False, "AI语音命令发送失败"
        except Exception as e:
            logger.error(f"{self.log_prefix} 执行AI语音发送动作时出错: {e}")
            await send_api.text_to_group(
                text=f"执行AI语音动作时出错: {e}",
                group_id=chat_stream.group_info.group_id
            )
            return False, f"执行AI语音动作时出错: {e}"

# ===== Command组件 =====
class AiVoiceCommand(BaseCommand):
    """
    AI语音命令（Command）：/voice <文本> [音色]
    适用场景：用户主动输入命令时立即播报。
    """
    command_name = "ai_voice_command"
    command_description = "将文本内容转换为AI语音并发送，支持可选音色。用法：/voice 你好 小新"
    command_pattern = r"^/(?:voice|ai_voice)\s+(?P<text>.+?)(?:\s+(?P<character>\S+))?$"
    command_help = "将文本内容转换为AI语音并发送，支持可选音色。用法：/voice 你好 小新"
    command_examples = ["/voice 你好，世界！", "/voice 今天天气不错 妲己", "/voice 试试 酥心御姐"]
    intercept_message = True

    async def execute(self) -> Tuple[bool, str]:
        """执行AI语音命令"""
        text = self.matched_groups.get("text", "").strip()
        character = self.matched_groups.get("character", None)
        if not text:
            await self.send_text("❌ 请输入要转换为语音的文本内容")
            return False, "缺少文本内容"
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9，。！？、,.!?:;\s]", "", text)
        # 优化音色查找
        character = AiVoicePlugin.resolve_voice_character(
            character,
            self.get_config
        )
        
        # 检查是否群聊
        if not hasattr(self.message.message_info, 'group_info') or not self.message.message_info.group_info:
            logger.error(f"AI语音功能仅支持群聊使用。")
            await self.send_text(f"AI语音功能仅支持群聊使用。原文：{text}")
            return False, "AI语音功能仅支持群聊使用。"
        
        # 发送AI语音命令
        try:
            command_args: Dict[str, Any] = {"text": text}
            if character:
                command_args["character"] = character
            success = await self.send_command(
                command_name="AI_VOICE_SEND",
                args=command_args,
                storage_message=False
            )
            if success:
                logger.info(f"{self.log_prefix} 成功发送AI语音命令，内容：\"{text}\"")
                return True, f"成功发送AI语音消息：\"{text}\" (音色：{character})"
            else:
                logger.error(f"{self.log_prefix} AI语音命令发送失败")
                await self.send_text("AI语音命令发送失败")
                return False, "AI语音命令发送失败"
        except Exception as e:
            logger.error(f"{self.log_prefix} 执行AI语音命令时出错: {e}")
            await self.send_text(f"执行AI语音命令时出错: {e}")
            return False, f"执行AI语音命令时出错: {e}"

# ===== 插件注册 =====
@register_plugin
class AiVoicePlugin(BasePlugin):
    """
    AI语音插件 - 提供AI语音合成与发送能力
    支持Action/Command两种模式，可通过配置文件灵活开关。
    """
    plugin_name = "ai_voice_plugin"
    plugin_description = "将文本内容转换为AI语音并发送到当前聊天，支持多种音色。"
    plugin_version = "1.0.0"
    plugin_author = "靓仔"
    enable_plugin = True
    config_file_name = "config.toml"
    dependencies = []  # 插件依赖列表
    python_dependencies = []  # Python包依赖列表

    # 配置节描述
    config_section_descriptions = {
        "plugin": "插件基本信息配置",
        "voice": "AI语音功能配置",
        "components": "组件启用控制",
        "advanced": "高级设置"
    }

    # 配置Schema定义
    config_schema = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件")
        },
        "voice": {
            "default_character": ConfigField(type=str, default="温柔妹妹", description="默认AI语音音色"),
            "alias_map": ConfigField(type=dict, default=VOICE_ALIAS_MAP, description="音色别名映射")
        },
        "components": {
            "enable_ai_voice_action": ConfigField(type=bool, default=True, description="是否启用AI语音Action"),
            "enable_ai_voice_command": ConfigField(type=bool, default=True, description="是否启用AI语音命令Command")
        },
        "advanced": {
            "text_filter_regex": ConfigField(type=str, default=r"[^\u4e00-\u9fa5a-zA-Z0-9，。！？、,.!?:;\s]", description="文本过滤正则表达式"),
            "log_level": ConfigField(type=str, default="INFO", description="日志级别"),
            "send_text_in_private": ConfigField(type=bool, default=True, description="是否在非群聊时发送原始文本")
        }
    }

    @staticmethod
    def resolve_voice_character(character: Optional[str], get_config) -> str:
        """
        解析并获取有效的音色标识
        支持直接使用音色标识或使用别名
        """
        # 获取默认音色配置
        default_character_config = get_config("voice.default_character", "lucy-voice-guangdong-f1")

        # 如果没有指定音色，使用默认音色配置
        if not character:
            character = default_character_config

        # 尝试从配置中获取别名映射
        alias_map = get_config("voice.alias_map", VOICE_ALIAS_MAP)

        # 检查是否直接是音色标识
        if character.startswith("lucy-voice-"):
            return character

        # 尝试从别名映射中查找
        if character in alias_map:
            mapped = alias_map[character]
            logger.debug(f"[resolve_voice_character] 音色别名 '{character}' 映射到 '{mapped}'")
            return mapped

        # 如果没有找到匹配的别名，尝试使用默认音色的映射
        if default_character_config in alias_map:
            mapped = alias_map[default_character_config]
            logger.debug(f"[resolve_voice_character] 未找到音色别名 '{character}'，使用默认音色别名 '{default_character_config}' 映射到 '{mapped}'")
            return mapped

        # 最后兜底：如果默认音色也不在映射中，直接返回（可能是lucy-voice-开头的ID）
        logger.debug(f"[resolve_voice_character] 未找到音色别名 '{character}'，使用默认音色: {default_character_config}")
        return default_character_config

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """返回插件包含的组件列表，支持通过配置动态开关"""
        enable_action = self.get_config("components.enable_ai_voice_action", True)
        enable_command = self.get_config("components.enable_ai_voice_command", True)
        components = []
        if enable_action:
            components.append((AiVoiceAction.get_action_info(), AiVoiceAction))
        if enable_command:
            components.append((AiVoiceCommand.get_command_info(), AiVoiceCommand))
        return components
