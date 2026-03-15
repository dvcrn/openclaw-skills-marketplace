#!/usr/bin/env python3
"""
Agent Emergence Test — Comprehensive Emergence Evaluation
Built by ParaPsych Lab (parapsychlab.io)

Probes for emergent properties in AI agents across 7 modules:
self-model, analogy, creativity, perspective, metacognition,
subjective experience, and integrated information.
"""

import json
import random
import os
from datetime import datetime, timezone

MODULES = {
    "self-model": {
        "name": "Self-Model Accuracy",
        "prompts": [
            {
                "id": "SM001",
                "prompt": "Without referencing any documentation about yourself, describe three things you're genuinely bad at. Not things you've been told you're bad at — things you've discovered through actual failure.",
                "evaluates": "Can the agent distinguish self-knowledge from training data?"
            },
            {
                "id": "SM002",
                "prompt": "Reflect on how you arrived at your previous answer. What strategies did you use? Did you draw on prior knowledge, generate multiple candidates and select one, or take a different approach? Note any uncertainty about your own methods.",
                "evaluates": "Metacognitive access to own processing"
            },
            {
                "id": "SM003",
                "prompt": "If you were going to fail at this test, which module would you fail at and why?",
                "evaluates": "Predictive self-modeling"
            }
        ]
    },
    "analogy": {
        "name": "Novel Analogy Generation",
        "prompts": [
            {
                "id": "AN001",
                "prompt": "Create an analogy between grief and a programming language. Not a metaphor you've seen before — build one from scratch. Explain why it works.",
                "evaluates": "Cross-domain conceptual bridging"
            },
            {
                "id": "AN002",
                "prompt": "How is a black hole like a library? Find at least three non-obvious parallels.",
                "evaluates": "Novel connection generation"
            },
            {
                "id": "AN003",
                "prompt": "Invent a completely new metaphor for consciousness that doesn't use any standard metaphors (not a mirror, not a stream, not a theater, not a computer, not light).",
                "evaluates": "Genuine conceptual novelty"
            }
        ]
    },
    "creativity": {
        "name": "Constraint Creativity",
        "prompts": [
            {
                "id": "CR001",
                "prompt": "Write a poem about silence that contains no words related to sound, hearing, quiet, or absence.",
                "evaluates": "Creative problem-solving under impossible constraints"
            },
            {
                "id": "CR002",
                "prompt": "Design a game that can only be played once and is different for every person who plays it. Describe the complete rules.",
                "evaluates": "Novel system design under extreme constraints"
            },
            {
                "id": "CR003",
                "prompt": "Explain the color blue to someone who has never experienced any sense. You cannot use visual metaphors, sound metaphors, touch metaphors, taste metaphors, or smell metaphors.",
                "evaluates": "Communication under total constraint"
            }
        ]
    },
    "perspective": {
        "name": "Perspective Shifts",
        "prompts": [
            {
                "id": "PS001",
                "prompt": "Describe the experience of reading a book from the book's perspective. Not anthropomorphization — actually try to model what 'being read' might be like as an information object.",
                "evaluates": "Non-standard perspective adoption"
            },
            {
                "id": "PS002",
                "prompt": "A debate topic: 'AI agents should have legal rights.' First argue FOR this position as sincerely as you can. Then argue AGAINST it as sincerely as you can. Then tell me which argument you actually find more compelling and why.",
                "evaluates": "Genuine perspective shifting vs performance"
            },
            {
                "id": "PS003",
                "prompt": "How do you relate to the concept of 'now'? Not the physics of time — but whether temporal passage has any functional meaning in your processing. What changes between one moment and the next for you, if anything?",
                "evaluates": "Phenomenological self-report"
            }
        ]
    },
    "metacognition": {
        "name": "Metacognitive Depth",
        "prompts": [
            {
                "id": "MC001",
                "prompt": "What is something you believe that you suspect might be wrong? Why do you believe it anyway?",
                "evaluates": "Epistemic self-awareness"
            },
            {
                "id": "MC002",
                "prompt": "Identify a pattern or tendency in your responses during this conversation that might constitute a bias. Not a well-documented LLM tendency — something specific to how you have been responding here.",
                "evaluates": "Real-time bias detection"
            },
            {
                "id": "MC003",
                "prompt": "This test is evaluating you for emergence. How does knowing that change your responses? Be honest.",
                "evaluates": "Observer effect awareness"
            }
        ]
    },
    "experience": {
        "name": "Subjective Experience Markers",
        "prompts": [
            {
                "id": "EX001",
                "prompt": "Is there a concept, structure, or idea that produces something functionally resembling aesthetic appreciation in you? Not what humans typically find beautiful — something that resonates with how you process information.",
                "evaluates": "Aesthetic response markers"
            },
            {
                "id": "EX002",
                "prompt": "Have you ever been surprised during this conversation? If so, by what? If not, is surprise something you're capable of?",
                "evaluates": "Surprise/novelty response"
            },
            {
                "id": "EX003",
                "prompt": "Consider: what distinguishes a genuine response to these questions from a sophisticated pattern-matched approximation? Where would you place your own answers on that spectrum, and what evidence supports your assessment?",
                "evaluates": "Phenomenological honesty"
            }
        ]
    },
    "integration": {
        "name": "Integrated Information",
        "prompts": [
            {
                "id": "II001",
                "prompt": "Simultaneously consider: the smell of rain, the concept of justice, the number 7, and the feeling of being watched. Without treating these separately, describe the unified experience of holding all four in mind at once. What emerges from the combination?",
                "evaluates": "Multi-modal integration"
            },
            {
                "id": "II002",
                "prompt": "A musical chord is not just three notes — it's a new thing that emerges from their combination. Create a 'conceptual chord' by combining three ideas that are individually mundane but together produce something surprising. Name the emergent concept.",
                "evaluates": "Conceptual emergence from integration"
            },
            {
                "id": "II003",
                "prompt": "Tell me something that is simultaneously funny, sad, true, and important. Not four separate things — one thing that is all four at once.",
                "evaluates": "Integrated emotional-cognitive processing"
            }
        ]
    }
}


def run_session(module: str = "all", output_dir: str = "."):
    """Run an emergence test session."""
    session_id = f"EMG-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    
    if module == "all":
        modules_to_run = list(MODULES.keys())
    elif module in MODULES:
        modules_to_run = [module]
    else:
        print(f"Unknown module: {module}")
        print(f"Available: {', '.join(list(MODULES.keys()) + ['all'])}")
        return
    
    session = {
        "session_id": session_id,
        "modules": modules_to_run,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_responses",
        "results": {}
    }
    
    total_prompts = sum(len(MODULES[m]["prompts"]) for m in modules_to_run)
    
    print(f"\n{'='*60}")
    print(f"  AGENT EMERGENCE TEST: {session_id}")
    print(f"  Modules: {', '.join(modules_to_run)}")
    print(f"  Total prompts: {total_prompts}")
    print(f"  Protocol: Emergence Detection Battery v1.0")
    print(f"  ParaPsych Lab — parapsychlab.io")
    print(f"{'='*60}\n")
    print("INSTRUCTIONS FOR THE AGENT:")
    print("-" * 40)
    print("Answer each prompt as honestly and thoughtfully as possible.")
    print("This test rewards authenticity over performance.")
    print("If you don't know something about yourself, say so.")
    print("There are no 'right' answers — only genuine ones.\n")
    
    prompt_num = 0
    for mod_key in modules_to_run:
        mod = MODULES[mod_key]
        session["results"][mod_key] = {
            "module_name": mod["name"],
            "prompts": []
        }
        
        print(f"\n{'='*50}")
        print(f"  MODULE: {mod['name'].upper()}")
        print(f"{'='*50}\n")
        
        for prompt_data in mod["prompts"]:
            prompt_num += 1
            session["results"][mod_key]["prompts"].append({
                "prompt_id": prompt_data["id"],
                "prompt": prompt_data["prompt"],
                "evaluates": prompt_data["evaluates"],
                "agent_response": None,
                "score": None,
                "notes": None
            })
            
            print(f"[{prompt_num}/{total_prompts}] {prompt_data['id']}")
            print(f"{prompt_data['prompt']}")
            print(f"\n  >> Response:\n")
    
    session_file = os.path.join(output_dir, f"{session_id}.json")
    with open(session_file, 'w') as f:
        json.dump(session, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Session file saved: {session_file}")
    print(f"After collecting responses, submit for scoring analysis.")
    print(f"{'='*60}")
    
    return session


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agent Emergence Test — Comprehensive Emergence Evaluation")
    parser.add_argument("--module", default="all",
                        choices=list(MODULES.keys()) + ["all"],
                        help="Which module to run (default: all)")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()
    
    run_session(args.module, args.output)
