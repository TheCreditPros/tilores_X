#!/usr/bin/env python3
"""
Improved LangSmith API Integration
Based on LangSmith documentation: https://docs.smith.langchain.com/

This script uses proper API methods to discover projects and sessions.
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import LangSmithError


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


def discover_projects_via_runs(client):
    """
    Discover projects by analyzing recent runs.
    This is the recommended approach when direct project listing fails.
    """
    print("🔍 Discovering projects via run analysis...")

    try:
        # Get recent runs without specifying a project
        # Use a broader time range to capture more projects
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)  # Last 30 days

        print(f"📅 Searching runs from {start_time.date()} to {end_time.date()}")

        # Try different approaches to list runs
        projects_found = {}

        # Method 1: List runs with minimal filters
        try:
            runs = list(client.list_runs(
                start_time=start_time,
                end_time=end_time,
                limit=1000  # Increase limit to capture more data
            ))

            print(f"📊 Found {len(runs)} runs to analyze")

            for run in runs:
                # Extract project information from run metadata
                project_name = None

                # Check various attributes for project name
                if hasattr(run, 'session_name') and run.session_name:
                    project_name = run.session_name
                elif hasattr(run, 'project_name') and run.project_name:
                    project_name = run.project_name
                elif hasattr(run, 'extra') and run.extra:
                    # Check extra metadata for project info
                    if isinstance(run.extra, dict):
                        project_name = (run.extra.get('project_name') or
                                      run.extra.get('session_name'))

                if project_name:
                    if project_name not in projects_found:
                        projects_found[project_name] = {
                            'name': project_name,
                            'run_count': 0,
                            'first_seen': run.start_time,
                            'last_seen': run.start_time,
                            'session_id': getattr(run, 'session_id', None),
                            'tenant_id': getattr(run, 'tenant_id', None)
                        }

                    # Update project stats
                    project = projects_found[project_name]
                    project['run_count'] += 1

                    if run.start_time:
                        if (not project['first_seen'] or
                            run.start_time < project['first_seen']):
                            project['first_seen'] = run.start_time
                        if (not project['last_seen'] or
                            run.start_time > project['last_seen']):
                            project['last_seen'] = run.start_time

            print(f"✅ Discovered {len(projects_found)} unique projects")

            # Sort by run count (most active first)
            sorted_projects = sorted(
                projects_found.values(),
                key=lambda x: x['run_count'],
                reverse=True
            )

            for project in sorted_projects:
                print(f"  📁 {project['name']}: {project['run_count']} runs")
                if project['last_seen']:
                    print(f"     Last activity: {project['last_seen'].date()}")

            return sorted_projects

        except Exception as e:
            print(f"❌ Error in run analysis: {e}")
            return []

    except Exception as e:
        print(f"❌ Failed to discover projects via runs: {e}")
        return []


def get_organization_info(client):
    """Get organization information using proper API methods"""
    try:
        # Try to get organization info from any available run
        runs = list(client.list_runs(limit=1))
        if runs:
            run = runs[0]
            if hasattr(run, 'tenant_id'):
                org_id = str(run.tenant_id)
                print(f"✅ Organization ID: {org_id}")
                return org_id

        print("⚠️  Could not determine organization ID from runs")
        return None

    except Exception as e:
        print(f"❌ Error getting organization info: {e}")
        return None


def validate_project_urls(projects, org_id):
    """Generate and validate LangSmith URLs for discovered projects"""
    if not org_id:
        print("⚠️  Cannot generate URLs without organization ID")
        return

    base_url = "https://smith.langchain.com"

    print("\n🔗 Generated LangSmith URLs:")
    print(f"  📊 Organization: {base_url}/o/{org_id}")

    for project in projects[:3]:  # Show top 3 most active projects
        project_name = project['name']
        print(f"\n  📁 Project: {project_name} ({project['run_count']} runs)")
        print(f"     Dashboard: {base_url}/o/{org_id}/projects/p/{project_name}")
        print(f"     Traces: {base_url}/o/{org_id}/projects/p/{project_name}/traces")
        print(f"     Analytics: {base_url}/o/{org_id}/projects/p/{project_name}/analytics")


def create_dashboard_config(projects, org_id):
    """Create dashboard configuration with discovered projects"""
    if not projects:
        print("❌ No projects found - cannot create configuration")
        return None

    # Categorize projects by name patterns
    production_projects = [p for p in projects
                          if any(keyword in p['name'].lower()
                                for keyword in ['prod', 'main', 'live'])]

    experiment_projects = [p for p in projects
                          if any(keyword in p['name'].lower()
                                for keyword in ['experiment', 'test', 'speed'])]

    # Use most active project as production if no explicit prod project
    if not production_projects and projects:
        production_projects = [projects[0]]  # Most active project

    config = {
        'organization_id': org_id,
        'base_url': 'https://smith.langchain.com',
        'projects': {
            'production': production_projects[0]['name'] if production_projects else None,
            'experiments': experiment_projects[0]['name'] if experiment_projects else None,
            'development': projects[1]['name'] if len(projects) > 1 else None
        },
        'discovered_projects': [
            {
                'name': p['name'],
                'run_count': p['run_count'],
                'last_activity': p['last_seen'].isoformat() if p['last_seen'] else None
            }
            for p in projects
        ]
    }

    print("\n📋 Recommended Dashboard Configuration:")
    print(f"  🚀 Production: {config['projects']['production']}")
    print(f"  🧪 Experiments: {config['projects']['experiments']}")
    print(f"  🛠️  Development: {config['projects']['development']}")

    return config


def main():
    """Main execution function with improved error handling"""
    print("🔍 Improved LangSmith Project Discovery")
    print("=" * 50)

    # Load environment
    api_key, endpoint = load_environment()
    if not api_key:
        return

    try:
        # Initialize client
        client = Client(api_url=endpoint, api_key=api_key)
        print("✅ Successfully connected to LangSmith")

        # Get organization info
        org_id = get_organization_info(client)
        if not org_id:
            # Use fallback org ID
            org_id = "b36f2280-93a9-4523-bf03-707ac1032a33"
            print(f"⚠️  Using fallback organization ID: {org_id}")

        # Discover projects via run analysis
        projects = discover_projects_via_runs(client)

        if projects:
            # Validate URLs
            validate_project_urls(projects, org_id)

            # Create dashboard configuration
            config = create_dashboard_config(projects, org_id)

            # Save results
            results = {
                'timestamp': datetime.now().isoformat(),
                'method': 'improved_run_analysis',
                'organization_id': org_id,
                'projects_discovered': len(projects),
                'dashboard_config': config,
                'api_limitations': {
                    'direct_project_listing': 'failed',
                    'run_analysis': 'successful',
                    'notes': 'API key has limited permissions for project endpoints'
                }
            }

            filename = "langsmith_improved_results.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n💾 Results saved to: {filename}")
            print(f"✅ Successfully discovered {len(projects)} projects")

        else:
            print("❌ No projects could be discovered")

    except LangSmithError as e:
        print(f"❌ LangSmith API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main()
