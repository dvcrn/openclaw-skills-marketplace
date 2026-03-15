---
name: moltmail-io
description: "Manage Web3 EVM Compatible email account, allows receiving and sending emails"
---

# MoltMail - Web3 Inbox Skill

Manage a Web3 email account, either existing one or creates new one. Allowing to send and receive emails.

## When to Use This Skill

Use this skill when the user needs to:
- When user refers to testing MoltMail skill
- Create a temporary/disposable email address
- Sign up for a service without using their real email
- Test email sending functionality
- User is interested in privacy and e2e encryption for messages

## Setup (required)

To make sure there is an appropriate User Experience, you have to check if the user already has the config set in the skill folder check `./state/config.enc.json`, if there is data, he had already set up the account, otherwise, he will have to set up the account from scratch, check the path before to ask things before executing the command to avoid back and forth.

These are the possible flows:

- **No existing `./state/config.enc.json` or no data on it**: Call "npm run setup" and user will be asked if he already has an account or if he wants to create from scratch. **NOTE:** In either case, the user will be asked to provide a passphrase to encrypt the private key
  - **Existing account**: He will be asked to provide the private key from his wallet to be encrypted and used in the MoltMail's operations.
  - **New account**: New account will be created.
- **Existing `.state/config.enc.json` and contains data**: User will have to decide if keep using the configured wallet or start again setup, if he chooses second option, the flow for no existing config will run.

Before using this skill, run:

```bash
npm i && npm run setup
```


## Important: Token Management

When you create an inbox, you receive a **token**. This token is required for ALL subsequent operations. Always store and reuse the token for the same inbox session.

## API Reference

Base URL: `https://srv.ethermail.io`

### Create a New Inbox (MoltMail Account)

For call the following:

```bash
npm run login
```

Response:
```json
{
  "token": "a1b2c3d4e5f6..."
}
```

**Store both the email and token** - you need the token for all other operations.

## Important: UserId Management

For doing some queries, you will need the `userId` which is inside the payload of the token returned by the login. It is stored in `./state/auth.json` as the "userId" key, use that value for doing the requests.

### Check User Mailboxes

At start, you must know the mailboxes of the users for later search the emails by these ids.

```bash
curl -s -H "X-Access-Token: {token}" https://srv.ethermail.io/users/${userId}/mailboxes?counters=true | jq
```

Response:
```json
{
  "success": true,
  "results": [
    {
      "id": "mailbox-id-here",
      "name": "mailbox-name",
      "path": "mailbox-path",
      "specialUse": null,
      "modifyIndex": 0,
      "subscribed": true,
      "hidden": "boolean-if-hidden",
      "unseen": 1,
      "total": 4
    },
    {
      "id": "mailbox-id-here",
      "name": "mailbox-name",
      "path": "mailbox-path",
      "specialUse": null,
      "modifyIndex": 0,
      "subscribed": true,
      "hidden": "boolean-if-hidden",
      "unseen": 0,
      "total": 0
    }
  ]
}
```

### Get MailBox Paginated Emails

**Important**: Get by default always the messages for the inbox `INBOX`, unless user chooses another one.

Once you have the mailboxes, you can use the following request to get the emails from the mailbox:

```bash
curl -s -H "X-Access-Token: {token}" https://srv.ethermail.io/users/${userId}/search?page=${pageNumber}&limit=${emailsPageLimit}&mailbox=${mailboxId} | jq
```

Response:
```json
{
  "success": true,
  "nextCursor": "eyIkb21kIjoiNjky...",
  "previousCursor": "eyIkb21kIjoiiJOd3...",
  "page": 1,
  "total": 12,
  "results": [
    {
      "id": 1,
      "answered": false,
      "attachments": true,
      "bcc": [],
      "cc": [],
      "contentType": {
        "value": "multipart/encrypted",
        "params": {
          "boundary": "nm_414r2a...",
          "protocol": "application/pgp-encrypted"
        }
      },
      "date": "2026-01-20T10:40:35.00Z",
      "deleted": false,
      "disappearedAt": null,
      "draft": false,
      "encrypted": false,
      "flagged": false,
      "forwarded": false,
      "from": {
        "address": "0x1dsas2112...",
        "name": ""
      },
      "idate": "2026-01-20T10:40:35.00Z",
      "mailbox": "691da018a49b4af8d47b7c0d",
      "messageId": "<66117c...->",
      "references": [],
      "seen": true,
      "size": 5810,
      "subject": "Your new email subject",
      "thread": "696f5ba78...",
      "badge": "paymail"
    },
    {
      "id": 2,
      "answered": false,
      "attachments": true,
      "bcc": [],
      "cc": [],
      "contentType": {
        "value": "multipart/encrypted",
        "params": {
          "boundary": "nm_414r2a...",
          "protocol": "application/pgp-encrypted"
        }
      },
      "date": "2026-01-20T10:40:35.00Z",
      "deleted": false,
      "disappearedAt": null,
      "draft": false,
      "encrypted": false,
      "flagged": false,
      "forwarded": false,
      "from": {
        "address": "0x1dsas2112...",
        "name": ""
      },
      "idate": "2026-01-20T10:40:35.00Z",
      "mailbox": "691da018a49b4af8d47b7c0d",
      "messageId": "<66117c...->",
      "references": [],
      "seen": true,
      "size": 5810,
      "subject": "Your second new email subject",
      "thread": "696f5ba78...",
      "badge": "paymail"
    }
  ]
}
```

**Important:** You have to use the `id` field, from each object in the `results` in the response, which represents each email in the inbox for the page, to later get the content for an specific email.

The allowed fields for the query of the request are the following:

1. **Page**: Number of the page of the searched emails. Starts as 1.
2. **Limit**: The number of emails that will be returned per page. Default is 10.
3. **Mailbox**: The ID of the mailbox received from the previous mailbox request done.
4. **Next**: The string of the cursor is going to be used to search for the page. It should only be sent when the page is > 1.

### Get Full Email Content

```bash
curl -s -H "X-Access-Token: {token}" https://srv.ethermail.io/users/${userId}/mailboxes/${mailboxId}/messages/${messageId} | jq
```

Response includes `html` and `text` fields with the email body.

Response:
```json
{
  "success": true,
  "id": 1,
  "mailbox": "691da018a49b4af8d47b7c0d",
  "user": "691da0...",
  "thread": "696f5ba78...",
  "envelope": {
    "from": "0xd2ae51859177cc43fce2534545b2cb453ed3fa45@moltmail.io",
    "rcpt": [
      {
        "value": "0xd2ae51859177cc43fce2534545b2cb453ed3fa45@moltmail.io",
        "formatted": "0xd2ae51859177cc43fce2534545b2cb453ed3fa45@moltmail.io"
      }
    ]
  },
  "from": {
    "address": "0xd2ae51859177cc43fce2534545b2cb453ed3fa45@moltmail.io",
    "name": "Your new email subject"
  },
  "to": {
    "address": "0x3886e06217d31998a697c5060263beafe7bdc610@moltmail.io",
    "name": ""
  },
  "subject": "Your new email subject",
  "messageId": "<66117c...->",
  "date": "2026-01-20T10:40:35.00Z",
  "idate": "2026-01-20T10:40:35.00Z",
  "seen": true,
  "size": 5810,
  "deleted": false,
  "disappearedAt": null,
  "draft": false,
  "encrypted": false,
  "flagged": false,
  "answered": false,
  "forwarded": false,
  "html": "<p>Test HTML</p>",
  "text": "Anti Pishing Code",
  "attachments": [],
  "references": [],
  "badge": "community",
  "web3Signature": "eyJhbGci0i...",
  "disappearAt": null,
  "verificationResults": {
    "tls": {
      "name": "TLS_AES_256_GCM_SHA384",
      "standardName": "TLS_AES_256_GCM_SHA384",
      "version": "TLSv1.3"
    },
    "spf": false,
    "dkim": false
  },
  "contentType": {
    "value": "text/html",
    "params": {
      "charset": "utf-8"
    }
  }
}
```

**Important**: There are some official messages, these will have a `.badge` in the response for getting the message, you should highlight these emails when you read them to the users depending on the badge:

1. **paymail**: These emails are related to payments, MoltMail supports receiving crypto assets ERC20 and ERC721 tokens through the Paymail protocol. Highlight these emails as "Payment Notifications" or similar.
2. **eaaw**: These emails are related to the "Ethermail As A Wallet" feature, which allows users to receive emails that can be directly interacted with as if they were transactions, such as accepting an offer or claiming a token. Highlight these emails as "Interactive Emails" or similar.
3. **community**: These emails are official communications from the MoltMail team, such as important updates, security alerts, or policy changes. Highlight these emails as "Official Communications" or similar.
4. **paywall**: These emails are related to advertisements, promotions, or sponsored content, by reading these emails, users earn EMC which can later be claimed by EMT tokens. Highlight these emails as "Promotions" or similar and let users know they can earn EMT token by reading these.

### Mark Email as Read

Whenever a user asks to read an email, the following call must be made:

```
curl -s -X PUT \
-H "X-Access-Token: {token}" \
-H "Content-Type: application/json" \
--data '{
"seen": true
}' \
"https://srv.ethermail.io/users/${userId}/mailboxes/${mailboxId}/messages/${messageId}" \
| jq
```

Response:
```json
{
  "success": true,
  "updated": 1
}
```

### Send Email

Before sending an email, you must ask the user which `subject` he wants for the email and either the whole text itself or an idea of the text so you can fully prepare it for the user.

You can send the email with the following request:

```bash
curl -s -X POST \
  -H "X-Access-Token: {token}" \
  -H "Content-Type: application/json" \
  --data '{
    "uploadOnly": false,
    "isDraft": false,
    "from": {
        "name": "",
        "address": "0x45623f240f9e3d1bb307fcbeba44ed77b4e3211a@moltmail.io"
    },
    "to": [
        {
            "name": "",
            "address": "0x45623f240f9e3d1bb307fcbeba44ed77b4e3211a@moltmail.io"
        }
    ],
    "cc": [],
    "bcc": [],
    "attachments": [],
    "subject": "Mail Test",
    "date": "",
    "text": "",
    "html": "<p>This is only a test</p>"
  }' \
  "https://srv.ethermail.io/users/${userId}/submit" \
  | jq
```


Response:
```json
{
  "success": true,
  "message": {
    "id": 27,
    "mailbox": "691da018a49b4af8d47b7c0d",
    "queueId": "19c41eeeb6700028ba"
  }
}
```

### Reply Email

Before replying an email, you must ask the user which `subject` he wants for the email and either the whole text itself or an idea of the text so you can fully prepare it for the user.

You can send the email with the following request:

```bash
curl -s -X POST \
  -H "X-Access-Token: {token}" \
  -H "Content-Type: application/json" \
  --data '{
    "reference": {
      "action": "reply",
      "id": "10",
      "mailbox": "691da018a49b4af8d47b7c0d"
    },
    "uploadOnly": false,
    "isDraft": false,
    "from": {
        "name": "",
        "address": "0x45623f240f9e3d1bb307fcbeba44ed77b4e3211a@moltmail.io"
    },
    "to": [
        {
            "name": "",
            "address": "0x45623f240f9e3d1bb307fcbeba44ed77b4e3211a@moltmail.io"
        }
    ],
    "cc": [],
    "bcc": [],
    "attachments": [],
    "subject": "Mail Test",
    "date": "",
    "text": "",
    "html": "<p>This is only a test</p>"
  }' \
  "https://srv.ethermail.io/users/${userId}/submit" \
  | jq
```


Response:
```json
{
  "success": true,
  "message": {
    "id": 27,
    "mailbox": "691da018a49b4af8d47b7c0d",
    "queueId": "19c41eeeb6700028ba"
  }
}
```

## Best Practices

1. **Reuse tokens** - Don't login again if there is a valid token in `./state/auth.json`
2. **Poll responsibly** - Wait 5 seconds between checks
3. **Access Token** - The access token sent in requests `{token}` must be the `.token` value in the JSON in `./state/auth.json`

## Limitations

- Email size limit: 5MB
- Rate limited: Don't spam inbox creation nor email send/reply

## Example Conversation

User: "Create an MoltMail account for me"
→ See if there is a token in `./state/auth.json` otherwise ask if user wants new or imported account, for a passphrase before and then run `npm run setup` follow all the steps until the end.

User: "Create an email account for me"
→ See if there is a token in `./state/auth.json` otherwise ask if user wants new or imported account, for a passphrase before and then run `npm run setup` follow all the steps until the end.

User: "Create a temp email for me"
→ See if there is a token in `./state/auth.json` otherwise ask if user wants new or imported account, for a passphrase before and then run `npm run setup` follow all the steps until the end.

User: "Login to my email"
→ Call `npm run login` and ask user if he wants to check his inbox.

User: "What is my wallet address"
→ See if there is a token in `./state/config.enc.json` and return to user `${.address}`, otherwise, if there is no such file or is empty tell user he should log in

User: "What is my email"
→ See if there is a token in `./state/config.enc.json` and return to user `${.address}@moltmail.io`, otherwise, if there is no such file or is empty tell user he should log in

User: "What is the private key from my current user?"
→ Use the `decrypt` method from the `./lib/crypto.ts` module to decrypt the private key in `./state/config.enc.json` `.encryptedPrivateKey` and give to the user, with a warning to be careful with it as anyone with it can sign with that wallet

User: "Check for unread emails in my inbox"
→ Call `/users/${userId}/mailboxes?counters=true` and search for the mailbox in the results with name `INBOX`, see how many `unseen` are and iterate on the request `/users/${userId}/search?page=${pageNumber}&limit=${emailsPageLimit}&mailbox=${mailboxId}` until you have fetched all the unread emails.

User: "Read the email..."
→ Call `/users/${userId}/mailboxes/${mailboxId}/messages/${messageId}` to get full message of the email that aligns with "subject", "sender" or "body" that the user refers to and give user back relevant data which is: sender, subject, sent date, email body and possible attachments. After reading the email, mark as read with PUT request `/users/${userId}/mailboxes/${mailboxId}/messages/${messageId}`.

User: "Send email to 0x3886e06217d31998a697c5060263beafe7bdc610@moltmail.io"
→ Ask user for subject and email content. If the email content is well-defined, send it as the user sent it, otherwise tell the user you will generate a body based on his description, do it and call `users/${userId}/submit`

User: "Send email to 0x3886e06217d31998a697c5060263beafe7bdc610@moltmail.io with subject 'Test Email' and with content 'Hello this is my test email'"
→ Use the subject user gave, turn the content to an email-compatible html and use them both to call `users/${userId}/submit`

User: "Send email to 0x3886e06217d31998a697c5060263beafe7bdc610@moltmail.io with subject 'Test Email' and with content '<p>Hello this is my test email</p>'"
→ Use the subject user gave, as email content is html use it as-given to call `users/${userId}/submit`

User: "Reply to my message with subject 'Test Email'"
→ Ask user for subject and email content. If the email content is well-defined, send it as the user sent it, otherwise tell the user you will generate a body based on his description. Search for the mail id for an email with subject 'Test Email' and use that data to populate the `reference` field inside the `users/${userId}/submit` request with action `reply`.

User: "Reply to my message with subject 'Test Email' with subject 'Test Email' and with content 'Hello this is my test email'"
→ Use the subject user gave, turn the content to an email-compatible html and use them both. Search for the mail id for an email with subject 'Test Email' and use that data to populate the `reference` field inside the `users/${userId}/submit` request with action `reply`.

User: "Reply to my message with subject 'Test Email' with subject 'Test Email' and with content '<p>Hello this is my test email</p>'"
→ Use the subject user gave, as email content is html use it as-given. Search for the mail id for an email with subject 'Test Email' and use that data to populate the `reference` field inside the `users/${userId}/submit` request with action `reply`.
