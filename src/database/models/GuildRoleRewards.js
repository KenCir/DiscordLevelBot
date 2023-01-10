/**
 * サーバーのレベル毎によるロール報酬
 *
 * @param {import('sequelize').Sequelize} sequelize
 * @param {import('sequelize').DataTypes} DataTypes
 */
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('guild_role_rewards', {
        id: {
            type: DataTypes.STRING,
            primaryKey: true,
        },
        /**
         * ギルドID
         */
        guild_id: {
            type: DataTypes.STRING,
            allowNull: false,
        },
        /**
         * 報酬を獲得するレベル
         */
        level: {
            type: DataTypes.INTEGER,
            allowNull: false,
        },
        /**
         * ロールID
         */
        role_id: {
            type: DataTypes.STRING,
            allowNull: false,
        },
    }, {
        indexes: [
            {
                unique: true,
                fields: ['id'],
            },
        ],
    });
};