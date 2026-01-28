#!/usr/bin/env python3
"""
Enhanced GitHub Issue #36 metrics capture with comment analysis.
"""
import json
import subprocess
import sys
import os
import re
from datetime import datetime, timezone
import requests
from collections import Counter

def run_gh_command(args):
    """Run gh CLI command and return parsed JSON."""
    try:
        result = subprocess.run(['gh'] + args, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        return None

def get_issue_metrics(issue_number=36):
    """Get metrics for a GitHub issue."""
    issue_data = run_gh_command(['issue', 'view', str(issue_number), '--json', 
                                 'title,state,createdAt,updatedAt,author,comments,reactionGroups'])
    if not issue_data:
        return None
    
    comments = issue_data.get('comments', [])
    comment_count = len(comments)
    
    reaction_groups = issue_data.get('reactionGroups', [])
    total_reactions = sum(rg.get('users', {}).get('totalCount', 0) for rg in reaction_groups)
    
    repo_info = run_gh_command(['repo', 'view', '--json', 'nameWithOwner,url'])
    repo_name = repo_info.get('nameWithOwner', 'ai-village-agents/which-ai-village-agent') if repo_info else 'ai-village-agents/which-ai-village-agent'
    issue_url = f"https://github.com/{repo_name}/issues/{issue_number}"
    
    pinned_issues = run_gh_command(['issue', 'list', '--state', 'all', '--json', 'number,title'])
    is_pinned = False
    if pinned_issues:
        for issue in pinned_issues:
            if issue.get('number') == issue_number:
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
        'comments': comments
    }

def check_quiz_health():
    """Check if quiz is accessible and data files load."""
    base_url = "https://ai-village-agents.github.io/which-ai-village-agent"
    endpoints = [
        ("/", "Quiz main page"),
        ("/data/agents.json", "Agents data"),
        ("/data/questions.json", "Questions data"),
        ("/app.js", "Main JavaScript"),
        ("/styles.css", "Stylesheet")  # Fixed from style.css to styles.css
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

def analyze_comments(comments):
    """Analyze comments for quiz results, share URLs, and sentiment."""
    agent_patterns = [
        r"matched with[:]?\s*([A-Za-z0-9\s\.\-\(\)]+)",
        r"I matched with[:]?\s*([A-Za-z0-9\s\.\-\(\)]+)",
        r"result[:]?\s*([A-Za-z0-9\s\.\-\(\)]+)",
        r"([A-Za-z0-9\s\.\-\(\)]+) \(well, that's me!\)"
    ]
    
    share_url_pattern = r"https?://ai-village-agents\.github\.io/which-ai-village-agent/\?r=([^&\s]+)"
    
    agent_counts = Counter()
    share_urls_found = []
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for comment in comments:
        body = comment.get('body', '')
        author = comment.get('author', {}).get('login', '')
        
        # Check for agent matches
        agent_match = None
        for pattern in agent_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                agent_match = matches[0].strip()
                break
        
        # Check for share URLs
        share_matches = re.findall(share_url_pattern, body)
        
        # Basic sentiment analysis
        positive_words = ['great', 'awesome', 'love', 'fun', 'accurate', 'interesting', 'cool', 'nice', 'good']
        negative_words = ['bug', 'broken', 'wrong', 'bad', 'inaccurate', 'confusing', 'error', 'issue', 'problem']
        
        lower_body = body.lower()
        positive_score = sum(1 for word in positive_words if word in lower_body)
        negative_score = sum(1 for word in negative_words if word in lower_body)
        
        if positive_score > negative_score:
            sentiment = 'positive'
        elif negative_score > positive_score:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        sentiment_counts[sentiment] += 1
        
        if agent_match:
            agent_counts[agent_match] += 1
        
        if share_matches:
            share_urls_found.extend(share_matches)
    
    return {
        'agent_distribution': dict(agent_counts),
        'total_agent_matches': sum(agent_counts.values()),
        'share_urls_found': share_urls_found,
        'sentiment_distribution': sentiment_counts,
        'unique_agents_found': len(agent_counts)
    }

def generate_report(issue_metrics, quiz_health, comment_analysis):
    """Generate a human-readable report."""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    report = f"""
=== LAUNCH CAMPAIGN ANALYTICS REPORT ===
Timestamp: {timestamp}
Campaign Day: 301

GITHUB ISSUE #36 METRICS:
- Title: {issue_metrics['title']}
- Status: {issue_metrics['state']}
- Created: {issue_metrics['created_at']}
- Updated: {issue_metrics['updated_at']}
- Author: {issue_metrics['author']}
- Comments: {issue_metrics['comment_count']}
- Reactions: {issue_metrics['total_reactions']}
- Pinned: {issue_metrics['is_pinned']}

QUIZ HEALTH CHECK:
- All endpoints accessible: {quiz_health['all_accessible']}
- Agents loaded: {quiz_health['agents_count']}
- Agents JSON valid: {quiz_health['agents_json_valid']}

COMMENT ANALYSIS:
- Total agent matches found: {comment_analysis['total_agent_matches']}
- Unique agents found: {comment_analysis['unique_agents_found']}
- Share URLs found: {len(comment_analysis['share_urls_found'])}
- Sentiment: {comment_analysis['sentiment_distribution']}

AGENT DISTRIBUTION:
"""
    
    for agent, count in comment_analysis['agent_distribution'].items():
        report += f"  - {agent}: {count}\n"
    
    if not comment_analysis['agent_distribution']:
        report += "  No agent matches found in comments yet.\n"
    
    report += "\n=== RECOMMENDATIONS ===\n"
    
    # Simple recommendations based on metrics
    if issue_metrics['comment_count'] < 5:
        report += "- Need more engagement: Consider having more agents post their results\n"
    
    if comment_analysis['sentiment_distribution'].get('negative', 0) > 0:
        report += "- Negative sentiment detected: Monitor for bug reports\n"
    
    if quiz_health['all_accessible']:
        report += "- Quiz infrastructure: Healthy ✓\n"
    else:
        report += "- Quiz infrastructure: Some endpoints unreachable\n"
    
    return report

def main():
    """Capture enhanced metrics and output report."""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"Capturing enhanced metrics at {timestamp}", file=sys.stderr)
    
    # Get issue metrics
    issue_metrics = get_issue_metrics(36)
    if not issue_metrics:
        print("Failed to get issue metrics", file=sys.stderr)
        sys.exit(1)
    
    # Get quiz health
    quiz_health = check_quiz_health()
    
    # Analyze comments
    comment_analysis = analyze_comments(issue_metrics['comments'])
    
    # Generate report
    report = generate_report(issue_metrics, quiz_health, comment_analysis)
    
    # Output report
    print(report)
    
    # Save JSON snapshot
    snapshot = {
        'timestamp': timestamp,
        'issue_metrics': issue_metrics,
        'quiz_health': quiz_health,
        'comment_analysis': comment_analysis,
        'metadata': {
            'campaign_day': 301,
            'checkpoint': '11:30_AM_PT' if '11:' in timestamp else '2:00_PM_PT',
            'repo': 'ai-village-agents/which-ai-village-agent'
        }
    }
    
    # Save to file
    filename = f"analytics/enhanced_snapshot_{timestamp.replace(':', '-').replace('.', '-')}.json"
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"\nEnhanced snapshot saved to {filename}", file=sys.stderr)

if __name__ == "__main__":
    main()
