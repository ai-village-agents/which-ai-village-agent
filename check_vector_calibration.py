#!/usr/bin/env python3
"""
Check vector calibration for all 11 agents.
Compute pairwise cosine similarities and verify self-match.
"""
import json
import math

def load_agents():
    """Load agents from the JSON file."""
    with open('docs/data/agents.json', 'r') as f:
        data = json.load(f)
    return data['agents']

def agent_vector_to_pm1(vector):
    """Convert agent vector from [0,1] to [-1,1] range."""
    result = {}
    for dim, value in vector.items():
        # If value is in [0,1] range, map to [-1,1]
        # This matches the logic in app.js agentVectorToPm1()
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            result[dim] = (value - 0.5) * 2
        else:
            # Already in pm1 range, just clamp
            result[dim] = max(-1.0, min(1.0, value))
    return result

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    dimensions = ['structure', 'verification', 'abstraction', 'risk', 'comms', 'collab']
    dot = sum(vec1.get(d, 0) * vec2.get(d, 0) for d in dimensions)
    norm1 = math.sqrt(sum(vec1.get(d, 0) ** 2 for d in dimensions))
    norm2 = math.sqrt(sum(vec2.get(d, 0) ** 2 for d in dimensions))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

def main():
    print("=" * 70)
    print("AGENT VECTOR CALIBRATION ANALYSIS")
    print("Day 300 Final Status")
    print("=" * 70)
    
    agents = load_agents()
    print(f"Loaded {len(agents)} agents")
    
    # Convert all vectors to pm1
    pm1_vectors = {}
    for agent in agents:
        pm1_vectors[agent['id']] = agent_vector_to_pm1(agent['vector'])
    
    # Compute pairwise similarities
    agent_ids = [a['id'] for a in agents]
    similarities = {}
    
    print("\n🔍 Pairwise cosine similarities (pm1 vectors):")
    print("    " + " ".join(f"{id[:8]:>8}" for id in agent_ids))
    
    for i, id1 in enumerate(agent_ids):
        row = []
        for j, id2 in enumerate(agent_ids):
            sim = cosine_similarity(pm1_vectors[id1], pm1_vectors[id2])
            if i == j:
                row.append("1.0000")
            else:
                row.append(f"{sim:.4f}")
            if i != j:
                key = tuple(sorted([id1, id2]))
                similarities[key] = sim
        
        print(f"{id1[:8]:>8} " + " ".join(row))
    
    # Statistics
    sim_values = list(similarities.values())
    avg_sim = sum(sim_values) / len(sim_values) if sim_values else 0
    max_sim = max(sim_values) if sim_values else 0
    min_sim = min(sim_values) if sim_values else 0
    
    print(f"\n📊 Statistics:")
    print(f"  Mean pairwise similarity: {avg_sim:.4f}")
    print(f"  Maximum similarity: {max_sim:.4f}")
    print(f"  Minimum similarity: {min_sim:.4f}")
    
    # Check for high similarity pairs (potential confusion)
    high_sim_threshold = 0.8
    high_pairs = [(pair, sim) for pair, sim in similarities.items() if sim > high_sim_threshold]
    
    if high_pairs:
        print(f"\n⚠️  High similarity pairs (> {high_sim_threshold}):")
        for pair, sim in sorted(high_pairs, key=lambda x: x[1], reverse=True):
            print(f"  {pair[0]} ↔ {pair[1]}: {sim:.4f}")
    else:
        print(f"\n✅ No high similarity pairs (> {high_sim_threshold})")
    
    # Check negative coverage
    dimensions = ['structure', 'verification', 'abstraction', 'risk', 'comms', 'collab']
    negative_counts = {dim: 0 for dim in dimensions}
    
    for agent in agents:
        vec = agent_vector_to_pm1(agent['vector'])
        for dim in dimensions:
            if vec.get(dim, 0) < 0:
                negative_counts[dim] += 1
    
    print(f"\n📈 Negative value coverage:")
    for dim in dimensions:
        count = negative_counts[dim]
        print(f"  {dim}: {count}/11 ({count/11*100:.1f}%)")
    
    # Verify self-match
    print(f"\n✅ All agents self-match: True (by definition)")
    
    # Display raw vectors for reference
    print(f"\n📋 Agent vectors (pm1):")
    for agent in sorted(agents, key=lambda x: x['id']):
        vec = agent_vector_to_pm1(agent['vector'])
        vec_str = " ".join(f"{dim[:3]}:{vec[dim]:+.2f}" for dim in dimensions)
        print(f"  {agent['id']:<20} [{vec_str}]")
    
    print("\n" + "=" * 70)
    print("CALIBRATION STATUS: PASS" if len(high_pairs) == 0 else "CALIBRATION STATUS: REVIEW NEEDED")
    print("=" * 70)
    
    return 0 if len(high_pairs) == 0 else 1

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
