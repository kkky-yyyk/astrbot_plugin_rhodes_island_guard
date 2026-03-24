import json
import os
import aiohttp
import random
from bs4 import BeautifulSoup
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("astrbot_plugin_rhodes_island_guard", "kkky", "卫戍协议辅助插件", "1.0.0")
class RhodesIslandGuardPlugin(Star):
    def __init__(self, context: Context):
        try:
            print("=== 罗德岛协议助手插件初始化开始 ===")
            super().__init__(context)
            # 兼容不同版本的数据目录获取
            base_data_dir = getattr(context, 'data_dir', os.path.join(os.getcwd(), 'data'))
            self.data_dir = os.path.join(base_data_dir, "plugins", "astrbot_plugin_rhodes_island_guard")
            
            # 图片目录（插件自身目录）
            self.image_dir = os.path.join(os.path.dirname(__file__), "images")
            if not os.path.exists(self.image_dir):
                os.makedirs(self.image_dir)

            # 数据文件路径
            self.protocol_file = os.path.join(self.data_dir, "protocols.json")
            self.covenant_file = os.path.join(self.data_dir, "covenants.json")
            self.operator_file = os.path.join(self.data_dir, "operators.json")
            
            self.load_protocols()
            self.load_covenants()
            self.load_operators()

            self.songs_file = os.path.join(self.data_dir, "songs.json")
            self.songs = []
            self.load_songs() #调用加载
            print("=== 插件初始化完成 ===")
        except Exception as e:
            logger.error(f"插件初始化异常: {e}")
            import traceback
            traceback.print_exc()

    # ---------- 数据加载 ----------
    def load_protocols(self):
        try:
            if os.path.exists(self.protocol_file):
                with open(self.protocol_file, 'r', encoding='utf-8') as f:
                    self.protocols = json.load(f)
            else:
                self.protocols = {}
                self.save_protocols()
        except Exception as e:
            logger.error(f"加载 protocols.json 失败: {e}")
            self.protocols = {}

    def save_protocols(self):
        try:
            with open(self.protocol_file, 'w', encoding='utf-8') as f:
                json.dump(self.protocols, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存 protocols.json 失败: {e}")

    def load_covenants(self):
        try:
            if os.path.exists(self.covenant_file):
                with open(self.covenant_file, 'r', encoding='utf-8') as f:
                    self.covenants = json.load(f)
            else:
                self.covenants = {}
                self.save_covenants()
        except Exception as e:
            logger.error(f"加载 covenants.json 失败: {e}")
            self.covenants = {}

    def save_covenants(self):
        try:
            with open(self.covenant_file, 'w', encoding='utf-8') as f:
                json.dump(self.covenants, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存 covenants.json 失败: {e}")

    def load_operators(self):
        try:
            if os.path.exists(self.operator_file):
                with open(self.operator_file, 'r', encoding='utf-8') as f:
                    self.operators = json.load(f)
            else:
                self.operators = {}
                self.save_operators()
        except Exception as e:
            logger.error(f"加载 operators.json 失败: {e}")
            self.operators = {}

    def save_operators(self):
        try:
            with open(self.operator_file, 'w', encoding='utf-8') as f:
                json.dump(self.operators, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存 operators.json 失败: {e}")
    
    def load_songs(self):
        try:
            if os.path.exists(self.songs_file):
                with open(self.songs_file, 'r', encoding='utf-8') as f:
                    self.songs = json.load(f)
            else:
                self.songs = []
                self.save_songs()
        except Exception as e:
            logger.error(f"加载 songs.json 失败: {e}")
            self.songs = []

    def save_songs(self):
        try:
            with open(self.songs_file, 'w', encoding='utf-8') as f:
                json.dump(self.songs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存 songs.json 失败: {e}")

    # ---------- 发送本地图片 ----------
    async def send_local_image(self, event: AstrMessageEvent, image_name: str):
        """根据图片名（不含扩展名）发送本地 images 文件夹下的图片"""
        try:
            image_path = os.path.join(self.image_dir, f"{image_name}.png")
            if not os.path.exists(image_path):
                # 尝试其他扩展名
                for ext in ['.jpg', '.jpeg', '.gif']:
                    alt_path = os.path.join(self.image_dir, f"{image_name}{ext}")
                    if os.path.exists(alt_path):
                        image_path = alt_path
                        break
                else:
                    yield event.plain_result(f"未找到图片：{image_name}")
                    return
            yield event.image_result(image_path)
        except Exception as e:
            logger.error(f"发送图片失败: {e}")
            yield event.plain_result(f"发送图片时出错: {e}")

    # ---------- 测试命令 ----------
    @filter.command("test")
    async def test(self, event: AstrMessageEvent):
        try:
            print("test 命令被调用")
            yield event.plain_result("test ok")
        except Exception as e:
            logger.error(f"test 命令执行出错: {e}")
            yield event.plain_result(f"命令执行出错: {e}")

    # ---------- 命令：盟约查询 ----------
    @filter.command("盟约")
    async def covenant_query(self, event: AstrMessageEvent):
        """
        用法：盟约 <盟约名>
        示例：盟约 叙拉古
        """
        try:
            print("盟约 命令被调用")
            args = event.message_str.strip().split()
            if len(args) < 2:
                yield event.plain_result("请提供盟约名称，例如：盟约 叙拉古")
                return

            covenant_name = args[1]
            if covenant_name not in self.covenants:
                yield event.plain_result(f"未找到盟约「{covenant_name}」，请检查名称。")
                return

            operators = self.covenants[covenant_name]
            reply = f"📜 **{covenant_name}盟约干员列表**\n"
            for op in operators:
                reply += f"• {op['name']}（{op['level']}级）\n"
            yield event.plain_result(reply)

            # 在回复干员列表后，尝试发送该盟约对应的图片
            async for result in self.send_local_image(event, covenant_name):
                yield result
        except Exception as e:
            logger.error(f"盟约命令执行出错: {e}")
            yield event.plain_result(f"命令执行出错: {e}")

    # ---------- 命令：干员查询 ----------
    @filter.command("干员")
    async def operator_query(self, event: AstrMessageEvent):
        """
        用法：干员 <干员名>
        示例：干员 拉普兰德
        """
        try:
            print("干员 命令被调用")
            args = event.message_str.strip().split()
            if len(args) < 2:
                yield event.plain_result("请提供干员名称，例如：干员 拉普兰德")
                return

            op_name = args[1]
            if op_name not in self.operators:
                yield event.plain_result(f"未找到干员「{op_name}」，请检查名称。")
                return

            op = self.operators[op_name]
            reply = f"👤 **{op_name}**\n"
            reply += f"📖 **特质**：{op['trait']}\n"
            reply += f"⭐ **等级**：{op['level']}\n"
            reply += f"🏰 **所属盟约**：{op['covenant']}"
            yield event.plain_result(reply)
        except Exception as e:
            logger.error(f"干员命令执行出错: {e}")
            yield event.plain_result(f"命令执行出错: {e}")

    # ---------- 命令：金曲 ----------
    @filter.command("金曲")
    async def random_song(self, event: AstrMessageEvent):
        """随机发送一个B站金曲视频链接"""
        try:
            print("金曲 命令被调用")
            if not self.songs:
                yield event.plain_result("暂无金曲数据，请联系管理员添加。")
                return
            song = random.choice(self.songs)
            reply = f"🎵 为您推荐：{song['title']}\n🔗 {song['url']}"
            yield event.plain_result(reply)
        except Exception as e:
            logger.error(f"金曲命令执行出错: {e}")
            yield event.plain_result("获取金曲失败，请稍后重试。")
    
    # ---------- 命令：卫一把 ----------
    @filter.command("卫一把")
    async def random_covenants(self, event: AstrMessageEvent):
        """随机推荐2-3个盟约，用于下一把游戏"""
        try:
            print("卫一把 命令被调用")
            covenants = list(self.covenants.keys())
            if len(covenants) < 2:
                yield event.plain_result("盟约数据不足，无法推荐。")
                return

            # 随机选择 2 或 3 个盟约
            count = random.choice([2, 3]) if len(covenants) >= 3 else 2
            selected = random.sample(covenants, count)

            reply = "🎲 为您推荐下一把可以尝试的盟约组合：\n"
            for c in selected:
                # 获取该盟约下的干员数量（可选，增加趣味）
                op_count = len(self.covenants[c])
                reply += f"• {c}（{op_count}名干员）\n"
            yield event.plain_result(reply)
        except Exception as e:
            logger.error(f"卫一把命令执行出错: {e}")
            yield event.plain_result("推荐失败，请稍后重试。")

    # ---------- 生命周期 ----------
    async def initialize(self):
        logger.info("卫戍协议插件已加载")

    async def terminate(self):
        logger.info("卫戍协议插件已卸载")