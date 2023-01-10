/**
 * 各レベルのデータ
 *
 * @param {import('sequelize').Sequelize} sequelize
 * @param {import('sequelize').DataTypes} DataTypes
 */
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('levels', {
        /**
         * 管理用ID
         * ユーザーID-ギルドID
         */
        id: {
            type: DataTypes.STRING,
            primaryKey: true,
        },
        /**
         * ユーザーID
         */
        user_id: {
            type: DataTypes.STRING,
            allowNull: false,
        },
        /**
         * ギルドID
         */
        guild_id: {
            type: DataTypes.STRING,
            allowNull: false,
        },
        /**
         * 経験値
         */
        xp: {
            type: DataTypes.INTEGER,
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