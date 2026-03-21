import json
import os
import aiohttp
from bs4 import BeautifulSoup
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("rhodes_island_guard", "kkky", "卫戍协议辅助插件", "1.0.0")
class RhodesIslandGuardPlugin(Star):
    def __init__(self, context: Context):
        print("=== 罗德岛协议助手插件初始化开始 ===")
        super().__init__(context)
        # 兼容不同版本的数据目录获取
        base_data_dir = getattr(context, 'data_dir', os.path.join(os.getcwd(), 'data'))
        self.data_dir = os.path.join(base_data_dir, "plugins", "rhodes_island_guard")
        
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
        print("=== 插件初始化完成 ===")

    # ---------- 数据加载 ----------
    def load_protocols(self):
        if os.path.exists(self.protocol_file):
            with open(self.protocol_file, 'r', encoding='utf-8') as f:
                self.protocols = json.load(f)
        else:
            self.protocols = {}
            self.save_protocols()

    def save_protocols(self):
        with open(self.protocol_file, 'w', encoding='utf-8') as f:
            json.dump(self.protocols, f, ensure_ascii=False, indent=2)

    def load_covenants(self):
        if os.path.exists(self.covenant_file):
            with open(self.covenant_file, 'r', encoding='utf-8') as f:
                self.covenants = json.load(f)
        else:
            self.covenants = {}
            self.save_covenants()

    def save_covenants(self):
        with open(self.covenant_file, 'w', encoding='utf-8') as f:
            json.dump(self.covenants, f, ensure_ascii=False, indent=2)

    def load_operators(self):
        if os.path.exists(self.operator_file):
            with open(self.operator_file, 'r', encoding='utf-8') as f:
                self.operators = json.load(f)
        else:
            self.operators = {}
            self.save_operators()

    def save_operators(self):
        with open(self.operator_file, 'w', encoding='utf-8') as f:
            json.dump(self.operators, f, ensure_ascii=False, indent=2)

    # ---------- 发送本地图片 ----------
    async def send_local_image(self, event: AstrMessageEvent, image_name: str):
        """根据图片名（不含扩展名）发送本地 images 文件夹下的图片"""
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

    @filter.command("/test")
    async def test(self, event: AstrMessageEvent):
        yield event.plain_result("test ok")
    # ---------- 命令：盟约查询 ----------
    @filter.command("/盟约")
    async def covenant_query(self, event: AstrMessageEvent):
        """
        用法：盟约 <盟约名>
        示例：盟约 叙拉古
        """
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

    # ---------- 命令：干员查询 ----------
    @filter.command("/干员")
    async def operator_query(self, event: AstrMessageEvent):
        """
        用法：干员 <干员名>
        示例：干员 拉普兰德
        """
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

    # ---------- 命令：战绩查询（森空岛模拟） ----------
    @filter.command("/战绩")
    async def record_query(self, event: AstrMessageEvent):
        """
        用法：战绩 <玩家名或UID>
        示例：战绩 博士#1234
        """
        args = event.message_str.strip().split()
        if len(args) < 2:
            yield event.plain_result("请提供玩家名称，例如：战绩 博士#1234")
            return

        player_name = args[1]
        yield event.plain_result(f"正在查询玩家「{player_name}」的战绩...\n（当前为模拟数据）")

        # 模拟数据
        mock_data = {
            "recent_games": 10,
            "wins": 7,
            "win_rate": "70%",
            "last_match": "2025-03-20 19:30"
        }
        reply = f"🎮 **{player_name} 近期战绩**\n"
        reply += f"📊 对局数：{mock_data['recent_games']}\n"
        reply += f"🏆 胜场：{mock_data['wins']}\n"
        reply += f"📈 胜率：{mock_data['win_rate']}\n"
        reply += f"🕒 最后对局：{mock_data['last_match']}"
        yield event.plain_result(reply)

        # ===== 真实接口对接说明 =====
        # 森空岛目前没有公开的玩家战绩 API。如需实现，可尝试以下方法：
        # 1. 使用用户提供的 Cookie（需要登录态）模拟请求。
        # 2. 分析森空岛网页端接口（F12 抓包），找到获取战绩的 API。
        # 3. 使用 aiohttp 携带 Cookie 请求该 API，并解析 JSON。
        # 
        # 示例伪代码（需要用户配置 cookie）：
        # async with aiohttp.ClientSession() as session:
        #     headers = {"Cookie": "your_cookie_here"}
        #     async with session.get(f"https://api.skland.com/player/{player_name}", headers=headers) as resp:
        #         data = await resp.json()
        #         # 解析并返回
        # 由于需要登录，本插件暂不实现自动获取，你可根据需求自行扩展。
        pass

    # ---------- 命令：PRTS wiki 搜索（联网，限定于 PRTS） ----------
    @filter.command("/prts")
    async def prts_search(self, event: AstrMessageEvent):
        """
        用法：prts <关键词>
        示例：prts 拉普兰德
        从 PRTS wiki 获取干员信息。
        """
        args = event.message_str.strip().split()
        if len(args) < 2:
            yield event.plain_result("请提供搜索关键词，例如：prts 拉普兰德")
            return

        keyword = args[1]
        url = f"https://prts.wiki/w/{keyword}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        yield event.plain_result(f"未找到「{keyword}」的相关信息（页面不存在）")
                        return
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # 简单提取页面第一段介绍
                    content_div = soup.find('div', class_='mw-parser-output')
                    if content_div:
                        paragraphs = content_div.find_all('p', recursive=False)
                        if paragraphs:
                            text = paragraphs[0].get_text().strip()
                            # 限制长度
                            if len(text) > 500:
                                text = text[:500] + "..."
                            reply = f"📖 **{keyword}**（来自 PRTS wiki）\n{text}"
                            yield event.plain_result(reply)
                        else:
                            yield event.plain_result(f"未找到「{keyword}」的详细介绍")
                    else:
                        yield event.plain_result(f"解析页面失败")
            except Exception as e:
                logger.error(f"PRTS 搜索出错: {e}")
                yield event.plain_result("网络请求失败，请稍后重试")


    # ---------- 生命周期 ----------
    async def initialize(self):
        logger.info("卫戍协议插件已加载")

    async def terminate(self):
        logger.info("卫戍协议插件已卸载")