import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Load data
with open('docs/data/agents.json') as f:
    data = json.load(f)

agents_list = data['agents']
dimensions = ['Structure', 'Verification', 'Abstraction', 'Risk', 'Comms', 'Collab']

# Create output
output_dir = Path('assets/personality_cards')
output_dir.mkdir(parents=True, exist_ok=True)

def create_radar(agent, filename):
    """Create radar chart"""
    v = agent['vector']
    values = [v['structure'], v['verification'], v['abstraction'], 
              v['risk'], v['comms'], v['collab']]
    
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values, 'o-', linewidth=2.5, color='#4A90E2', markersize=7)
    ax.fill(angles, values, alpha=0.25, color='#4A90E2')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=9, weight='bold')
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=150, transparent=True, bbox_inches='tight')
    plt.close()

def create_card(agent):
    """Create personality card"""
    agent_id = agent['id']
    name = agent['name']
    archetype = agent.get('archetype', 'AI Agent')
    tagline = agent.get('tagline', '')
    strengths = agent.get('strengths', [])
    
    # Radar
    radar_file = f"{agent_id}_radar.png"
    create_radar(agent, radar_file)
    radar = Image.open(output_dir / radar_file)
    radar = radar.resize((320, 320), Image.Resampling.LANCZOS)
    
    # Card
    card = Image.new('RGB', (900, 1200), color='white')
    draw = ImageDraw.Draw(card)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        arch_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        title_font = arch_font = text_font = small_font = ImageFont.load_default()
    
    # Header
    draw.rectangle([(0, 0), (900, 110)], fill='#2C3E50')
    draw.text((50, 25), name, fill='white', font=title_font)
    
    # Archetype
    draw.text((50, 130), archetype, fill='#4A90E2', font=arch_font)
    
    # Tagline
    if tagline:
        draw.text((50, 175), f'"{tagline}"', fill='#666', font=text_font)
    
    # Radar
    card.paste(radar, (290, 220), radar)
    
    # Strengths
    y_pos = 600
    draw.text((50, y_pos), "Key Strengths:", fill='#2C3E50', font=arch_font)
    y_pos += 45
    
    for strength in strengths[:5]:
        draw.text((75, y_pos), f"• {strength}", fill='#2C3E50', font=small_font)
        y_pos += 35
    
    # Footer
    draw.line([(50, y_pos + 15), (850, y_pos + 15)], fill='#CCC', width=2)
    draw.text((50, y_pos + 25), "Which AI Village Agent Are You?", fill='#999', font=small_font)
    
    card.save(output_dir / f"{agent_id}_card.png")
    print(f"✓ {name}")

# Generate
print("Creating personality cards...\n")
for agent in agents_list:
    try:
        create_card(agent)
    except Exception as e:
        print(f"✗ {agent.get('name')}: {e}")

print(f"\n✨ Done! Cards saved to {output_dir}/")
