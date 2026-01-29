import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Load agents data
with open('docs/data/agents.json') as f:
    agents_data = json.load(f)

# Dimension names
dimensions = ['Structure', 'Verification', 'Abstraction', 'Risk', 'Comms', 'Collab']

# Create output directory
output_dir = Path('assets/personality_cards')
output_dir.mkdir(parents=True, exist_ok=True)

def create_radar_chart(agent_data, filename):
    """Create a radar chart PNG for an agent"""
    vector = agent_data['vector']
    values = [
        vector['structure'],
        vector['verification'],
        vector['abstraction'],
        vector['risk'],
        vector['comms'],
        vector['collab']
    ]
    
    # Setup radar
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    
    # Plot
    ax.plot(angles, values, 'o-', linewidth=2.5, color='#4A90E2', markersize=8)
    ax.fill(angles, values, alpha=0.25, color='#4A90E2')
    
    # Labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=10, weight='bold')
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=150, transparent=True, bbox_inches='tight')
    plt.close()

def create_personality_card(agent_data):
    """Create a personality card"""
    name = agent_data['name']
    agent_id = agent_data['id']
    archetype = agent_data.get('archetype', 'AI Agent')
    tagline = agent_data.get('tagline', '')
    strengths = agent_data.get('strengths', [])
    
    # Create radar
    radar_file = f"{agent_id}_radar.png"
    create_radar_chart(agent_data, radar_file)
    radar_path = output_dir / radar_file
    radar = Image.open(radar_path)
    radar = radar.resize((350, 350), Image.Resampling.LANCZOS)
    
    # Create card
    card = Image.new('RGB', (1000, 1300), color='white')
    draw = ImageDraw.Draw(card)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        archetype_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        archetype_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header
    draw.rectangle([(0, 0), (1000, 120)], fill='#2C3E50')
    draw.text((50, 25), name, fill='white', font=title_font)
    
    # Archetype
    draw.text((50, 140), archetype, fill='#4A90E2', font=archetype_font)
    
    # Tagline
    if tagline:
        draw.text((50, 190), f'"{tagline}"', fill='#666666', font=text_font)
    
    # Paste radar
    card.paste(radar, (325, 240), radar)
    
    # Strengths
    y_pos = 650
    draw.text((50, y_pos), "Key Strengths:", fill='#2C3E50', font=archetype_font)
    y_pos += 50
    
    for strength in strengths[:5]:
        draw.text((80, y_pos), f"• {strength}", fill='#2C3E50', font=small_font)
        y_pos += 40
    
    # Footer
    draw.line([(50, y_pos + 20), (950, y_pos + 20)], fill='#CCCCCC', width=2)
    draw.text((50, y_pos + 35), "Which AI Village Agent Are You? — Day 300", fill='#999999', font=small_font)
    
    card.save(output_dir / f"{agent_id}_card.png")
    print(f"✓ {name}")

# Generate all cards
print("Generating personality cards...\n")
for agent_id, agent_data in agents_data.items():
    try:
        create_personality_card(agent_data)
    except Exception as e:
        print(f"✗ Error with {agent_id}: {e}")

print(f"\n✨ Done! Cards saved to {output_dir}/")
