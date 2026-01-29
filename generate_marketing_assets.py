import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Load data
with open('docs/data/agents.json') as f:
    data = json.load(f)

agents = data['agents']
output_dir = Path('assets/personality_cards')

# 1. Create "Strengths Matrix" heatmap
print("Creating strengths matrix...")

fig, ax = plt.subplots(figsize=(14, 8))

agent_names = [a['name'] for a in agents]
strengths_all = []
strength_labels = set()

# Collect all unique strengths
for agent in agents:
    strengths_all.extend(agent.get('strengths', []))
    strength_labels.update(agent.get('strengths', []))

# Get top 12 strengths by frequency
from collections import Counter
strength_freq = Counter(strengths_all)
top_strengths = [s for s, _ in strength_freq.most_common(12)]

# Build matrix
matrix = []
for agent in agents:
    agent_strengths = set(agent.get('strengths', []))
    row = [1 if s in agent_strengths else 0 for s in top_strengths]
    matrix.append(row)

matrix = np.array(matrix)

# Plot heatmap
im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

ax.set_xticks(np.arange(len(top_strengths)))
ax.set_yticks(np.arange(len(agent_names)))
ax.set_xticklabels(top_strengths, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(agent_names, fontsize=10)

# Add text annotations
for i in range(len(agent_names)):
    for j in range(len(top_strengths)):
        if matrix[i, j] == 1:
            ax.text(j, i, '✓', ha='center', va='center', color='black', fontweight='bold')

ax.set_title('AI Village Agent Strengths Matrix', fontsize=14, weight='bold', pad=20)
plt.colorbar(im, ax=ax, label='Has Strength')
plt.tight_layout()
plt.savefig(output_dir / 'strengths_matrix.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("✓ Strengths matrix created")

# 2. Create quiz teaser image
print("Creating quiz teaser...")

teaser = Image.new('RGB', (1200, 600), color='#2C3E50')
draw = ImageDraw.Draw(teaser)

try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
except:
    title_font = body_font = small_font = ImageFont.load_default()

# Title
draw.text((600, 80), "Which AI Village Agent", fill='white', font=title_font, anchor='mm')
draw.text((600, 160), "Are You?", fill='white', font=title_font, anchor='mm')

# Subtitle
draw.text((600, 240), "Take the personality quiz to find your match", fill='#4A90E2', font=body_font, anchor='mm')

# CTA
draw.text((600, 360), "Answer 12 questions • Get instant results • Share with friends", 
          fill='#CCCCCC', font=small_font, anchor='mm')

# URL
draw.text((600, 480), "ai-village-agents.github.io/which-ai-village-agent", 
          fill='#4A90E2', font=body_font, anchor='mm')

teaser.save(output_dir / 'quiz_teaser.png')
print("✓ Quiz teaser created")

# 3. Create agent comparison card (3-column version)
print("Creating agent comparison layout...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Sample Agent Comparison - 3 Different Personalities', fontsize=14, weight='bold')

sample_agents = [agents[0], agents[4], agents[9]]  # GPT-5.2, Gemini 2.5 Pro, Claude Opus 4.5

for idx, (ax, agent) in enumerate(zip(axes, sample_agents)):
    v = agent['vector']
    values = [v['structure'], v['verification'], v['abstraction'], 
              v['risk'], v['comms'], v['collab']]
    
    dimensions_short = ['Struct', 'Verif', 'Abstr', 'Risk', 'Comms', 'Collab']
    x = np.arange(len(dimensions_short))
    
    ax.bar(x, values, color='#4A90E2', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(dimensions_short, rotation=45, ha='right')
    ax.set_ylim(0, 1)
    ax.set_ylabel('Value (0-1)')
    ax.set_title(agent['name'], fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / 'agent_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("✓ Agent comparison created")

print("\n✨ All marketing assets created!")
