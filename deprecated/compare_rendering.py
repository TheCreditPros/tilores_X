#!/usr/bin/env python3
"""
Compare API response vs OpenWebUI rendering
"""

import requests
import json

def test_client_agent_query():
    """Test the working client agent query"""

    query = "/client my email is e.j.price1986@gmail.com, how is my credit"

    print("🧪 TESTING CLIENT AGENT QUERY")
    print("=" * 50)
    print(f"Query: {query}")

    try:
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": query}],
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            print(f"\n📊 RESPONSE ANALYSIS:")
            print(f"Length: {len(content)} characters")
            print(f"Lines: {content.count(chr(10))} line breaks")
            print(f"Bold headers: {content.count('**')//2} pairs")
            print(f"Bullets: {content.count('- ')}")

            print(f"\n📝 RAW RESPONSE (first 500 chars):")
            print("-" * 50)
            print(repr(content[:500]))
            print("-" * 50)

            print(f"\n🎨 FORMATTED PREVIEW:")
            print("-" * 50)
            print(content[:800])
            print("-" * 50)

            # Save full response for manual inspection
            with open("client_agent_response.txt", "w") as f:
                f.write(content)

            print(f"\n💾 Full response saved to: client_agent_response.txt")

            print(f"\n🌐 OPENWEBUI TEST INSTRUCTIONS:")
            print("1. Open http://localhost:3000")
            print("2. Configure API: http://host.docker.internal:8080/v1")
            print("3. Send exact query:")
            print(f"   {query}")
            print("4. Compare rendering with the saved response")
            print("5. Look for differences in:")
            print("   - Bold text rendering (**text** vs <strong>text</strong>)")
            print("   - Bullet point spacing")
            print("   - Line break handling")
            print("   - Section separation")

        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_client_agent_query()
