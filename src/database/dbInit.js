require('dotenv').config();
const { Sequelize, DataTypes } = require('sequelize');

const sequelize = new Sequelize(process.env.MYSQL_DATABASE, process.env.MYSQL_USERNAME, process.env.MYSQL_PASSWORD, {
    host: process.env.MYSQL_HOST,
    port: process.env.MYSQL_PORT,
    dialect: 'mysql',
});

const GuildRoleRewards = require('./models/GuildRoleRewards')(sequelize, DataTypes);
const Guilds = require('./models/Guilds')(sequelize, DataTypes);
require('./models/Levels')(sequelize, DataTypes);
require('./models/Users')(sequelize, DataTypes);

Guilds.hasMany(GuildRoleRewards, {
    foreignKey: 'guild_id',
    constraints: false,
});
GuildRoleRewards.belongsTo(Guilds, {
    foreignKey: 'guild_id',
    constraints: false,
});


const force = process.argv.includes('--force') || process.argv.includes('-f');

sequelize.sync({ force }).then(async () => {
    console.log('Database synced');
    sequelize.close();
}).catch(console.error);