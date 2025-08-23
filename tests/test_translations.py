# from homeassistant.helpers.translation import async_get_translations
#
# from custom_components.bololo import DOMAIN
#
#
# async def test_translations(hass):
#     """测试翻译功能"""
#
#     # 加载中文翻译
#     zh_translations = await async_get_translations(hass, "zh-Hans", "config", [DOMAIN])
#     assert zh_translations["config.step.user.title"] == "用户信息配置"
#
#     print("翻译测试通过!")