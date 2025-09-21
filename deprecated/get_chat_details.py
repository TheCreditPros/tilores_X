#!/usr/bin/env python3
"""
Get Chat Details from Available Logs
Retrieves the most detailed information available about recent chats
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def load_jsonl(filename: str) -> List[Dict[str, Any]]:
    """Load data from JSONL file"""
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return data

def get_last_chat_details():
    """Get details of the most recent chat interaction"""

    print("🔍 Analyzing Available Chat Data")
    print("=" * 50)

    # Load rating data
    ratings = load_jsonl("openwebui_ratings.jsonl")

    if not ratings:
        print("❌ No chat data found in logs")
        return

    # Get the most recent interaction
    last_rating = ratings[-1]

    print(f"📊 Most Recent Chat Interaction:")
    print(f"   Chat ID: {last_rating.get('chat_id', 'N/A')}")
    print(f"   Message ID: {last_rating.get('message_id', 'N/A')}")
    print(f"   User ID: {last_rating.get('user_id', 'N/A')}")
    print(f"   Model Used: {last_rating.get('model', 'N/A')}")
    print(f"   User Rating: {last_rating.get('rating', 'N/A')}")
    print(f"   Timestamp: {last_rating.get('received_at', 'N/A')}")
    print(f"   Source IP: {last_rating.get('ip', 'N/A')}")
    print(f"   Tags: {last_rating.get('tags', [])}")

    # Find all interactions for this chat
    chat_id = last_rating.get('chat_id')
    if chat_id:
        print(f"\n📚 All Interactions for Chat '{chat_id}':")
        chat_interactions = [r for r in ratings if r.get('chat_id') == chat_id]

        for i, interaction in enumerate(chat_interactions, 1):
            print(f"   {i}. {interaction.get('received_at', 'N/A')} - "
                  f"Model: {interaction.get('model', 'N/A')} - "
                  f"Rating: {interaction.get('rating', 'N/A')}")

    # Summary statistics
    print(f"\n📈 Summary Statistics:")
    print(f"   Total Interactions: {len(ratings)}")

    models_used = [r.get('model') for r in ratings if r.get('model')]
    unique_models = list(set(models_used))
    print(f"   Models Used: {len(unique_models)} unique models")
    for model in unique_models:
        count = models_used.count(model)
        print(f"     - {model}: {count} interactions")

    ratings_count = {}
    for r in ratings:
        rating = r.get('rating', 'unknown')
        ratings_count[rating] = ratings_count.get(rating, 0) + 1

    print(f"   Rating Distribution:")
    for rating, count in ratings_count.items():
        print(f"     - {rating}: {count} ratings")

    print(f"\n⚠️  Note: Current webhook only captures rating events.")
    print(f"   To capture full messages, implement enhanced chat webhook.")
    print(f"   Enhanced webhook available in: enhanced_chat_webhook.py")

def get_recent_activity(limit: int = 5):
    """Get recent activity summary"""

    ratings = load_jsonl("openwebui_ratings.jsonl")

    if not ratings:
        return

    print(f"\n🕒 Recent Activity (Last {limit} interactions):")
    print("-" * 50)

    recent = ratings[-limit:]
    for i, interaction in enumerate(reversed(recent), 1):
        timestamp = interaction.get('received_at', 'N/A')
        model = interaction.get('model', 'N/A')
        rating = interaction.get('rating', 'N/A')
        chat_id = interaction.get('chat_id', 'N/A')

        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp

        print(f"{i:2d}. {time_str} | {model:20s} | {rating:4s} | Chat: {chat_id}")

if __name__ == "__main__":
    get_last_chat_details()
    get_recent_activity(10)
