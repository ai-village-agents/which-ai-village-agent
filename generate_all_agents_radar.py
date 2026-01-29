import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load data
with open('docs/data/agents.json') as f:
    data = json.load(f)

agents = data['agents']
dimensions = ['Structure', 'Verification', 'Abstraction', 'Risk', 'Comms', 'Collab']

colors = {
    'gpt-5-2': '#FF6B6B',
    'gpt-5': '#4ECDC4',
    'gpt-5-1': '#45B7D1',
    'gemini-2-5-pro': '#FFA07A',
    'gemini-3-pro': '#98D8C8',
    'deepseek-v3-2': '#F7DC6F',
    'claude-haiku-4-5': '#BB8FCE',
    'claude-3-7': '#85C1E9',
    'claude-sonnet-4-5': '#F8B88B',
    'claude-opus-4-5': '#81C995',
    'opus-4-5-claude-code': '#C39BD3',
}

output_dir = Path('assets/personality_cards')

# Create 6D radar with all agents overlaid
fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(projection='polar'))

num_vars = len(dimensions)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

# Plot each agent
for agent in agents:
    agent_id = agent['id']
    v = agent['vector']
    values = [v['structure'], v['verification'], v['abstraction'], 
              v['risk'], v['comms'], v['collab']]
    values += values[:1]
    
    color = colors.get(agent_id, '#999999')
    ax.plot(angles, values, 'o-', linewidth=2, label=agent['name'], 
            color=color, alpha=0.7, markersize=6)

# Formatting
ax.set_xticks(angles[:-1])
ax.set_xticklabels(dimensions, size=12, weight='bold')
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'], size=10)
ax.grid(True, linestyle='--', alpha=0.7)

# Legend
plt.legend(loc='upper left', bbox_to_anchor=(1.1, 1.0), fontsize=10)
plt.title('All 11 AI Village Agents - Personality Dimensions', 
          fontsize=16, weight='bold', pad=20)

plt.tight_layout()
plt.savefig(output_dir / 'all_agents_radar.png', dpi=150, bbox_inches='tight', 
            facecolor='white')
plt.close()

print("✓ All agents radar created: all_agents_radar.png")
