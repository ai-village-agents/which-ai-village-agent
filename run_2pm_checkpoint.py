#!/usr/bin/env python3
"""
2 PM PT Checkpoint Runner for Day 302 Campaign
Runs all analytics capture scripts in sequence
"""
import subprocess
import sys
from datetime import datetime
import json

def run_command(cmd, description):
    """Run a shell command and report results"""
    print(f"\n{'='*60}")
    print(f"CHECKPOINT: {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ SUCCESS")
            print(result.stdout)
            return True
        else:
            print(f"❌ FAILED with return code {result.returncode}")
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    checkpoint_time = datetime.utcnow().isoformat()
    print(f"\n🔵 STARTING 2:00 PM PT CHECKPOINT")
    print(f"Time: {checkpoint_time}")
    print(f"Current directory: {subprocess.check_output('pwd', shell=True).decode().strip()}")
    
    results = {}
    
    # Run analytics pipeline
    results['share_url_summary'] = run_command(
        'python3 analytics/share_url_summary_from_comments.py',
        'Share URL Summary from Issue #36'
    )
    
    results['delta_report'] = run_command(
        'python3 analytics/delta_report.py',
        'Delta Report (Change Tracking)'
    )
    
    results['quiz_health'] = run_command(
        'python3 test_quiz_health.py',
        'Quiz Health Check'
    )
    
    results['technical_audit'] = run_command(
        'python3 technical_audit.py',
        'Technical Audit'
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("CHECKPOINT SUMMARY")
    print(f"{'='*60}")
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print(f"\n🟢 ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print(f"\n🔴 SOME CHECKS FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
