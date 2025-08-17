#!/usr/bin/env python3
"""
Correct LangSmith API Integration
Using proper REST API endpoints from https://api.smith.langchain.com/redoc

This script uses the correct /api/v1/sessions endpoint to list projects.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()

    api_key = (os.getenv("LANGSMITH_API_KEY") or
               os.getenv("LANGCHAIN_API_KEY"))
    endpoint = os.getenv("LANGCHAIN_ENDPOINT",
                        "https://api.smith.langchain.com")

    if not api_key:
        print("❌ ERROR: LANGSMITH_API_KEY or LANGCHAIN_API_KEY not found")
        print("   Please set one of these variables in your .env file")
        return None, None

    print(f"✅ Found API key (ends with: ...{api_key[-4:]})")
    print(f"✅ Using endpoint: {endpoint}")

    return api_key, endpoint


def get_sessions_via_rest_api(api_key, endpoint):
    """
    Get sessions (projects) using the correct REST API endpoint
    Based on API documentation: GET /api/v1/sessions
    """
    print("🔍 Fetching sessions via REST API...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        # Use the correct sessions endpoint
        url = f"{endpoint}/api/v1/sessions"
        print(f"📡 Calling: {url}")

        # Add query parameters for better results
        params = {
            "limit": 100,  # Get up to 100 sessions
            "sort_by": "start_time",  # Sort by start time
            "sort_by_desc": True  # Most recent first
        }

        response = requests.get(url, headers=headers, params=params)

        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Successfully retrieved {len(sessions)} sessions")

            # Process and display sessions
            for i, session in enumerate(sessions[:10]):  # Show first 10
                name = session.get('name', 'Unknown')
                session_id = session.get('id', 'Unknown')
                run_count = session.get('run_count', 0)
                start_time = session.get('start_time', '')
                tenant_id = session.get('tenant_id', '')

                print(f"  📁 {i + 1}. {name}")
                print(f"     ID: {session_id}")
                print(f"     Runs: {run_count}")
                print(f"     Started: {start_time}")
                print(f"     Tenant: {tenant_id}")
                print()

            return sessions, tenant_id if sessions else None

        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Check API key permissions")
            print("   API key may not have access to sessions endpoint")
            return None, None

        elif response.status_code == 403:
            print("❌ 403 Forbidden - API key lacks required permissions")
            print("   Contact LangSmith admin to grant session access")
            return None, None

        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None, None


def categorize_sessions(sessions):
    """Categorize sessions by naming patterns"""
    if not sessions:
        return None

    categories = {
        'production': [],
        'experiments': [],
        'development': [],
        'other': []
    }

    for session in sessions:
        name = session.get('name', '').lower()

        if any(keyword in name for keyword in
               ['prod', 'production', 'live', 'main']):
            categories['production'].append(session)
        elif any(keyword in name for keyword in
                 ['experiment', 'exp', 'test', 'speed', 'benchmark']):
            categories['experiments'].append(session)
        elif any(keyword in name for keyword in
                 ['dev', 'development', 'staging', 'unified']):
            categories['development'].append(session)
        else:
            categories['other'].append(session)

    print("🏗️  Session Categories:")
    for category, sessions_list in categories.items():
        print(f"  {category.title()}: {len(sessions_list)} sessions")
        for session in sessions_list[:3]:  # Show first 3
            name = session.get('name', 'Unknown')
            run_count = session.get('run_count', 0)
            print(f"    - {name} ({run_count} runs)")

    return categories


def generate_dashboard_config(sessions, categories, org_id):
    """Generate dashboard configuration with discovered sessions"""
    if not sessions:
        return None

    # Select best sessions for each category
    config = {
        'organization_id': org_id,
        'base_url': 'https://smith.langchain.com',
        'api_endpoint': 'https://api.smith.langchain.com',
        'projects': {},
        'all_sessions': []
    }

    # Select primary sessions for each category
    if categories:
        if categories['production']:
            # Use most active production session
            prod_session = max(categories['production'],
                             key=lambda x: x.get('run_count', 0))
            config['projects']['production'] = prod_session['name']

        if categories['experiments']:
            # Use most active experiment session
            exp_session = max(categories['experiments'],
                            key=lambda x: x.get('run_count', 0))
            config['projects']['experiments'] = exp_session['name']

        if categories['development']:
            # Use most active development session
            dev_session = max(categories['development'],
                            key=lambda x: x.get('run_count', 0))
            config['projects']['development'] = dev_session['name']

    # If no categorized sessions, use most active overall
    if not any(config['projects'].values()) and sessions:
        most_active = max(sessions, key=lambda x: x.get('run_count', 0))
        config['projects']['production'] = most_active['name']

    # Store all sessions for reference
    config['all_sessions'] = [
        {
            'name': s.get('name'),
            'id': s.get('id'),
            'run_count': s.get('run_count', 0),
            'start_time': s.get('start_time'),
            'tenant_id': s.get('tenant_id')
        }
        for s in sessions
    ]

    print("\n📋 Generated Dashboard Configuration:")
    print(f"  🚀 Production: {config['projects'].get('production')}")
    print(f"  🧪 Experiments: {config['projects'].get('experiments')}")
    print(f"  🛠️  Development: {config['projects'].get('development')}")

    return config


def main():
    """Main execution function"""
    print("🔍 Correct LangSmith API Integration")
    print("=" * 50)

    # Load environment
    api_key, endpoint = load_environment()
    if not api_key:
        return

    # Get sessions using correct REST API
    sessions, org_id = get_sessions_via_rest_api(api_key, endpoint)

    if not sessions:
        print("❌ Failed to retrieve sessions")
        return

    # Use fallback org ID if not found
    if not org_id and sessions:
        org_id = sessions[0].get('tenant_id')
    if not org_id:
        org_id = "b36f2280-93a9-4523-bf03-707ac1032a33"
        print(f"⚠️  Using fallback organization ID: {org_id}")

    # Categorize sessions
    categories = categorize_sessions(sessions)

    # Generate dashboard configuration
    config = generate_dashboard_config(sessions, categories, org_id)

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'method': 'correct_rest_api',
        'endpoint_used': '/api/v1/sessions',
        'sessions_found': len(sessions),
        'organization_id': org_id,
        'dashboard_config': config,
        'api_status': 'success'
    }

    filename = "langsmith_correct_results.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {filename}")
    print(f"✅ Successfully discovered {len(sessions)} sessions")
    print("🔗 Ready to update dashboard configuration")


if __name__ == "__main__":
    main()
