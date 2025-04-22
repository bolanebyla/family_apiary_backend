from pydantic_settings import BaseSettings


class TgChatBotSettings(BaseSettings):
    TOKEN: str
    PRODUCT_PURCHASE_REQUEST_NOTIFICATION_CHAT_ID: str

    class Config:
        env_prefix = 'PRODUCTS_TG_CHAT_BOT_'
