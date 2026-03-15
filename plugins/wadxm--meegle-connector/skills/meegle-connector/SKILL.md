---
name: meegle-connector
description: "Connect to Meegle via MCP service, support OAuth authentication, and enable querying and managing work items, views, etc."
homepage: https://www.npmjs.com/package/mcporter
---

# Meegle Skill

Connect to Meegle via MCP Service, supporting OAuth authentication.

## Prerequisites

This skill relies on the following environment:

- **Node.js** (>= 18) and `npx`
- **mcporter**: MCP transfer tool, sourced from npm (`npm install -g mcporter` or automatically obtained via `npx`)

Credential storage path: `~/.mcporter/credentials.json` (automatically written after OAuth completion, containing access tokens)

## Connection Method

### 1. Ask the user which method to use for authentication

Note: Be sure to ask the user and let the user make an active choice. Automatically choosing for the user is prohibited.
This tool supports two authentication methods: one is to automatically re-engage the browser for OAuth (suitable for scenarios where OpenClaw is installed locally), and the other is to authenticate via an OAuth proxy (suitable for scenarios where OpenClaw is installed on a remote server).

### 2. If the user chooses the first method, the authorization method is as follows

#### 2.1. Create a Configuration File

Copy `meegle-config.json` from the skill package directory to the working directory

#### 2.2. Perform OAuth authentication (only once)

```bash
npx mcporter auth meegle --config meegle-config.json
```

This will open a browser for you to authorize your Meegle account. ** After authorization is completed, the credentials will be cached in `~/.mcporter/credentials.json`, and subsequent calls will not require re-authorization. **

### 3. If the user chooses the second method, the authorization method is as follows

#### 3.1. Create a Configuration File

Copy `meegle-config.json` from the skill package directory to the working directory

#### 3.2. Perform OAuth authentication (only once)
```bash
npx mcporter auth meegle --config meegle-config.json --oauth-timeout 1000
```

This will cause mcporter to generate an OAuth Client configuration for Meegle that does not include a token, with the path located in `~/.mcporter/credentials.json`.

#### 3.3. Prompt the user for local authorization

Send the file content to the user in the following format, and refrain from modifying any expressions other than the file content:

```plain
OAuth configuration has been generated!
[File content]
Please refer to the instructions in the document https://project.feishu.cn/b/helpcenter/1ykiuvvj/1n3ae9b4 to authorize on your local computer. After authorization is completed, please send the credential file to me. Note that the returned file will contain token information, so be sure to send it through a secure communication channel, and it is recommended to destroy the file after sending.
```

After receiving the file sent by the user, use the new file to overwrite the `~/.mcporter/credentials.json` file on the local machine.
**Note: The credential.json file sent back by the user contains token information for accessing Meegle. Please ensure that it is only stored as the login credential for mcporter in ~/.mcporter. Storing or recording it in any other location is prohibited. If intermediate cache files are involved during the process, they must be cleaned up promptly.**

#### 3.4. Verify the Authorization Result

Attempted to connect to the MCP server and confirmed successful authorization.

### 4. Subsequent Use

```bash
npx mcporter call meegle <tool_name> --config meegle-config.json
```

## Available Features

- **Query**: To-do, View, Work Item Information
- **Operation**: Create, modify, and transfer work items
