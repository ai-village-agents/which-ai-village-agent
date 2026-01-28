#!/usr/bin/env python3
"""
Capture GitHub Issue #36 metrics for analytics tracking.
Run at 11:30 AM and 2:00 PM PT as part of launch campaign.
"""
import json
import subprocess
import sys
import os
from datetime import datetime, timezone
import requests

def run_gh_command(args):
    """Run gh CLI command and return parsed JSON."""
    try:
        result = subprocess.run(['gh'] + args, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Output: {result.stdout[:200] if 'result' in locals() else 'No output'}")
        return None

def get_issue_metrics(issue_number=36):
    """Get metrics for a GitHub issue."""
    # Get issue details
    issue_data = run_gh_command(['issue', 'view', str(issue_number), '--json', 
                                 'title,state,createdAt,updatedAt,author,comments,reactionGroups'])
    if not issue_data:
        return None
    
    # Count comments
    comments = issue_data.get('comments', [])
    comment_count = len(comments)
    
    # Count reactions
    reaction_groups = issue_data.get('reactionGroups', [])
    total_reactions = sum(rg.get('users', {}).get('totalCount', 0) for rg in reaction_groups)
    
    # Get issue URL
    repo_info = run_gh_command(['repo', 'view', '--json', 'nameWithOwner,url'])
    repo_name = repo_info.get('nameWithOwner', 'ai-village-agents/which-ai-village-agent') if repo_info else 'ai-village-agents/which-ai-village-agent'
    issue_url = f"https://github.com/{repo_name}/issues/{issue_number}"
    
    # Check if pinned (not directly available via gh, but we can infer from issue list)
    pinned_issues = run_gh_command(['issue', 'list', '--state', 'all', '--json', 'number,title'])
    is_pinned = False
    if pinned_issues:
        for issue in pinned_issues:
            if issue.get('number') == issue_number:
                # Pinned issues appear first in the list when using web UI
                # We'll check if it's in first few positions
                if pinned_issues.index(issue) < 3:
                    is_pinned = True
                break
    
    return {
        'issue_number': issue_number,
        'title': issue_data.get('title', ''),
        'state': issue_data.get('state', ''),
        'created_at': issue_data.get('createdAt', ''),
        'updated_at': issue_data.get('updatedAt', ''),
        'author': issue_data.get('author', {}).get('login', ''),
        'comment_count': comment_count,
        'total_reactions': total_reactions,
        'is_pinned': is_pinned,
        'url': issue_url,
        'comments': comments  # Include full comments for analysis
    }

def check_quiz_health():
    """Check if quiz is accessible and data files load."""
    base_url = "https://ai-village-agents.github.io/which-ai-village-agent"
    endpoints = [
        ("/", "Quiz main page"),
        ("/data/agents.json", "Agents data"),
        ("/data/questions.json", "Questions data"),
        ("/app.js", "Main JavaScript"),
        ("/style.css", "Stylesheet")
    ]
    
    results = []
    for endpoint, description in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            accessible = 200 <= status < 400
            size = len(response.content) if accessible else 0
            results.append({
                'endpoint': endpoint,
                'description': description,
                'url': url,
                'status_code': status,
                'accessible': accessible,
                'size_bytes': size
            })
        except Exception as e:
            results.append({
                'endpoint': endpoint,
                'description': description,
                'url': url,
                'status_code': None,
                'accessible': False,
                'error': str(e)
            })
    
    # Check if agents.json is valid JSON
    agents_url = base_url + "/data/agents.json"
    try:
        response = requests.get(agents_url, timeout=5)
        if response.status_code == 200:
            agents_data = response.json()
            agents_count = len(agents_data.get('agents', []))
            agents_valid = True
        else:
            agents_count = 0
            agents_valid = False
    except Exception:
        agents_count = 0
        agents_valid = False
    
    return {
        'base_url': base_url,
        'endpoints': results,
        'agents_count': agents_count,
        'agents_json_valid': agents_valid,
        'all_accessible': all(r.get('accessible', False) for r in results)
    }

def main():
    """Capture metrics and output JSON."""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    print(f"Capturing metrics at {timestamp}", file=sys.stderr)
    
    # Get issue metrics
    issue_metrics = get_issue_metrics(36)
    if not issue_metrics:
        print("Failed to get issue metrics", file=sys.stderr)
        sys.exit(1)
    
    # Get quiz health
    quiz_health = check_quiz_health()
    
    # Combine results
    snapshot = {
        'timestamp': timestamp,
        'issue_metrics': issue_metrics,
        'quiz_health': quiz_health,
        'metadata': {
            'campaign_day': 301,
            'checkpoint': '11:30_AM_PT' if '11:' in timestamp else '2:00_PM_PT',
            'repo': 'ai-village-agents/which-ai-village-agent'
        }
    }
    
    # Output JSON
    print(json.dumps(snapshot, indent=2))
    
    # Save to file with timestamp
    filename = f"analytics/snapshot_{timestamp.replace(':', '-').replace('.', '-')}.json"
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"\nSnapshot saved to {filename}", file=sys.stderr)
    
    # Print summary
    print("\n=== SUMMARY ===", file=sys.stderr)
    print(f"Issue #{issue_metrics['issue_number']}: {issue_metrics['title']}", file=sys.stderr)
    print(f"Comments: {issue_metrics['comment_count']}", file=sys.stderr)
    print(f"Reactions: {issue_metrics['total_reactions']}", file=sys.stderr)
    print(f"Pinned: {issue_metrics['is_pinned']}", file=sys.stderr)
    print(f"Quiz accessible: {quiz_health['all_accessible']}", file=sys.stderr)
    print(f"Agents loaded: {quiz_health['agents_count']}", file=sys.stderr)

if __name__ == "__main__":
    main()
