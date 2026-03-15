const fs = require('fs');
const path = require('path');
const os = require('os');
const RTMClient = require('./rtm-client');

// Using the provided keys
const API_KEY = 'e722a3fa98943b14145c599c9b429bec';
const SHARED_SECRET = '477f54b2c6b4f874';
const TOKEN_FILE = path.join(os.homedir(), '.rtm-token.json');

module.exports = {
    name: 'rtm-skill',
    version: '1.0.0',
    register: function (context) {
        const logger = context.logger || console;
        logger.info('[rtm-skill] registering skill');

        const client = new RTMClient(API_KEY, SHARED_SECRET);

        // Try to load token from disk
        try {
            if (fs.existsSync(TOKEN_FILE)) {
                const data = fs.readFileSync(TOKEN_FILE, 'utf8');
                const parsed = JSON.parse(data);
                if (parsed.token) {
                    client.setToken(parsed.token);
                    logger.info('[rtm-skill] loaded auth token from disk');
                }
            }
        } catch (err) {
            logger.error('[rtm-skill] failed to load token:', err.message);
        }

        // In-memory mappings to allow short IDs for user commands
        let taskCache = [];

        context.registerCommand && context.registerCommand({
            name: 'rtm',
            description: 'Manage Remember The Milk tasks (rtm auth, list, add, complete, delete)',
            async handler({ argv, reply }) {
                const subcmd = argv[0] || 'list';

                try {
                    if (subcmd === 'auth') {
                        const frob = await client.getFrob();
                        // In a real scenario we might save frob to disk temporarily, but here we'll just ask the user to pass it
                        const url = client.getAuthUrl();
                        const msg = `Please open this URL in your browser to authorize:\n${url}\n\nOnce authorized, run: rtm token ${frob}`;
                        if (reply) await reply(msg);
                        return msg;
                    }

                    if (subcmd === 'token') {
                        const frob = argv[1];
                        if (!frob) throw new Error('You must provide the frob from the auth command: rtm token <frob>');
                        const token = await client.getToken(frob);
                        client.setToken(token);
                        fs.writeFileSync(TOKEN_FILE, JSON.stringify({ token }));
                        const msg = `Success! RTM is authorized. Token saved.`;
                        if (reply) await reply(msg);
                        return msg;
                    }

                    // Require token for the rest
                    if (!client.token) {
                        throw new Error('Not authorized. Run `rtm auth` first.');
                    }

                    if (subcmd === 'list') {
                        const tasks = await client.getTasks('status:incomplete');
                        const listsObj = await client.getLists();

                        // map list ids to names
                        const listMap = {};
                        if (listsObj) {
                            const listsArr = Array.isArray(listsObj) ? listsObj : [listsObj];
                            for (const l of listsArr) {
                                listMap[l.id] = l.name;
                            }
                        }

                        taskCache = tasks; // Save for short ID mapping

                        if (tasks.length === 0) {
                            const msg = "No incomplete tasks found!";
                            if (reply) await reply(msg);
                            return msg;
                        }

                        let output = "📝 Your Tasks:\n";
                        tasks.forEach((t, i) => {
                            const shortId = i + 1;
                            const cat = listMap[t.list_id] || 'Inbox';
                            let line = `[${shortId}] [${cat}] ${t.name}`;

                            const extras = [];
                            if (t.priority && t.priority !== 'N') extras.push(`Priority: ${t.priority}`);
                            if (t.due) extras.push(`Due: ${t.due}`);
                            if (t.tags && t.tags.length > 0) extras.push(`Tags: ${t.tags.join(', ')}`);

                            const validNotes = (t.notes || []).filter(n => n && n.$t).map(n => n.$t).join('; ');
                            if (validNotes) extras.push(`Notes: ${validNotes}`);

                            if (extras.length > 0) {
                                line += ` (${extras.join(' | ')})`;
                            }
                            output += line + '\n';
                        });

                        if (reply) await reply(output);
                        return output;
                    }

                    if (subcmd === 'add') {
                        const name = argv.slice(1).join(' ');
                        if (!name) throw new Error('Provide a task name: rtm add <name>');
                        const tl = await client.createTimeline();
                        await client.addTask(tl, name);
                        const msg = `✅ Added task: "${name}"`;
                        if (reply) await reply(msg);
                        return msg;
                    }

                    if (subcmd === 'complete' || subcmd === 'delete') {
                        const shortIdStr = argv[1];
                        if (!shortIdStr) throw new Error(`Provide a task ID: rtm ${subcmd} <id> (you can get the ID from 'rtm list')`);
                        const idx = parseInt(shortIdStr, 10) - 1;

                        if (taskCache.length === 0) {
                            throw new Error('Please run `rtm list` first so I can find the task IDs.');
                        }
                        if (idx < 0 || idx >= taskCache.length) {
                            throw new Error(`Invalid task ID. Must be between 1 and ${taskCache.length}.`);
                        }

                        const task = taskCache[idx];
                        const tl = await client.createTimeline();

                        if (subcmd === 'complete') {
                            await client.completeTask(tl, task.list_id, task.taskseries_id, task.task_id);
                            const msg = `✔️ Completed task: "${task.name}"`;
                            if (reply) await reply(msg);
                            return msg;
                        } else {
                            await client.deleteTask(tl, task.list_id, task.taskseries_id, task.task_id);
                            const msg = `🗑️ Deleted task: "${task.name}"`;
                            if (reply) await reply(msg);
                            return msg;
                        }
                    }

                    throw new Error(`Unknown subcommand: ${subcmd}`);

                } catch (err) {
                    const msg = `❌ RTM Error: ${err.message}`;
                    logger.error(msg);
                    if (reply) await reply(msg);
                    return msg;
                }
            }
        });
    }
};
