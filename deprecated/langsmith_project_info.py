#!/usr/bin/env python3
"""
LangSmith Project Information Script
This script connects to LangSmith and retrieves project and organization information.
"""

import os
import json
from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import LangSmithError


def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()

    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

    if not api_key:
        print("❌ ERROR: LANGSMITH_API_KEY or LANGCHAIN_API_KEY not found in environment")
        print("   Please set one of these variables in your .env file")
        return None, None

    print(f"✅ Found API key (ends with: ...{api_key[-4:]})")
    print(f"✅ Using endpoint: {endpoint}")

    return api_key, endpoint


def get_langsmith_info(api_key, endpoint):
    """Connect to LangSmith and retrieve project information"""
    try:
        # Initialize LangSmith client
        client = Client(api_url=endpoint, api_key=api_key)
        print("✅ Successfully connected to LangSmith")

        # Try to get projects/sessions using available methods
        print("\n🔍 Retrieving project information...")
        projects = []
        organization_id = None

        try:
            # First, try to get runs and extract project info from them
            print("🔄 Checking recent runs to find projects...")
            runs = list(client.list_runs(limit=100))
            unique_projects = {}

            for run in runs:
                project_name = None
                if hasattr(run, "session_name") and run.session_name:
                    project_name = run.session_name
                elif hasattr(run, "project_name") and run.project_name:
                    project_name = run.project_name

                if project_name and project_name not in unique_projects:
                    unique_projects[project_name] = {
                        "name": project_name,
                        "id": getattr(run, "session_id", "unknown"),
                        "runs_count": 1,
                        "last_run_time": (
                            run.start_time.isoformat() if hasattr(run, "start_time") and run.start_time else None
                        ),
                        "tenant_id": str(run.tenant_id) if hasattr(run, "tenant_id") else None,
                    }
                elif project_name:
                    unique_projects[project_name]["runs_count"] += 1

                # Extract organization ID from first run
                if not organization_id and hasattr(run, "tenant_id"):
                    organization_id = str(run.tenant_id)

            projects = list(unique_projects.values())
            print(f"✅ Found {len(projects)} unique projects from {len(runs)} runs")

            for project in projects:
                print(f"  📁 Project: {project['name']} ({project['runs_count']} runs)")

        except Exception as e:
            print(f"❌ Error retrieving runs: {e}")

            # Try direct REST API call as fallback
            try:
                print("🔄 Trying direct API approach...")
                import requests

                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

                # Try to get sessions/projects directly
                response = requests.get(f"{endpoint}/sessions", headers=headers, params={"limit": 50})
                if response.status_code == 200:
                    sessions_data = response.json()
                    if isinstance(sessions_data, list):
                        projects = sessions_data
                    elif isinstance(sessions_data, dict) and "sessions" in sessions_data:
                        projects = sessions_data["sessions"]
                    print(f"✅ Found {len(projects)} projects via direct API")
                else:
                    print(f"❌ API request failed: {response.status_code}")

            except Exception as e2:
                print(f"❌ Direct API approach also failed: {e2}")

        # If we still don't have org ID, use fallback
        if not organization_id:
            print("⚠️  Could not determine organization ID from API")
            # Use the hardcoded org ID from the task description as fallback
            organization_id = "b36f2280-93a9-4523-bf03-707ac1032a33"
            print(f"⚠️  Using fallback organization ID: {organization_id}")

        # Return comprehensive info
        return {
            "connection_status": "success",
            "endpoint": endpoint,
            "organization_id": organization_id,
            "projects": projects,  # Projects found from runs or API
            "project_count": len(projects),
        }

    except LangSmithError as e:
        print(f"❌ LangSmith API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None


def analyze_projects(info):
    """Analyze projects to identify production, development, and experiment environments"""
    if not info or not info.get("projects"):
        print("❌ No project information available for analysis")
        return

    projects = info["projects"]
    print(f"\n📈 Analyzing {len(projects)} projects...")

    production_projects = []
    development_projects = []
    experiment_projects = []
    other_projects = []

    for project in projects:
        name = project["name"].lower()

        # Categorize based on naming patterns
        if any(keyword in name for keyword in ["production", "prod", "live"]):
            production_projects.append(project)
        elif any(keyword in name for keyword in ["dev", "development", "test", "staging"]):
            development_projects.append(project)
        elif any(keyword in name for keyword in ["experiment", "exp", "trial", "benchmark"]):
            experiment_projects.append(project)
        else:
            other_projects.append(project)

    print("\n🏗️  Project Categories:")
    print(f"  🚀 Production: {len(production_projects)} projects")
    for proj in production_projects:
        print(f"     - {proj['name']} (ID: {proj['id']})")

    print(f"  🧪 Development/Test: {len(development_projects)} projects")
    for proj in development_projects:
        print(f"     - {proj['name']} (ID: {proj['id']})")

    print(f"  🔬 Experiments: {len(experiment_projects)} projects")
    for proj in experiment_projects:
        print(f"     - {proj['name']} (ID: {proj['id']})")

    print(f"  📂 Other: {len(other_projects)} projects")
    for proj in other_projects:
        print(f"     - {proj['name']} (ID: {proj['id']})")

    return {
        "production": production_projects,
        "development": development_projects,
        "experiments": experiment_projects,
        "other": other_projects,
    }


def generate_example_urls(info, categorized_projects):
    """Generate example LangSmith URLs for different features"""
    if not info or not info.get("organization_id"):
        print("⚠️  Cannot generate URLs without organization ID")
        return

    org_id = info["organization_id"]
    base_url = "https://smith.langchain.com"

    print("\n🔗 Example LangSmith URLs:")
    print(f"  📊 Organization Dashboard: {base_url}/o/{org_id}")
    print(f"  ⚙️  Organization Settings: {base_url}/o/{org_id}/settings")

    # Generate URLs for each project category
    if categorized_projects:
        for category, projects in categorized_projects.items():
            if projects and category != "other":
                project = projects[0]  # Use first project as example
                project_id = project["id"]
                print(f"\n  📁 {category.title()} Project Examples (using '{project['name']}'):")
                print(f"     - Project Dashboard: {base_url}/o/{org_id}/projects/p/{project_id}")
                print(f"     - Traces: {base_url}/o/{org_id}/projects/p/{project_id}/traces")
                print(f"     - Experiments: {base_url}/o/{org_id}/projects/p/{project_id}/experiments")
                print(f"     - Analytics: {base_url}/o/{org_id}/projects/p/{project_id}/analytics")
                print(f"     - Settings: {base_url}/o/{org_id}/projects/p/{project_id}/settings")


def save_results(info, categorized_projects):
    """Save results to a JSON file for later reference"""
    results = {
        "timestamp": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
        "langsmith_info": info,
        "categorized_projects": categorized_projects,
        "recommendations": {
            "organization_id": info.get("organization_id"),
            "base_api_url": info.get("endpoint"),
            "dashboard_base_url": "https://smith.langchain.com",
            "suggested_project_names": {
                "production": "tilores_production",
                "development": "tilores_development",
                "experiments": "tilores_experiments",
            },
        },
    }

    filename = "langsmith_project_info_results.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {filename}")
    return filename


def main():
    """Main execution function"""
    print("🔍 LangSmith Project Information Retrieval")
    print("=" * 50)

    # Load environment
    api_key, endpoint = load_environment()
    if not api_key:
        return

    # Get LangSmith information
    info = get_langsmith_info(api_key, endpoint)
    if not info:
        print("❌ Failed to retrieve LangSmith information")
        return

    # Analyze projects
    categorized_projects = analyze_projects(info)

    # Generate example URLs
    generate_example_urls(info, categorized_projects)

    # Save results
    results_file = save_results(info, categorized_projects)

    print("\n✅ LangSmith project information retrieval completed!")
    print("📋 Summary:")
    print(f"   - Total projects: {info.get('project_count', 0)}")
    print(f"   - Organization ID: {info.get('organization_id', 'Unknown')}")
    print(f"   - Results file: {results_file}")


if __name__ == "__main__":
    main()
