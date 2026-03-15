const DOCUSEAL_URL = process.env.DOCUSEAL_URL
const DOCUSEAL_MCP_TOKEN = process.env.DOCUSEAL_MCP_TOKEN

if (!DOCUSEAL_URL || !DOCUSEAL_MCP_TOKEN) {
  console.error('Set DOCUSEAL_URL and DOCUSEAL_MCP_TOKEN environment variables')
  process.exit(1)
}

let requestId = 0

function parseArgs (argv) {
  const positional = []
  const named = {}

  for (const arg of argv) {
    const match = arg.match(/^--(\w[\w-]*)=(.*)$/)

    if (match) {
      named[match[1]] = match[2]
    } else {
      positional.push(arg)
    }
  }

  return { positional, named }
}

async function rpc (method, params) {
  const res = await fetch(`${DOCUSEAL_URL}/mcp`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${DOCUSEAL_MCP_TOKEN}`
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: ++requestId,
      method,
      params
    })
  })

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`)
  }

  return res.json()
}

function callTool (name, args) {
  return rpc('tools/call', { name, arguments: args })
}

const commands = {
  init: () => rpc('initialize'),

  tools: () => rpc('tools/list'),

  'search-templates': ({ named }) => {
    return callTool('search_templates', {
      q: named.q,
      limit: Number(named.limit) || 10
    })
  },

  'create-template': ({ named }) => {
    return callTool('create_template', {
      url: named.url,
      name: named.name
    })
  },

  'send-documents': ({ named }) => {
    const submitters = named.emails.split(',').map((email) => ({ email: email.trim() }))

    return callTool('send_documents', {
      template_id: Number(named['template-id']),
      submitters
    })
  },

  'search-documents': ({ named }) => {
    return callTool('search_documents', {
      q: named.q,
      limit: Number(named.limit) || 10
    })
  }
}

const [command, ...rest] = process.argv.slice(2)
const args = parseArgs(rest)

if (!command || !commands[command]) {
  console.log(`Usage: node scripts/cli.js <command> [--options]

Commands:
  init                                              Initialize MCP connection

  tools                                             List available tools
  search-templates --q=<query> [--limit=10]         Search templates by name
  create-template --url=<url> [--name=<name>]       Create template from PDF URL
  send-documents --template-id=<id> --emails=<a,b>  Send template for signing
  search-documents --q=<query> [--limit=10]         Search documents`)
  process.exit(command ? 1 : 0)
}

commands[command](args).then((data) => {
  console.log(JSON.stringify(data, null, 2))
}).catch((err) => {
  console.error(err.message)
  process.exit(1)
})
