/**
 * 各ユーザーのデータ
 *
 * @param {import('sequelize').Sequelize} sequelize
 * @param {import('sequelize').DataTypes} DataTypes
 */
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('users', {
        /**
         * ユーザーID
         */
        user_id: {
            type: DataTypes.STRING,
            primaryKey: true,
        },
        /**
         * Rank背景画像
         */
        rank_image: {
            type: DataTypes.BLOB,
            allowNull: true,
        },
    }, {
        indexes: [
            {
                unique: true,
                fields: ['user_id'],
            },
        ],
    });
};