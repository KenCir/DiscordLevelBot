import asyncio
import os

import aiomysql


class Database:
    """
    データベース操作系クラス
    """

    def __init__(self):
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
                # ギルドの設定データ
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS guild_settings (guild_id BIGINT UNSIGNED PRIMARY KEY,"
                    "min_exp INT UNSIGNED NOT NULL, max_exp INT UNSIGNED NOT NULL,"
                    "stack_level_roles BOOLEAN NOT NULL,　created_at DATETIME DEFAULT CURRENT_TIMESTAMP,"
                    "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP)"
                )
                # ギルドのレベルロールデータ
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS guild_level_roles (guild_id BIGINT UNSIGNED,"
                    "role_id BIGINT UNSIGNED, level INT UNSIGNED NOT NULL,"
                    "created_at DATETIME DEFAULT CURRENT_TIMESTAMP,"
                    "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,"
                    "PRIMARY KEY (guild_id, role_id))"
                )
                # ユーザーのレベルデータ
                await cur.execute(
                    "CREATE TABLE IF NOT EXISTS user_levels (user_id BIGINT UNSIGNED, guild_id BIGINT UNSIGNED,"
                    "channel_id BIGINT UNSIGNED, exp INT UNSIGNED NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,"
                    "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,"
                    "PRIMARY KEY (user_id, guild_id, channel_id))"
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

    async def get_guild_setting(self, guild_id: int) -> tuple[int, int, bool]:
        """
        ギルドの設定データを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT min_exp, max_exp, stack_level_roles FROM guild_settings WHERE guild_id = %s",
                    (guild_id,),
                )
                result = await cur.fetchone()
                await conn.commit()

        return result if result else (15, 25, False)

    async def update_guild_setting(
        self,
        guild_id: int,
        min_exp: int = 15,
        max_exp: int = 25,
        stack_level_roles: bool = False,
    ) -> None:
        """
        ギルドの設定データを作成します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO guild_settings (guild_id, min_exp, max_exp, stack_level_roles) VALUES (%s, %s, %s, %s) AS new ON DUPLICATE KEY UPDATE min_exp = new.min_exp, max_exp = new.max_exp, stack_level_roles = new.stack_level_roles",
                    (guild_id, min_exp, max_exp, stack_level_roles),
                )
                await conn.commit()

    async def delete_guild_setting(self, guild_id: int) -> None:
        """
        ギルドの設定データを削除します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM guild_settings WHERE guild_id = %s",
                    (guild_id,),
                )
                await conn.commit()

    async def get_guild_level_roles(self, guild_id: int) -> list[tuple[int, int]]:
        """
        ギルドのレベルロールデータを全取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT role_id, level FROM guild_level_roles WHERE guild_id = %s ORDER BY level ASC",
                    (guild_id,),
                )
                result = await cur.fetchall()
                await conn.commit()

        return result

    async def get_guild_level_role(self, guild_id: int, role_id: int) -> int | None:
        """
        ギルドのレベルロールデータを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT level FROM guild_level_roles WHERE guild_id = %s AND role_id = %s",
                    (guild_id, role_id),
                )
                result = await cur.fetchone()
                await conn.commit()

        return result[0] if result else None

    async def create_guild_level_role(
        self, guild_id: int, role_id: int, level: int
    ) -> None:
        """
        ギルドのレベルロールデータを作成します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO guild_level_roles (guild_id, role_id, level) VALUES (%s, %s, %s)",
                    (guild_id, role_id, level),
                )
                await conn.commit()

    async def delete_guild_level_role(self, guild_id: int, role_id: int) -> None:
        """
        ギルドのレベルロールデータを削除します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM guild_level_roles WHERE guild_id = %s AND role_id = %s",
                    (guild_id, role_id),
                )
                await conn.commit()

    async def delete_all_guild_level_roles(self, guild_id: int) -> None:
        """
        ギルドのレベルロールデータを全て削除します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM guild_level_roles WHERE guild_id = %s",
                    (guild_id,),
                )
                await conn.commit()

    async def get_user_level(self, user_id: int, guild_id: int, channel_id: int) -> int:
        """
        ユーザーのレベルデータを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT exp FROM user_levels WHERE user_id = %s AND guild_id = %s AND channel_id = %s",
                    (user_id, guild_id, channel_id),
                )
                result = await cur.fetchone()
                await conn.commit()

        return result[0] if result else 0

    async def get_user_level_total(self, user_id: int, guild_id: int) -> int:
        """
        ユーザーのレベルデータの合計を取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT SUM(exp) FROM user_levels WHERE user_id = %s AND guild_id = %s",
                    (user_id, guild_id),
                )
                result = await cur.fetchone()
                await conn.commit()

        return result[0] if result else 0

    async def get_user_level_rank(
        self, user_id: int, guild_id: int, channel_id: int
    ) -> int | None:
        """
        ユーザーのランクを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "WITH ranked_users AS (SELECT user_id, RANK() OVER (ORDER BY exp DESC) AS ranking FROM user_levels WHERE guild_id = %s AND channel_id = %s) SELECT ranking FROM ranked_users WHERE user_id = %s",
                    (guild_id, channel_id, user_id),
                )
                result = await cur.fetchone()
                await conn.commit()

        return result[0] if result else None

    async def get_user_level_rank_total(
        self, user_id: int, guild_id: int
    ) -> int | None:
        """
        ユーザーのランクを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT ranking FROM (SELECT user_id, RANK() OVER (ORDER BY SUM(exp) DESC) AS ranking FROM user_levels WHERE guild_id = %s GROUP BY user_id) AS ranked_users WHERE user_id = %s",
                    (guild_id, user_id),
                )
                result = await cur.fetchone()
                await conn.commit()

        return result[0] if result else None

    async def get_user_level_ranking(
        self, guild_id: int, channel_id: int
    ) -> list[tuple[int, int, int]]:
        """
        チャンネルのランキングを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT user_id, exp, RANK() OVER (ORDER BY exp DESC) AS ranking FROM user_levels WHERE guild_id = %s AND channel_id = %s ORDER BY exp DESC",
                    (guild_id, channel_id),
                )
                result = await cur.fetchall()
                await conn.commit()

        return result

    async def get_user_level_ranking_total(
        self, guild_id: int
    ) -> list[tuple[int, int, int]]:
        """
        ギルドのランキングを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT user_id, SUM(exp) AS total_exp, RANK() OVER (ORDER BY SUM(exp) DESC) AS ranking FROM user_levels WHERE guild_id = %s GROUP BY user_id ORDER BY total_exp DESC",
                    (guild_id,),
                )
                result = await cur.fetchall()
                await conn.commit()

        return result

    async def get_user_level_ranking_channel(
        self, user_id: int, guild_id: int
    ) -> list[tuple[int, int, int]]:
        """
        ユーザーのチャンネルランキングを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT channel_id, exp, RANK() OVER (ORDER BY exp DESC) AS ranking FROM user_levels WHERE user_id = %s AND guild_id = %s ORDER BY exp DESC",
                    (user_id, guild_id),
                )
                result = await cur.fetchall()
                await conn.commit()

        return result

    async def get_user_level_ranking_total_channel(
        self, guild_id: int
    ) -> list[tuple[int, int, int]]:
        """
        チャンネルのランキングを取得します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT channel_id, SUM(exp) AS total_exp, RANK() OVER (ORDER BY SUM(exp) DESC) AS ranking FROM user_levels WHERE guild_id = %s GROUP BY channel_id ORDER BY total_exp DESC",
                    (guild_id,),
                )
                result = await cur.fetchall()
                await conn.commit()

        return result

    async def update_user_level(
        self, user_id: int, guild_id: int, channel_id: int, exp: int = 0
    ) -> None:
        """
        ユーザーのレベルデータを作成します
        すでに存在する場合は更新します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO user_levels (user_id, guild_id, channel_id, exp) VALUES (%s, %s, %s, %s) AS new ON DUPLICATE KEY UPDATE exp = user_levels.exp + new.exp",
                    (user_id, guild_id, channel_id, exp),
                )
                await conn.commit()

    async def remove_user_level_exp(
        self, user_id: int, guild_id: int, channel_id: int, exp: int = 0
    ) -> None:
        """
        ユーザーのレベルデータを作成します
        すでに存在する場合は更新します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE user_levels SET exp = GREATEST(user_levels.exp - %s, 0) WHERE user_id = %s AND guild_id = %s AND channel_id = %s",
                    (exp, user_id, guild_id, channel_id),
                )
                await conn.commit()

    async def delete_user_level(
        self, user_id: int, guild_id: int, channel_id: int
    ) -> None:
        """
        ユーザーのレベルデータを削除します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM user_levels WHERE user_id = %s AND guild_id = %s AND channel_id = %s",
                    (user_id, guild_id, channel_id),
                )
                await conn.commit()

    async def delete_user_level_total(self, user_id: int, guild_id: int) -> None:
        """
        ユーザーのレベルデータを削除します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM user_levels WHERE user_id = %s AND guild_id = %s",
                    (user_id, guild_id),
                )
                await conn.commit()

    async def delete_all_user_levels(self, guild_id: int) -> None:
        """
        ユーザーのレベルデータを全て削除します
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM user_levels WHERE guild_id = %s",
                    (guild_id,),
                )
                await conn.commit()
