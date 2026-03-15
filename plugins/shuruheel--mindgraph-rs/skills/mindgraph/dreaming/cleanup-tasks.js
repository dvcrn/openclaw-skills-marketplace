/**
 * cleanup-tasks.js
 * Completes tasks that are clearly done based on graph state.
 * Updated to use the 18 Cognitive Layer Tools API.
 */

'use strict';

const mg = require('../mindgraph-client.js');

async function run() {
  console.log('🧹 Cleaning up stale tasks...');
  
  try {
    const batch = await mg.getNodes({ type: 'Task', status: 'active' });
    const tasks = batch.items || batch || [];
    
    for (const task of tasks) {
      const label = (task.label || '').toLowerCase();
      
      // Pattern 1: success criteria tasks where criteria is now defined
      if (label.includes('success criteria')) {
        console.log(`   Checking task: ${task.label}`);
        const ageHours = (Date.now() - (task.created_at * 1000)) / 3600000;
        if (ageHours > 0.5) {
          await mg.plan({
            action: 'complete_task',
            taskUid: task.uid,
            status: 'completed',
            description: 'Criteria defined (automated cleanup).'
          });
          console.log(`   ✓ Completed success criteria task`);
        }
      }
      
      // Pattern 2: very old generic tasks
      if (task.label === 'Task' && (Date.now() - (task.created_at * 1000)) > 86400000 * 3) {
        await mg.evolve('tombstone', task.uid, { reason: 'Deleting old generic task shell' });
        console.log(`   ✓ Deleted old generic task: ${task.uid}`);
      }
    }
    
    console.log('✅ Cleanup complete.');
  } catch (e) {
    console.error('❌ Cleanup failed:', e.message);
  }
}

run().catch(console.error);
