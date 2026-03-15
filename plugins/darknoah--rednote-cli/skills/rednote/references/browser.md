# Browser Commands

Load this reference only when the user needs detailed browser subcommand syntax, flags, or examples.

## `browser list`

List browser instances:

```bash
rednote browser list
```

Use `browser list` to inspect default browsers, custom instances, stale locks, ports, and the current `lastConnect` target.

## `browser create`

Create a reusable named browser instance:

```bash
rednote browser create --name seller-main --browser chrome --port 9222
```

Use `browser create` to create a dedicated profile for later `connect`, `login`, `publish`, `search`, `get-feed-detail`, or `interact` commands.

## `browser connect`

Connect to an existing named instance:

```bash
rednote browser connect --instance seller-main
```

Connect to a browser by explicit profile path:

```bash
rednote browser connect --browser edge --user-data-dir /tmp/edge-profile --port 9223
```

Force reconnect when the profile is blocked by a stale lock:

```bash
rednote browser connect --instance seller-main --force
```

Use `browser connect` before `login`, `check-login`, `status`, `home`, `search`, `get-feed-detail`, `get-profile`, `publish`, or `interact`.

## `browser remove`

Remove a named instance:

```bash
rednote browser remove --name seller-main
```

Use `browser remove` when the user wants to delete an obsolete custom browser instance and its managed profile.
