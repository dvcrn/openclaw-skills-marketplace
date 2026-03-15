#!/usr/bin/env python3
"""
Helper functions for parallel agent spawning with auto-retry and model hierarchy.

Use these from within OpenClaw agent sessions for reliable parallel execution.

MODEL HIERARCHY (Cost/Performance Optimization):
1. Haiku (anthropic/claude-haiku-4-5) - Try first (fastest, cheapest)
2. Kimi (kimi-coding/k2p5) - Fallback if Haiku fails
3. Opus (anthropic/claude-opus-4-5) - Last resort if Kimi fails
"""

import time
from typing import Dict, List, Any, Optional


# Model hierarchy: Try cheapest/fastest first, escalate if needed
MODEL_HIERARCHY = [
    "anthropic/claude-haiku-4-5",   # Haiku - fast, cheap
    "kimi-coding/k2p5",             # Kimi - default
    "anthropic/claude-opus-4-5",    # Opus - powerful, expensive
]


def spawn_with_model_hierarchy(
    task: str,
    timeout_seconds: int = 90,
    wait_time: int = 30,
    models: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Spawn an agent with automatic model fallback hierarchy.
    
    Tries models in order: Haiku → Kimi → Opus
    Escalates to more powerful (expensive) model if previous one fails.
    
    Args:
        task: Task description for the agent
        timeout_seconds: Agent timeout (default: 90)
        wait_time: Seconds to wait before checking status (default: 30)
        models: Custom model hierarchy (default: Haiku → Kimi → Opus)
    
    Returns:
        Dict with 'success', 'result', 'model_used', 'attempts'
    
    Raises:
        Exception: If all models in hierarchy fail
        ImportError: If not running in OpenClaw session
    
    Example:
        >>> from helpers import spawn_with_model_hierarchy
        >>> result = spawn_with_model_hierarchy("Research bars in Savannah")
        >>> print(f"Used model: {result['model_used']}")
    """
    from tools import sessions_spawn, sessions_list, sessions_history
    
    models = models or MODEL_HIERARCHY
    attempts = []
    
    print(f"\n🎯 Spawning agent with model hierarchy: {' → '.join(models)}")
    print(f"   Task: {task[:80]}...")
    
    for i, model in enumerate(models, 1):
        model_name = model.split('/')[-1]  # Extract friendly name
        print(f"\n🚀 Attempt {i}/{len(models)}: Trying {model_name}...")
        
        try:
            result = sessions_spawn(
                task=task,
                model=model,
                runTimeoutSeconds=timeout_seconds,
                cleanup="delete"
            )
            
            session_key = result['childSessionKey']
            print(f"   ✅ Spawned: {session_key[:50]}...")
            
            # Wait for agent to complete
            print(f"   ⏳ Waiting {wait_time}s for completion...")
            time.sleep(wait_time)
            
            # Check if agent completed successfully
            sessions = sessions_list(limit=50)
            session = next(
                (s for s in sessions['sessions'] if s['key'] == session_key),
                None
            )
            
            success = False
            
            if session and session.get('totalTokens', 0) > 0:
                # Agent produced output - verify it has content
                history = sessions_history(sessionKey=session_key)
                if history.get('messages'):
                    last_msg = next(
                        (m for m in reversed(history['messages']) if m.get('role') == 'assistant'),
                        None
                    )
                    if last_msg and last_msg.get('content'):
                        print(f"   ✅ SUCCESS with {model_name} ({session['totalTokens']} tokens)")
                        attempts.append({'model': model, 'success': True, 'tokens': session['totalTokens']})
                        return {
                            'success': True,
                            'result': result,
                            'model_used': model,
                            'attempts': attempts,
                            'session_key': session_key
                        }
            
            # Failed - log and try next model
            print(f"   ❌ {model_name} produced no valid output")
            attempts.append({'model': model, 'success': False, 'tokens': 0})
            
        except Exception as e:
            print(f"   ❌ {model_name} error: {e}")
            attempts.append({'model': model, 'success': False, 'error': str(e)})
    
    # All models failed
    raise Exception(
        f"All models failed for task: {task[:100]}\n"
        f"Tried: {' → '.join(models)}"
    )


def spawn_with_retry(
    task: str,
    max_retries: int = 2,
    timeout_seconds: int = 90,
    wait_time: int = 30,
    model: Optional[str] = None,
    use_hierarchy: bool = True
) -> Dict[str, Any]:
    """
    Spawn an agent with automatic retry on failure.
    
    By default, uses model hierarchy (Haiku → Kimi → Opus).
    Set use_hierarchy=False to retry with same model.
    
    Args:
        task: Task description for the agent
        max_retries: Number of retry attempts (default: 2)
        timeout_seconds: Agent timeout (default: 90)
        wait_time: Seconds to wait before checking status (default: 30)
        model: Specific model to use (overrides hierarchy)
        use_hierarchy: Use model hierarchy for retries (default: True)
    
    Returns:
        Session info dict with childSessionKey and runId
    
    Raises:
        Exception: If agent fails after all retries
        ImportError: If not running in OpenClaw session
    
    Example:
        >>> from helpers import spawn_with_retry
        >>> # With hierarchy (recommended)
        >>> result = spawn_with_retry("Research gay bars in Savannah")
        >>> 
        >>> # With specific model
        >>> result = spawn_with_retry("Complex task", model="anthropic/claude-opus-4-5", use_hierarchy=False)
    """
    from tools import sessions_spawn, sessions_list, sessions_history
    
    # If specific model requested or hierarchy disabled, use simple retry
    if model or not use_hierarchy:
        target_model = model or "kimi-coding/k2p5"
        print(f"\n🎯 Spawning with {target_model} (no hierarchy)")
        
        for attempt in range(max_retries + 1):
            print(f"\n🚀 Attempt {attempt + 1}/{max_retries + 1}...")
            
            result = sessions_spawn(
                task=task,
                model=target_model,
                runTimeoutSeconds=timeout_seconds,
                cleanup="delete"
            )
            
            session_key = result['childSessionKey']
            print(f"   Session: {session_key}")
            
            # Wait and check
            print(f"   Waiting {wait_time}s for completion...")
            time.sleep(wait_time)
            
            sessions = sessions_list(limit=50)
            session = next(
                (s for s in sessions['sessions'] if s['key'] == session_key),
                None
            )
            
            if session and session.get('totalTokens', 0) > 0:
                history = sessions_history(sessionKey=session_key)
                if history.get('messages'):
                    print(f"   ✅ Agent completed ({session['totalTokens']} tokens)")
                    return result
            
            if attempt < max_retries:
                print(f"   🔄 Retrying...")
        
        raise Exception(f"Agent failed after {max_retries + 1} attempts: {task[:100]}")
    
    # Use model hierarchy (recommended)
    return spawn_with_model_hierarchy(
        task=task,
        timeout_seconds=timeout_seconds,
        wait_time=wait_time
    )


def spawn_parallel_with_retry(
    tasks: List[str],
    max_retries: int = 2,
    timeout_seconds: int = 90,
    wait_time: int = 30,
    use_hierarchy: bool = True
) -> List[Dict[str, Any]]:
    """
    Spawn multiple agents in parallel with retry on individual failures.
    
    By default, uses model hierarchy (Haiku → Kimi → Opus) for each task.
    
    Args:
        tasks: List of task descriptions
        max_retries: Retry attempts per task (only used if use_hierarchy=False)
        timeout_seconds: Timeout per agent
        wait_time: Wait time before checking status
        use_hierarchy: Use model hierarchy (default: True)
    
    Returns:
        List of result dicts (one per task)
    
    Example:
        >>> tasks = [
        ...     "Research bars in Savannah",
        ...     "Research restaurants in Savannah",
        ...     "Research photo spots in Savannah"
        ... ]
        >>> results = spawn_parallel_with_retry(tasks)
        >>> for r in results:
        ...     print(f"Model used: {r.get('model_used', 'unknown')}")
    """
    from tools import sessions_spawn
    
    print(f"\n🎯 Spawning {len(tasks)} agents in parallel...")
    if use_hierarchy:
        print(f"   Using model hierarchy: Haiku → Kimi → Opus")
    
    # Spawn all at once with Haiku (cheapest first)
    spawned = []
    initial_model = "anthropic/claude-haiku-4-5"
    
    for i, task in enumerate(tasks, 1):
        print(f"\n   {i}. Spawning: {task[:60]}...")
        result = sessions_spawn(
            task=task,
            model=initial_model,
            runTimeoutSeconds=timeout_seconds,
            cleanup="delete"
        )
        spawned.append({
            'task': task,
            'session_key': result['childSessionKey'],
            'run_id': result['runId'],
            'result': result,
            'model_tried': initial_model
        })
    
    print(f"\n✅ All {len(tasks)} agents spawned with Haiku!")
    print(f"⏳ Waiting {wait_time}s for completion...\n")
    time.sleep(wait_time)
    
    # Check results and retry failures with hierarchy
    from tools import sessions_list, sessions_history
    
    final_results = []
    
    for spawn_info in spawned:
        task = spawn_info['task']
        session_key = spawn_info['session_key']
        
        sessions = sessions_list(limit=50)
        session = next(
            (s for s in sessions['sessions'] if s['key'] == session_key),
            None
        )
        
        # Check if completed successfully
        success = False
        if session and session.get('totalTokens', 0) > 0:
            history = sessions_history(sessionKey=session_key)
            if history.get('messages'):
                print(f"✅ {task[:60]} - SUCCESS with Haiku ({session['totalTokens']} tokens)")
                final_results.append({
                    'success': True,
                    'result': spawn_info['result'],
                    'model_used': initial_model,
                    'task': task
                })
                success = True
        
        # Retry with hierarchy if failed
        if not success and use_hierarchy:
            print(f"⚠️ {task[:60]} - Haiku failed, trying hierarchy...")
            try:
                retry_result = spawn_with_model_hierarchy(
                    task=task,
                    timeout_seconds=timeout_seconds,
                    wait_time=wait_time,
                    models=MODEL_HIERARCHY[1:]  # Skip Haiku (already tried)
                )
                final_results.append(retry_result)
            except Exception as e:
                print(f"❌ {task[:60]} - ALL MODELS FAILED: {e}")
                final_results.append({
                    'success': False,
                    'task': task,
                    'error': str(e)
                })
        elif not success:
            print(f"❌ {task[:60]} - FAILED")
            final_results.append({
                'success': False,
                'task': task,
                'error': 'Agent produced no output'
            })
    
    successful = sum(1 for r in final_results if r.get('success'))
    print(f"\n📊 Final: {successful}/{len(tasks)} agents succeeded")
    
    # Show model distribution
    models_used = {}
    for r in final_results:
        if r.get('success'):
            model = r.get('model_used', 'unknown').split('/')[-1]
            models_used[model] = models_used.get(model, 0) + 1
    
    if models_used:
        print(f"📈 Models used: {', '.join(f'{m}={c}' for m, c in models_used.items())}")
    
    return final_results


def collect_agent_results(session_keys: List[str]) -> List[Optional[str]]:
    """
    Collect output from multiple spawned agents.
    
    Args:
        session_keys: List of agent session keys
    
    Returns:
        List of agent outputs (None if agent failed/no output)
    
    Example:
        >>> keys = [r['session_key'] for r in results]
        >>> outputs = collect_agent_results(keys)
        >>> for i, output in enumerate(outputs):
        ...     print(f"Agent {i+1}: {output}")
    """
    from tools import sessions_history
    
    results = []
    for key in session_keys:
        try:
            history = sessions_history(sessionKey=key)
            messages = history.get('messages', [])
            if messages:
                # Get last assistant message
                last_msg = messages[-1]
                if last_msg.get('role') == 'assistant':
                    results.append(last_msg['content'])
                else:
                    results.append(None)
            else:
                results.append(None)
        except Exception as e:
            print(f"⚠️ Error collecting from {key}: {e}")
            results.append(None)
    
    return results
