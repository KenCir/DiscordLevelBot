const { Sequelize, DataTypes } = require('sequelize');
const sequelize = new Sequelize(process.env.MYSQL_DATABASE, process.env.MYSQL_USERNAME, process.env.MYSQL_PASSWORD, {
    host: process.env.MYSQL_HOST,
    port: process.env.MYSQL_PORT,
    dialect: 'mysql',
});
const GuildRoleRewards = require('./models/GuildRoleRewards')(sequelize, DataTypes);
const Guilds = require('./models/Guilds')(sequelize, DataTypes);
const Levels = require('./models/Levels')(sequelize, DataTypes);
const Users = require('./models/Users')(sequelize, DataTypes);
Guilds.hasMany(GuildRoleRewards, {
    foreignKey: 'guild_id',
    constraints: false,
});
GuildRoleRewards.belongsTo(Guilds, {
    foreignKey: 'guild_id',
    constraints: false,
});

class Database {
    /**
     * 接続を閉じる
     * @returns {Promise<void>}
     */
    async close() {
        return sequelize.close();
    }

    /**
     * ユーザーデータを取得
     * @param {string} userId
     * @returns {Promise<{ user_id: string, rank_image: Buffer }>}
     */
    getUser(userId) {
        return Users.findByPk(userId);
    }

    /**
     * ユーザーデータを作成
     * @param {string} userId
     * @param {Buffer|string} rankImage
     * @returns {Promise<any>}
     */
    async createUser(userId, rankImage) {
        if (await this.getUser(userId)) return;

        return Users.create({ user_id: userId, rank_image: rankImage });
    }

    /**
     * ユーザーデータをアップデート
     * @param {string} userId
     * @param {Buffer|string} rankImage
     * @returns {Promise<any>}
     */
    async updateUser(userId, rankImage) {
        if (!(await this.getUser(userId))) return this.createUser(userId, rankImage);

        return Users.update({ rank_image: rankImage }, { where: { user_id: userId } });
    }

    /**
     * ユーザーデータを削除
     * @param {string} userId
     * @returns {Promise<void>}
     */
    deleteUser(userId) {
        return Users.destroy({ where: { userId } });
    }
}

module.exports = Database;