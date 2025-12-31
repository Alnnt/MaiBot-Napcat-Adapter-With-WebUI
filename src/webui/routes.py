"""
WebUI 路由定义
"""

import json
from aiohttp import web
from src.config import global_config
from src.logger import logger
from .config_manager import (
    get_chat_config,
    update_group_list_type,
    update_group_list,
    update_private_list_type,
    update_private_list,
    save_config_to_file,
)
from .static import get_index_html


async def index_handler(request: web.Request) -> web.Response:
    """返回主页面"""
    return web.Response(text=get_index_html(), content_type="text/html")


async def get_config_handler(request: web.Request) -> web.Response:
    """获取当前配置"""
    config = get_chat_config()
    return web.json_response(config)


async def update_config_handler(request: web.Request) -> web.Response:
    """更新配置"""
    try:
        data = await request.json()

        field = data.get("field")
        value = data.get("value")

        if field is None or value is None:
            return web.json_response({"success": False, "error": "缺少 field 或 value 参数"}, status=400)

        success = False
        message = ""

        if field == "group_list_type":
            if value not in ["whitelist", "blacklist"]:
                return web.json_response({"success": False, "error": "group_list_type 必须是 whitelist 或 blacklist"}, status=400)
            success = update_group_list_type(value)
            message = f"群聊列表类型已更新为: {value}"

        elif field == "group_list":
            if not isinstance(value, list):
                return web.json_response({"success": False, "error": "group_list 必须是数组"}, status=400)
            # 确保所有元素都是整数
            try:
                value = [int(v) for v in value]
            except (ValueError, TypeError):
                return web.json_response({"success": False, "error": "group_list 中的元素必须是数字"}, status=400)
            success = update_group_list(value)
            message = f"群聊列表已更新，共 {len(value)} 个群组"

        elif field == "private_list_type":
            if value not in ["whitelist", "blacklist"]:
                return web.json_response({"success": False, "error": "private_list_type 必须是 whitelist 或 blacklist"}, status=400)
            success = update_private_list_type(value)
            message = f"私聊列表类型已更新为: {value}"

        elif field == "private_list":
            if not isinstance(value, list):
                return web.json_response({"success": False, "error": "private_list 必须是数组"}, status=400)
            # 确保所有元素都是整数
            try:
                value = [int(v) for v in value]
            except (ValueError, TypeError):
                return web.json_response({"success": False, "error": "private_list 中的元素必须是数字"}, status=400)
            success = update_private_list(value)
            message = f"私聊列表已更新，共 {len(value)} 个用户"

        else:
            return web.json_response({"success": False, "error": f"未知的字段: {field}"}, status=400)

        if success:
            # 保存配置到文件
            save_config_to_file()
            logger.info(f"[WebUI] {message}")
            return web.json_response({"success": True, "message": message, "config": get_chat_config()})
        else:
            return web.json_response({"success": False, "error": "更新配置失败"}, status=500)

    except json.JSONDecodeError:
        return web.json_response({"success": False, "error": "无效的 JSON 数据"}, status=400)
    except Exception as e:
        logger.error(f"[WebUI] 更新配置时发生错误: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


def setup_routes(app: web.Application):
    """设置路由"""
    app.router.add_get("/", index_handler)
    app.router.add_get("/api/config", get_config_handler)
    app.router.add_post("/api/config", update_config_handler)

