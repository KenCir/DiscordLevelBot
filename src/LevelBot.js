const { Client, IntentsBitField, Collection } = require('discord.js');
const { getLogger, configure } = require('log4js');

class LevelBot extends Client {
    constructor() {
        super({
            intents: [
                IntentsBitField.Flags.Guilds,
                IntentsBitField.Flags.GuildMessages,
                IntentsBitField.Flags.GuildMembers,
            ],
        });

        configure({
            appenders: {
                out: { type: 'stdout', layout: { type: 'coloured' } },
                app: { type: 'file', filename: 'logs/levelbot.log', pattern: 'yyyy-MM-dd.log' },
            },
            categories: {
                default: { appenders: ['out', 'app'], level: 'all' },
            },
        });

        this.logger = getLogger('LevelBot');

        /**
         * @type {import('discord.js').Collection<string, { info: { name: string, description: string, category: string, defer: boolean, ephemeral: boolean }, data: import('@discordjs/builders').SlashCommandBuilder, run: function(LevelBot, import('discord.js').CommandInteraction): Promise<void>, runMessage: function(LevelBot, import('discord.js').Message, string[]): Promise<void>  }}
         */
        this.commands = new Collection();
    }


}

module.exports = LevelBot;