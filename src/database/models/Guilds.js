/**
 * サーバーの設定
 *
 * @param {import('sequelize').Sequelize} sequelize
 * @param {import('sequelize').DataTypes} DataTypes
 */
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('users', {
        /**
         * ギルドID
         */
        guild_id: {
            type: DataTypes.STRING,
            primaryKey: true,
        },
        /**
         * このサーバーでのデフォルトのRank背景画像
         */
        rank_image: {
            type: DataTypes.BLOB,
            allowNull: false,
        },
        /**
         * 1メッセージで獲得できる経験値
         */
        msg_xp: {
            type: DataTypes.INTEGER,
            allowNull: false,
        },
        /**
         * 1メッセージで獲得できる経験値のクールダウン
         */
        msg_xp_cooldown: {
            type: DataTypes.INTEGER,
            allowNull: false,
        },
        /**
         * ロール報酬をスタックするか
         */
        stuck_role_rewards: {
            type: DataTypes.BOOLEAN,
            allowNull: false,
        },
    }, {
        indexes: [
            {
                unique: true,
                fields: ['guild_id'],
            },
        ],
    });
};