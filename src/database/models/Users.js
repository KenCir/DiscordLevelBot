/**
 * 各ユーザーのデータ
 *
 * @param {import('sequelize').Sequelize} sequelize
 * @param {import('sequelize').DataTypes} DataTypes
 */
module.exports = (sequelize, DataTypes) => {
    return sequelize.define('users', {
        user_id: {
            type: DataTypes.STRING,
            primaryKey: true,
        },
        rank_image: {
            type: DataTypes.BLOB,
            allowNull: false,
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