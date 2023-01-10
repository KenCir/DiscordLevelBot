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
     * @returns {Promise<{ user_id: string, rank_image: Buffer|null }>}
     */
    getUser(userId) {
        return Users.findByPk(userId);
    }

    /**
     * ユーザーデータを作成
     * @param {string} userId
     * @param {Buffer|string|null} rankImage
     * @returns {Promise<any>}
     */
    async createUser(userId, rankImage) {
        if (await this.getUser(userId)) return;

        return Users.create({ user_id: userId, rank_image: rankImage });
    }

    /**
     * ユーザーデータをアップデート
     * @param {string} userId
     * @param {Buffer|string|null} rankImage
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

    /**
     * レベルデータを取得
     * @param {userId} userId
     * @param {guildId} guildId
     * @returns {Promise<{ id: string, user_id: string, guild_id: string, xp: number } | null>}
     */
    getLevel(userId, guildId) {
        return Levels.findByPk(`${userId}-${guildId}`);
    }

    /**
     * レベルデータの全データを取得
     * @param {string} guildId
     */
    getAllLevel(guildId) {
        return Levels.findAll({
            where: {
                guild_id: guildId,
            },
            order: [
                ['xp', 'DESC'],
            ],
        });
    }

    /**
     * レベルデータを作成
     * @param {string} userId
     * @param {string} guildId
     * @param {number} xp
     * @returns {Promise<any>}
     */
    async createLevel(userId, guildId, xp) {
        if (await this.getLevel(userId, guildId)) return;

        return Levels.create({ id: `${userId}-${guildId}`, user_id: userId, guild_id: guildId, xp: xp });
    }

    /**
     * レベルデータを更新
     * @param {string} userId
     * @param {string} guildId
     * @param {number} xp
     * @returns {Promise<any>}
     */
    async updateLevel(userId, guildId, xp) {
        if (!(await this.getLevel(userId, guildId))) return this.createLevel(userId, guildId, xp);

        return Levels.update({ xp: xp }, { where: { id: `${userId}-${guildId}` } });
    }

    /**
     * レベルデータを削除
     * @param {string} userId
     * @param {string} guildId
     */
    deleteLevel(userId, guildId) {
        Levels.destroy({ where: { id: `${userId}-${guildId}` } });
    }

    /**
     * ギルドデータの取得
     * @param {string} guildId
     * @returns {Promise<{ guild_id: string, rank_image: Buffer|null, msg_xp: number, msg_xp_cooldown: number, stuck_role_rewards: boolean } | null>}
     */
    getGuild(guildId) {
        return Guilds.findByPk(guildId, {
            include: [GuildRoleRewards],
        });
    }

    /**
     * ギルドデータの作成
     * @param {string} guildId
     * @param {Buffer|string|null} rankImage
     * @param {number} msgXP
     * @param {number} msgXPCoolDown
     * @param {boolean} stuckRoleRewards
     */
    async createGuild(guildId, rankImage, msgXP, msgXPCoolDown, stuckRoleRewards) {
        if (await this.getGuild(guildId)) return;

        return Guilds.create({ guild_id: guildId, rank_image: rankImage, msg_xp: msgXP, msg_xp_cooldown: msgXPCoolDown, stuck_role_rewards: stuckRoleRewards });
    }

    /**
     * ギルドデータの更新
     * @param {string} guildId
     * @param {Buffer|string|null} rankImage
     * @param {number} msgXP
     * @param {number} msgXPCoolDown
     * @param {boolean} stuckRoleRewards
     */
    async updateGuild(guildId, rankImage, msgXP, msgXPCoolDown, stuckRoleRewards) {
        if (!(await this.getGuild(guildId))) return this.createGuild(guildId, rankImage, msgXP, msgXPCoolDown, stuckRoleRewards);

        return Guilds.update({ rank_image: rankImage, msg_xp: msgXP, msg_xp_cooldown: msgXPCoolDown, stuck_role_rewards: stuckRoleRewards }, { where: { guild_id: guildId } });
    }

    /**
     * ギルドデータの削除
     * @param {string} guildId
     * @returns {Promise<void>}
     */
    deleteGuild(guildId) {
        return Guilds.destroy({ guild_id: guildId });
    }
}

module.exports = Database;