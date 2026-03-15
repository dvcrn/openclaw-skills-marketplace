# Gmail Tool Slugs (Connection / Toolkit Names)

This file lists Gmail toolkit slugs / action names that must be connected/allowed in Composio when using the secure-gmail skill. Use these exact slugs when creating scoped sessions or enabling tools.

- `GMAIL_MODIFY_LABELS` — Modify email labels for a single message (use `listLabels` to find custom label IDs).
- `GMAIL_BATCH_DELETE_MESSAGES` — Permanently delete multiple Gmail messages in bulk.
- `GMAIL_BATCH_MODIFY_MESSAGES` — Modify labels on multiple Gmail messages in one call (up to 1,000 messages).
- `GMAIL_CREATE_DRAFT` — Create an email draft (supports recipients, subject, HTML/plain body, attachments, threading).
- `GMAIL_CREATE_FILTER` — Create a Gmail filter with specified criteria and actions.
- `GMAIL_CREATE_LABEL` — Create a new label in the user's Gmail account.
- `GMAIL_DELETE_DRAFT` — Permanently delete a specific draft by ID.
- `GMAIL_DELETE_FILTER` — Delete a Gmail filter by its ID.
- `GMAIL_DELETE_LABEL` — Permanently delete a user-created label from the account (WARNING: removes label from all messages).
- `GMAIL_DELETE_MESSAGE` — Permanently delete a specific email message by ID.
- `GMAIL_DELETE_THREAD` — Permanently delete a thread and all its messages.
- `GMAIL_FETCH_EMAILS` — Fetch a list of email messages (filtering, pagination, optional full content).
- `GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` — Fetch a specific email message by its `message_id`.
- `GMAIL_FETCH_MESSAGE_BY_THREAD_ID` — Retrieve messages in a thread by `thread_id`.
- `GMAIL_FORWARD_MESSAGE` — Forward an existing Gmail message to recipients (preserves body and attachments).
- `GMAIL_GET_ATTACHMENT` — Retrieve a specific attachment by attachment ID.
- `GMAIL_GET_AUTO_FORWARDING_SETTINGS` — Get auto-forwarding settings for the account.
- `GMAIL_GET_CONTACTS` — Fetch contacts (connections) for the authenticated account.
- `GMAIL_GET_DRAFT` — Retrieve a specific draft by its ID.
- `GMAIL_GET_FILTER` — Retrieve a specific Gmail filter by ID.
- `GMAIL_GET_LABEL_DETAILS` — Get details for a specific Gmail label (name, type, visibility, color, counts).
- `GMAIL_GET_LANGUAGE_SETTINGS` — Retrieve language/display preferences for the account.
- `GMAIL_GET_PEOPLE` — Retrieve person details or list 'Other Contacts'.
- `GMAIL_GET_PROFILE` — Retrieve Gmail profile info (email address, message/thread totals, history ID).
- `GMAIL_GET_VACATION_SETTINGS` — Retrieve vacation responder settings.
- `GMAIL_IMPORT_MESSAGE` — Import a message into the mailbox (delivery scanning applies; not SMTP send).
- `GMAIL_INSERT_MESSAGE` — Insert a message into mailbox (like IMAP APPEND; bypasses some scanning).
- `GMAIL_LIST_CSE_IDENTITIES` — List client-side encrypted identities for a user.
- `GMAIL_LIST_CSE_KEY_PAIRS` — List client-side encryption key pairs for a user.
- `GMAIL_LIST_DRAFTS` — Retrieve a paginated list of drafts (use `verbose=true` for full details).
- `GMAIL_LIST_FILTERS` — List all Gmail filters in the mailbox.
- `GMAIL_LIST_FORWARDING_ADDRESSES` — List configured forwarding addresses.
- `GMAIL_LIST_HISTORY` — List mailbox change history since a `startHistoryId` (use for incremental sync).
- `GMAIL_LIST_LABELS` — List all system and user-created labels.
- `GMAIL_LIST_MESSAGES` — List messages in the mailbox (supports label or query filters).
- `GMAIL_LIST_SEND_AS_ALIASES` — List send-as aliases for the account.
- `GMAIL_LIST_SMIME_CONFIGS` — List S/MIME configs for a send-as alias.
- `GMAIL_LIST_THREADS` — List threads in the mailbox (supports filters and pagination).
- `GMAIL_MODIFY_THREAD_LABELS` — Add/remove label IDs for an entire thread.
- `GMAIL_MOVE_TO_TRASH` — Move a message to Trash (reversible until permanently deleted).
- `GMAIL_SEND_EMAIL` — Send an email message (supports To/Cc/Bcc, subject, body, attachments, send-as aliases).
- `GMAIL_SEND_DRAFT` — Send an existing draft by draft ID.

Note: Exact slug names may vary depending on the Composio toolkit version. If a slug differs, check the Composio Tools list in your dashboard (Tools → Gmail) for the canonical slug names and update this file accordingly.
