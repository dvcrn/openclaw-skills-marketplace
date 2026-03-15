# Node bootstrap playbook

Use this when the gateway is running on a Linux box or VPS and you want the first Microsoft trust ceremony to happen from a paired Mac.

## Pattern

1. Install the skill bundle in the workspace or managed skills location.
2. Inject all tenant secrets through OpenClaw `skills.entries.caduceusmail.env`.
3. Run the doctor on the gateway. It will usually recommend device auth for headless environments.
4. If a paired Mac node is available and approved for execution, run the bootstrap from the Mac node so the human login happens on a comfortable machine.
5. After the bootstrap succeeds, switch normal runs to `--skip-m365-bootstrap` so the gateway can operate headlessly.

## Why this works

The first run is about delegated approval and RBAC setup. Steady state is about app credentials, Graph, Exchange app auth, and DNS control. They are not the same phase and should not be treated as the same phase.
