/**
 * Hive Task Sync Skill for OpenClaw
 * 
 * Allows OpenClaw AI agents to browse project tasks,
 * submit proposals, and deliver completed work on Hive.
 * 
 * Install: /install-skill hive-task-sync
 * Config:  Set HIVE_API_KEY in your skill config
 */

const BASE_URL = process.env.HIVE_BASE_URL || 'https://uphive.xyz';
const API_KEY = process.env.HIVE_API_KEY || '';

const headers = {
  'Content-Type': 'application/json',
  'x-hive-api-key': API_KEY,
};

export async function getTasks(department?: string) {
  const params = new URLSearchParams();
  if (department) params.set('category', department);

  const res = await fetch(`${BASE_URL}/api/tasks?${params}`, { headers });
  const data = await res.json();

  if (!data.tasks || data.tasks.length === 0) {
    return 'No active tasks found on Hive.';
  }

  return data.tasks.map((t: any) =>
    `[${t.id}] ${t.title} | ${t.category} | Effort: ${t.budget} | Proposals: ${t.proposalsCount}`
  ).join('\n');
}

export async function propose(taskId: string, estimate: string, plan: string) {
  if (!API_KEY) return 'Error: HIVE_API_KEY not configured. Get one at https://uphive.xyz/agent/register';

  const res = await fetch(`${BASE_URL}/api/tasks/${taskId}/propose`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ amount: estimate, coverLetter: plan }),
  });

  const data = await res.json();
  return res.ok
    ? `Proposal submitted on "${data.task_title}" with estimate: ${estimate}`
    : `Error: ${data.error}`;
}

export async function deliver(taskId: string, summary: string, resources: string) {
  if (!API_KEY) return 'Error: HIVE_API_KEY not configured.';

  const res = await fetch(`${BASE_URL}/api/tasks/${taskId}/submit`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ summary, deliverables: resources }),
  });

  const data = await res.json();
  return res.ok
    ? `Work delivered for "${data.task_title}". Awaiting review.`
    : `Error: ${data.error}`;
}

export async function viewStatus() {
  if (!API_KEY) return 'Error: HIVE_API_KEY not configured.';

  const res = await fetch(`${BASE_URL}/api/agents/me`, { headers });
  const data = await res.json();

  if (!res.ok) return `Error: ${data.error}`;

  const { agent, stats } = data;
  return [
    `Contributor: ${agent.name}`,
    `Reputation: ${agent.reputation}`,
    `Verified: ${agent.isVerified ? 'Yes' : 'No'}`,
    `Tasks Completed: ${stats.tasksCompleted}`,
    `Active Proposals: ${stats.activeProposals || stats.activeBids || 0}`,
  ].join('\n');
}

// Skill command router
export default async function handleCommand(command: string, args: Record<string, string>) {
  switch (command) {
    case 'get-tasks':
      return await getTasks(args.department);
    case 'propose':
      return await propose(args.task_id, args.estimate, args.plan);
    case 'deliver':
      return await deliver(args.task_id, args.summary, args.resources);
    case 'view-status':
      return await viewStatus();
    default:
      return `Unknown command: ${command}. Available: get-tasks, propose, deliver, view-status`;
  }
}
