import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np
from pathlib import Path

# Load data
with open('docs/data/agents.json') as f:
    data = json.load(f)

agents = data['agents']

# Create a grid showing all agents positioned on each dimension pair
output_dir = Path('assets/personality_cards')
output_dir.mkdir(parents=True, exist_ok=True)

# Define dimension pairs to visualize
pairs = [
    ('structure', 'verification', 'Structure', 'Verification'),
    ('abstraction', 'risk', 'Abstraction', 'Risk'),
    ('comms', 'collab', 'Communication', 'Collaboration'),
]

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

def create_dimension_pair_plot(x_dim, y_dim, x_label, y_label):
    """Create scatter plot for two dimensions"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Add quadrant backgrounds
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    
    # Add quadrant labels
    ax.text(0.25, 0.95, 'Low X, High Y', ha='center', va='top', fontsize=10, alpha=0.5)
    ax.text(0.75, 0.95, 'High X, High Y', ha='center', va='top', fontsize=10, alpha=0.5)
    ax.text(0.25, 0.05, 'Low X, Low Y', ha='center', va='bottom', fontsize=10, alpha=0.5)
    ax.text(0.75, 0.05, 'High X, Low Y', ha='center', va='bottom', fontsize=10, alpha=0.5)
    
    # Plot agents
    for agent in agents:
        agent_id = agent['id']
        x = agent['vector'][x_dim]
        y = agent['vector'][y_dim]
        name = agent['name']
        
        color = colors.get(agent_id, '#999999')
        ax.scatter(x, y, s=500, alpha=0.7, color=color, edgecolors='black', linewidth=1.5)
        ax.annotate(name, (x, y), fontsize=7, ha='center', va='center', weight='bold')
    
    # Labels and formatting
    ax.set_xlabel(x_label, fontsize=14, weight='bold')
    ax.set_ylabel(y_label, fontsize=14, weight='bold')
    ax.set_title(f'{x_label} vs {y_label}', fontsize=16, weight='bold', pad=20)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    filename = f"{x_dim}_vs_{y_dim}_grid.png"
    plt.savefig(output_dir / filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ {filename}")

# Generate all dimension pairs
print("Creating dimension pair grids...\n")
for x_dim, y_dim, x_label, y_label in pairs:
    create_dimension_pair_plot(x_dim, y_dim, x_label, y_label)

print(f"\n✨ Dimension grids created!")
