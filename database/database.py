import asyncio
import os

import aiomysql


class Database:
    """
    データベース操作系クラス
    """

    def __init__(self, bot):
        self.bot = bot
        self.initialized: bool = False
        self.pool: aiomysql.Pool | None = None

    async def connect(self) -> None:
        """
        データベースに接続します
        """

        loop = asyncio.get_event_loop()
        self.pool = await aiomysql.create_pool(
            host=os.environ.get("MYSQL_HOST"),
            port=int(os.environ.get("MYSQL_PORT")),
            user=os.environ.get("MYSQL_USERNAME"),
            password=os.environ.get("MYSQL_PASSWORD"),
            db=os.environ.get("MYSQL_DATABASE"),
            loop=loop,
            autocommit=False,
        )

        print("Connected to database")

    async def init(self) -> None:
        """
        各テーブルを初期化します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # ユーザーのレベルデータ
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS user_levels (user_id BIGINT UNSIGNED PRIMARY KEY,"
                    "level INT UNSIGNED NOT NULL, exp INT UNSIGNED NOT NULL, total_text_exp INT UNSIGNED NOT NULL,"
                    "total_voice_exp INT UNSIGNED NOT NULL, total_bonus_exp INT UNSIGNED NOT NULL,"
                    "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                    "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP)"
                )
                # 1日のランキング用データ
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS day_user_channel_exps (user_id BIGINT UNSIGNED,"
                    "channel_id BIGINT UNSIGNED, exp INT UNSIGNED NOT NULL,"
                    "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                    "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,"
                    "PRIMARY KEY (user_id, channel_id))"
                )
                await conn.commit()

        print("Initialized database")

        self.initialized = True

    async def close(self) -> None:
        """
        データベースから切断します
        """

        # 接続が閉じられるまで待機
        self.pool.close()
        await self.pool.wait_closed()
        print("Disconnected from database")

    def is_initialized(self) -> bool:
        """
        データベースが初期化されているかを返します
        """

        return self.initialized

    async def get_user_level(self, user_id: int) -> dict[str, int]:
        """
        ユーザーのレベルデータを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT level, exp, total_text_exp, total_voice_exp, total_bonus_exp FROM user_levels WHERE user_id = %s",
                    (user_id,),
                )
                return await cur.fetchone()
