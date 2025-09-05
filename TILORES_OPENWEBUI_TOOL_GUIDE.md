# 🤖 **Tilores Backend Prompt Tool for OpenWebUI**

## **Complete Installation & Usage Guide**

This tool enables OpenWebUI to fetch and apply specialized agent system prompts from your Tilores backend API, providing consistent, professional responses for different use cases.

---

## **📋 Available Tilores Agents**

### **1. Zoho CS Agent** (`zoho_cs_agent`)

- **Purpose**: Customer service inquiries within Zoho Desk
- **Format**: Concise bullet points only
- **Use Cases**: Account status, payment issues, service inquiries
- **Special Features**: Automatically highlights past due accounts

### **2. Client Chat Agent** (`client_chat_agent`)

- **Purpose**: Direct client communication and credit education
- **Format**: Friendly, educational bullet points
- **Use Cases**: Credit report analysis, improvement advice, milestone celebrations
- **Special Features**: Encouraging tone, educational explanations

---

## **🚀 Installation Steps**

### **Step 1: Install the Tool in OpenWebUI**

1. **Navigate to Workspace → Tools** in OpenWebUI
2. **Click "Create Tool" or "+" button**
3. **Copy and paste the complete tool code** from `tilores_backend_prompt_tool.py`
4. **Set tool name**: "Tilores Backend Prompt Fetcher"
5. **Save the tool**

### **Step 2: Configure Tool Settings**

1. **Click the tool's settings/edit button**
2. **Configure the Valves**:
   - **BACKEND_URL**: `https://tilores-x.up.railway.app`
   - **BACKEND_API_KEY**: Leave empty (not required)
   - **REQUEST_TIMEOUT**: `10` (seconds)
   - **DEBUG_MODE**: `false` (set to `true` for troubleshooting)

### **Step 3: Enable Tool for Models**

**Option A: Enable for Specific Model**

1. Go to **Workspace → Models**
2. Find your model (e.g., GPT-4o) and click edit
3. Scroll to **Tools** section
4. Enable "Tilores Backend Prompt Fetcher"
5. Save

**Option B: Enable During Chat**

1. Start a chat with any model
2. Click the **+ button** in the chat input
3. Enable "Tilores Backend Prompt Fetcher" for this session

---

## **💬 Usage Examples**

### **Basic Usage - Zoho CS Agent**

```
User: "Use the Zoho CS agent to check who is e.j.price1986@gmail.com"

LLM: I'll fetch the Zoho CS agent prompt and use it to check that customer.

[LLM calls fetch_tilores_prompt("zoho_cs_agent", "Who is e.j.price1986@gmail.com")]

Tool Response: ✅ Tilores Agent Activated: Zoho Desk Customer Service Agent
[Bullet-point response format applied]

LLM: • Customer: Esteban Price
      • Status: Active
      • Product: Success PLUS Individual $149
      • Enrolled: 2025-04-10
```

### **Basic Usage - Client Chat Agent**

```
User: "Switch to client chat agent and explain credit scores"

[LLM calls fetch_tilores_prompt("client_chat_agent", "Explain credit scores")]

Tool Response: ✅ Tilores Agent Activated: Client-Facing Credit Advisor
[Friendly, educational format applied]

LLM: • Credit scores range from 300-850 - think of it like a report card for your finances! 📊
      • Higher scores unlock better interest rates and loan terms 🎯
      • Payment history is the biggest factor (35% of your score) ⭐
      • Keep credit utilization below 30% for best results 💳
```

### **Quick Shortcuts**

```
User: "Use zoho_cs shortcut to check account status for john@example.com"

[LLM calls zoho_cs("Check account status for john@example.com")]

User: "Use credit_advisor shortcut to analyze my credit report"

[LLM calls credit_advisor("Analyze my credit report")]
```

### **List Available Agents**

```
User: "What Tilores agents are available?"

[LLM calls list_tilores_agents()]

Tool Response: 🤖 Available Tilores Agent Prompts:
- Zoho Desk Customer Service Agent (zoho_cs_agent)
- Client-Facing Credit Advisor (client_chat_agent)
```

### **Test Connection**

```
User: "Test the Tilores backend connection"

[LLM calls test_tilores_connection()]

Tool Response: ✅ Tilores Backend Connection Successful!
🌐 URL: https://tilores-x.up.railway.app
⏱️ Response Time: 0.45s
🤖 Agent Prompts Available: True
📊 Available Agents: 2
```

---

## **🔧 Available Tool Functions**

### **Primary Functions**

| Function                                         | Description                  | Usage                        |
| ------------------------------------------------ | ---------------------------- | ---------------------------- |
| `fetch_tilores_prompt(agent_type, user_message)` | Fetch and apply agent prompt | Main function for all agents |
| `list_tilores_agents()`                          | List all available agents    | Discovery and reference      |
| `test_tilores_connection()`                      | Test backend connectivity    | Troubleshooting              |

### **Quick Shortcuts**

| Function                       | Description          | Equivalent To                                             |
| ------------------------------ | -------------------- | --------------------------------------------------------- |
| `zoho_cs(user_message)`        | Quick Zoho CS agent  | `fetch_tilores_prompt("zoho_cs_agent", user_message)`     |
| `credit_advisor(user_message)` | Quick credit advisor | `fetch_tilores_prompt("client_chat_agent", user_message)` |

---

## **🎯 Best Practices**

### **When to Use Zoho CS Agent**

- ✅ Account status inquiries
- ✅ Payment-related questions
- ✅ Service cancellations
- ✅ Quick factual lookups
- ✅ Internal CS team communication

### **When to Use Client Chat Agent**

- ✅ Credit education requests
- ✅ Credit report analysis
- ✅ Improvement recommendations
- ✅ Customer encouragement
- ✅ Direct client communication

### **Conversation Flow Tips**

1. **Start with agent selection**: "Use Zoho CS agent for..."
2. **Ask specific questions**: Include customer email or details
3. **Switch agents as needed**: "Now switch to credit advisor..."
4. **Use shortcuts for speed**: "zoho_cs check status for..."

---

## **🔍 Troubleshooting**

### **Tool Not Being Called**

- ✅ Ensure model supports function calling (GPT-4o, GPT-3.5-turbo-1106+)
- ✅ Use explicit instructions: "Please use the Tilores prompt fetcher tool"
- ✅ Enable DEBUG_MODE to see detailed errors

### **Backend Connection Issues**

- ✅ Verify BACKEND_URL: `https://tilores-x.up.railway.app`
- ✅ Test with `test_tilores_connection()` function
- ✅ Check network connectivity

### **Agent Not Found Errors**

- ✅ Use exact agent names: `zoho_cs_agent` or `client_chat_agent`
- ✅ Check available agents with `list_tilores_agents()`
- ✅ Verify backend is running

### **Response Format Issues**

- ✅ Agent prompts automatically format responses
- ✅ Zoho CS = bullet points only
- ✅ Client Chat = friendly bullet points
- ✅ No additional formatting needed

---

## **🔗 Backend API Endpoints**

The tool connects to these Tilores backend endpoints:

| Endpoint                      | Purpose          | Response          |
| ----------------------------- | ---------------- | ----------------- |
| `GET /api/health`             | Connection test  | Health status     |
| `GET /api/prompts`            | List agents      | Available agents  |
| `GET /api/prompts/{agent_id}` | Get agent prompt | Full agent config |

---

## **📊 Model Compatibility**

| Model               | Function Calling | Compatibility                  |
| ------------------- | ---------------- | ------------------------------ |
| GPT-4o              | ✅ Excellent     | Fully supported                |
| GPT-4o Mini         | ✅ Excellent     | Fully supported                |
| GPT-3.5-turbo-1106+ | ✅ Good          | Fully supported                |
| Claude 3.5+         | ✅ Good          | Fully supported                |
| Local models        | ⚠️ Limited       | May not reliably call tools    |
| Basic models        | ❌ None          | Function calling not supported |

---

## **🎉 Success Indicators**

### **Tool Working Correctly**

- ✅ Agent activation messages appear
- ✅ Response format matches agent type
- ✅ Bullet points for both agents
- ✅ Professional tone maintained

### **Zoho CS Agent Success**

- ✅ Concise, factual responses
- ✅ Bullet points only
- ✅ Past due accounts highlighted
- ✅ Actionable information provided

### **Client Chat Agent Success**

- ✅ Friendly, encouraging tone
- ✅ Educational explanations
- ✅ Bullet point format
- ✅ Credit improvement focus

---

## **🚀 Ready to Use!**

Your Tilores Backend Prompt Tool is now configured and ready to provide specialized, professional responses for both customer service and client communication scenarios. The tool seamlessly integrates with your existing Tilores backend to ensure consistent, high-quality interactions across all channels.

**Need help?** Use the `test_tilores_connection()` function to verify everything is working correctly!
