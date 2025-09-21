"""
Tilores Backend Prompt Fetcher Tool for Open WebUI
Author: Tilores Team
Description: Fetches system prompts from Tilores backend API and applies them to conversations
Version: 1.0

This tool integrates with the Tilores Credit API to fetch agent-specific system prompts
and apply them to conversations for consistent, specialized responses.
"""

import requests
import json
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Tools:
    class Valves(BaseModel):
        # Configuration settings that users can modify in the UI
        BACKEND_URL: str = Field(
            default="https://tilores-x.up.railway.app",
            description="Base URL of Tilores backend API (without trailing slash)"
        )
        BACKEND_API_KEY: str = Field(
            default="",
            description="API key for authenticating with Tilores backend (optional)"
        )
        REQUEST_TIMEOUT: int = Field(
            default=10,
            description="Timeout for backend requests in seconds"
        )
        DEBUG_MODE: bool = Field(
            default=False,
            description="Enable debug mode for detailed error messages"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.name = "tilores_prompt_fetcher"
        self.description = "Fetches Tilores agent system prompts from backend API"

    def fetch_tilores_prompt(
        self, 
        agent_type: str, 
        user_message: str = "",
        variables: Optional[str] = None
    ) -> str:
        """
        Fetch a Tilores agent system prompt from backend API and apply it to the conversation
        
        Args:
            agent_type (str): The agent type ("zoho_cs_agent" or "client_chat_agent")
            user_message (str): The user's question/request to process with this prompt
            variables (str, optional): JSON string of variables to populate in the prompt template
        
        Returns:
            str: Formatted response with system prompt context applied
        
        Example usage:
            - fetch_tilores_prompt("zoho_cs_agent", "Who is e.j.price1986@gmail.com")
            - fetch_tilores_prompt("client_chat_agent", "What is my credit score?")
        """
        
        try:
            # Parse variables if provided
            prompt_variables = {}
            if variables:
                try:
                    prompt_variables = json.loads(variables)
                except json.JSONDecodeError as e:
                    if self.valves.DEBUG_MODE:
                        return f"❌ Error parsing variables: {str(e)}"
                    return "❌ Invalid variables format. Please provide valid JSON."

            # Prepare request headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "OpenWebUI-Tilores-Tool/1.0"
            }
            
            if self.valves.BACKEND_API_KEY:
                headers["Authorization"] = f"Bearer {self.valves.BACKEND_API_KEY}"

            # Make request to backend
            url = f"{self.valves.BACKEND_URL.rstrip('/')}/api/prompts/{agent_type}"
            
            if self.valves.DEBUG_MODE:
                debug_info = f"🔍 Making request to: {url}\n"
                debug_info += f"🔍 Headers: {headers}\n\n"
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.valves.REQUEST_TIMEOUT
            )

            # Handle HTTP errors
            if response.status_code == 404:
                return f"❌ Agent type '{agent_type}' not found. Available agents: zoho_cs_agent, client_chat_agent"
            elif response.status_code == 401:
                return f"❌ Authentication failed. Check your API key."
            elif response.status_code == 403:
                return f"❌ Access denied. Insufficient permissions for agent '{agent_type}'"
            elif response.status_code != 200:
                if self.valves.DEBUG_MODE:
                    return f"❌ Backend error: {response.status_code} - {response.text}"
                return f"❌ Backend request failed with status {response.status_code}"

            # Parse response
            try:
                prompt_data = response.json()
            except json.JSONDecodeError:
                if self.valves.DEBUG_MODE:
                    return f"❌ Invalid JSON response from backend: {response.text[:200]}"
                return "❌ Invalid response format from backend"

            # Check for error in response
            if "error" in prompt_data:
                return f"❌ Backend error: {prompt_data['error']}"

            # Extract prompt content
            system_prompt = prompt_data.get("content", "")
            if not system_prompt:
                return f"❌ Empty prompt content for agent '{agent_type}'"

            # Get additional metadata
            prompt_name = prompt_data.get("name", agent_type)
            prompt_description = prompt_data.get("description", "")
            use_case = prompt_data.get("use_case", "")
            format_info = prompt_data.get("format", "")
            
            # Populate variables in prompt template
            if prompt_variables:
                try:
                    system_prompt = system_prompt.format(**prompt_variables)
                except KeyError as e:
                    return f"❌ Missing variable '{e}' required by prompt template"
                except Exception as e:
                    if self.valves.DEBUG_MODE:
                        return f"❌ Error formatting prompt: {str(e)}"
                    return "❌ Error applying variables to prompt template"

            # Format the response
            result = self._format_prompt_response(
                agent_type=agent_type,
                prompt_name=prompt_name,
                prompt_description=prompt_description,
                use_case=use_case,
                format_info=format_info,
                system_prompt=system_prompt,
                user_message=user_message,
                variables=prompt_variables
            )

            if self.valves.DEBUG_MODE:
                result = debug_info + result

            return result

        except requests.exceptions.Timeout:
            return f"❌ Request timeout. Backend took longer than {self.valves.REQUEST_TIMEOUT} seconds to respond."
        
        except requests.exceptions.ConnectionError:
            return f"❌ Connection error. Cannot reach Tilores backend at {self.valves.BACKEND_URL}"
        
        except requests.exceptions.RequestException as e:
            if self.valves.DEBUG_MODE:
                return f"❌ Request error: {str(e)}"
            return "❌ Network error occurred while fetching prompt"
        
        except Exception as e:
            if self.valves.DEBUG_MODE:
                return f"❌ Unexpected error: {str(e)}"
            return "❌ An unexpected error occurred"

    def _format_prompt_response(
        self, 
        agent_type: str,
        prompt_name: str, 
        prompt_description: str,
        use_case: str,
        format_info: str,
        system_prompt: str, 
        user_message: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Format the tool response with proper structure"""
        
        result = f"✅ **Tilores Agent Activated: {prompt_name}**\n\n"
        
        if prompt_description:
            result += f"📝 **Description:** {prompt_description}\n\n"
        
        if use_case:
            result += f"🎯 **Use Case:** {use_case}\n\n"
            
        if format_info:
            result += f"📋 **Response Format:** {format_info}\n\n"
        
        # Show variables if any were used
        if variables:
            result += f"🔧 **Variables Applied:** {', '.join([f'{k}={v}' for k, v in variables.items()])}\n\n"
        
        # Show truncated system prompt for reference
        prompt_preview = system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
        result += f"🤖 **Agent Context Preview:** {prompt_preview}\n\n"
        
        if user_message:
            result += f"❓ **Your Question:** {user_message}\n\n"
            result += f"I am now operating as the **{prompt_name}**. Let me address your question:\n\n"
            result += f"---\n\n"
            # The actual system prompt content for the LLM to use
            result += system_prompt
            if user_message:
                result += f"\n\nUser question: {user_message}"
        else:
            result += f"The **{prompt_name}** is now active. You can ask your question and I'll respond according to this agent's specialized context."
        
        return result

    def list_tilores_agents(self) -> str:
        """
        List all available Tilores agent prompts from the backend
        
        Returns:
            str: Formatted list of available agent prompts
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "OpenWebUI-Tilores-Tool/1.0"
            }
            
            if self.valves.BACKEND_API_KEY:
                headers["Authorization"] = f"Bearer {self.valves.BACKEND_API_KEY}"

            url = f"{self.valves.BACKEND_URL.rstrip('/')}/api/prompts"
            response = requests.get(url, headers=headers, timeout=self.valves.REQUEST_TIMEOUT)
            
            if response.status_code != 200:
                return f"❌ Could not fetch agent list: {response.status_code}"
            
            prompts = response.json()
            
            if "error" in prompts:
                return f"❌ Backend error: {prompts['error']}"
            
            if not prompts:
                return "📝 No agent prompts available in Tilores backend system"
            
            result = "🤖 **Available Tilores Agent Prompts:**\n\n"
            
            for prompt in prompts:
                agent_id = prompt.get("id", "unknown")
                name = prompt.get("name", agent_id)
                description = prompt.get("description", "No description")
                use_case = prompt.get("use_case", "General")
                format_info = prompt.get("format", "Standard")
                
                result += f"### **{name}** (`{agent_id}`)\n"
                result += f"**Description:** {description}\n"
                result += f"**Use Case:** {use_case}\n"
                result += f"**Format:** {format_info}\n\n"
            
            result += f"**Usage:** Use `fetch_tilores_prompt(agent_type, your_message)` to activate any of these agents.\n\n"
            result += f"**Examples:**\n"
            result += f"• `fetch_tilores_prompt(\"zoho_cs_agent\", \"Who is e.j.price1986@gmail.com\")`\n"
            result += f"• `fetch_tilores_prompt(\"client_chat_agent\", \"What is my credit score?\")`"
            
            return result
            
        except Exception as e:
            if self.valves.DEBUG_MODE:
                return f"❌ Error listing agents: {str(e)}"
            return "❌ Could not retrieve agent list from Tilores backend"

    def test_tilores_connection(self) -> str:
        """
        Test the connection to the Tilores backend API
        
        Returns:
            str: Connection test results
        """
        try:
            headers = {}
            if self.valves.BACKEND_API_KEY:
                headers["Authorization"] = f"Bearer {self.valves.BACKEND_API_KEY}"
            
            # Try to hit the health endpoint
            url = f"{self.valves.BACKEND_URL.rstrip('/')}/api/health"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                result = f"✅ **Tilores Backend Connection Successful!**\n\n"
                result += f"🌐 **URL:** {self.valves.BACKEND_URL}\n"
                result += f"⏱️ **Response Time:** {response.elapsed.total_seconds():.2f}s\n"
                result += f"🏥 **Status:** {health_data.get('status', 'unknown')}\n"
                result += f"🔧 **Service:** {health_data.get('service', 'unknown')}\n"
                result += f"🤖 **Agent Prompts Available:** {health_data.get('agent_prompts_available', False)}\n"
                result += f"📊 **Available Agents:** {health_data.get('available_agents', 0)}\n"
                result += f"🕒 **Timestamp:** {health_data.get('timestamp', 'unknown')}"
                return result
            else:
                return f"⚠️ Tilores backend responded with status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return f"❌ Cannot connect to Tilores backend at {self.valves.BACKEND_URL}"
        except requests.exceptions.Timeout:
            return f"❌ Tilores backend connection timeout"
        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"

    def zoho_cs(self, user_message: str = "") -> str:
        """
        Quick shortcut to activate Zoho CS Agent
        
        Args:
            user_message (str): The user's question for the CS agent
            
        Returns:
            str: Response with Zoho CS agent context applied
        """
        return self.fetch_tilores_prompt("zoho_cs_agent", user_message)

    def credit_advisor(self, user_message: str = "") -> str:
        """
        Quick shortcut to activate Client Credit Advisor Agent
        
        Args:
            user_message (str): The user's question for the credit advisor
            
        Returns:
            str: Response with credit advisor agent context applied
        """
        return self.fetch_tilores_prompt("client_chat_agent", user_message)
