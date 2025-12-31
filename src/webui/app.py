"""
WebUI 应用 - 基于 aiohttp 的 Web 服务器
"""

import asyncio
from aiohttp import web
from typing import Optional
from src.logger import logger
from src.config import global_config
from .routes import setup_routes

_runner: Optional[web.AppRunner] = None
_site: Optional[web.TCPSite] = None

# WebUI 配置
WEBUI_HOST = "0.0.0.0"
WEBUI_PORT = 8096


async def start_webui():
    """启动 WebUI 服务"""
    global _runner, _site

    app = web.Application()
    setup_routes(app)

    _runner = web.AppRunner(app)
    await _runner.setup()
    _site = web.TCPSite(_runner, WEBUI_HOST, WEBUI_PORT)
    await _site.start()

    logger.info(f"WebUI 已启动，访问地址: http://{WEBUI_HOST}:{WEBUI_PORT}")


async def stop_webui():
    """停止 WebUI 服务"""
    global _runner
    if _runner:
        await _runner.cleanup()
        logger.info("WebUI 已停止")


# 兼容 router 接口
webui_router = None

