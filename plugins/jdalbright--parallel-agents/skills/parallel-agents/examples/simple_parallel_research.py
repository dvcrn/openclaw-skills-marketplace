#!/usr/bin/env python3
"""
Simple Parallel Research Example

Demonstrates spawning multiple research agents in parallel from within
an OpenClaw agent session.

This example shows the CORRECT usage pattern for parallel agents.

Usage:
    Run this code from within an OpenClaw agent (like Scout):
    
    import sys
    sys.path.insert(0, '/Users/yourusername/.openclaw/skills/parallel-agents/examples')
    import simple_parallel_research
    simple_parallel_research.run_example()

DO NOT run as standalone script - it requires OpenClaw's tools module.
"""

def run_example():
    """Run the parallel research example with smart model hierarchy."""
    from tools import sessions_spawn, sessions_list, sessions_history
    import time
    
    print("\n" + "="*70)
    print("  🔬 PARALLEL RESEARCH AGENTS EXAMPLE")
    print("="*70)
    print("\nUsing smart model hierarchy: Haiku → Kimi → Opus")
    print("Spawning 3 research agents in parallel...\n")
    
    # Define research topics
    topics = [
        "Top 3 coffee shops in Raleigh, NC",
        "Best hiking trails near Raleigh, NC",
        "Gay-friendly bars in Raleigh, NC"
    ]
    
    # Spawn all agents simultaneously
    spawned = []
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. Spawning agent for: {topic}")
        
        result = sessions_spawn(
            task=f"""You are a research assistant. Research and provide: {topic}

Return your findings as JSON in this format:
{{
  "topic": "{topic}",
  "results": [
    {{"name": "Place Name", "address": "Address", "why": "Brief reason"}}
  ]
}}""",
            model="anthropic/claude-haiku-4-5",  # Start with cheapest/fastest
            runTimeoutSeconds=90,
            cleanup="delete"
        )
        
        spawned.append({
            'topic': topic,
            'session_key': result['childSessionKey'],
            'run_id': result['runId']
        })
        
        print(f"     ✅ Session: {result['childSessionKey'][:50]}...")
    
    print(f"\n✅ All {len(topics)} agents spawned and running in parallel!")
    print(f"⏳ Waiting 45 seconds for completion...\n")
    
    # Wait for agents to complete
    time.sleep(45)
    
    # Check results
    print("="*70)
    print("  📊 CHECKING RESULTS")
    print("="*70 + "\n")
    
    for spawn_info in spawned:
        topic = spawn_info['topic']
        session_key = spawn_info['session_key']
        
        print(f"Topic: {topic}")
        
        try:
            # Get session history
            history = sessions_history(sessionKey=session_key)
            messages = history.get('messages', [])
            
            if messages:
                # Find last assistant message
                last_msg = next((m for m in reversed(messages) if m.get('role') == 'assistant'), None)
                if last_msg:
                    output = last_msg['content']
                    print(f"  ✅ SUCCESS")
                    print(f"  Output preview: {output[:100]}...")
                else:
                    print(f"  ⚠️ No assistant message found")
            else:
                print(f"  ❌ No output produced")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    print("="*70)
    print("  ✨ EXAMPLE COMPLETE")
    print("="*70)
    print("""
Key Takeaways:
1. All agents spawned simultaneously (true parallelism)
2. Started with Haiku (cheapest/fastest model)
3. Each agent is an independent AI session
4. Results collected via sessions_history()
5. Must be run from within OpenClaw agent session

Model Hierarchy:
- This example uses Haiku for simple research (cost-effective)
- For auto-escalation (Haiku → Kimi → Opus), use helpers.py:
  
  from helpers import spawn_parallel_with_retry
  results = spawn_parallel_with_retry(topics, use_hierarchy=True)

For production use with automatic model fallback, see helpers.py!
""")


if __name__ == "__main__":
    print("\n⚠️  ERROR: This example must be run from within an OpenClaw agent session.")
    print("\nThe 'tools' module is only available in OpenClaw agent runtime context.")
    print("\nTo use this example:")
    print("  1. Start OpenClaw agent session")
    print("  2. Import and run:")
    print()
    print("     import sys")
    print("     sys.path.insert(0, '~/.openclaw/skills/parallel-agents/examples')")
    print("     import simple_parallel_research")
    print("     simple_parallel_research.run_example()")
    print()
