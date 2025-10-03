# llmswap v5.1.1 - Multiple AI Second Brains with Memory & Mentorship

[![PyPI version](https://badge.fury.io/py/llmswap.svg)](https://badge.fury.io/py/llmswap)
[![PyPI Downloads](https://static.pepy.tech/badge/llmswap)](https://pepy.tech/projects/llmswap)
[![Homebrew](https://img.shields.io/badge/homebrew-available-blue?logo=homebrew)](https://github.com/llmswap/homebrew-tap)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**📚 Documentation:** [llmswap.org](https://llmswap.org) | **⚡ CLI Reference:** [CLI Docs](https://llmswap.org/docs/cli.html) | **🐍 SDK Guide:** [SDK Docs](https://llmswap.org/docs/sdk.html)

## ⚡ Quick Start (30 seconds)

```bash
# Install
pip install llmswap

# or Homebrew
brew tap llmswap/tap && brew install llmswap

# Create your first workspace
cd ~/my-project
llmswap workspace init

# Chat with AI that remembers everything
llmswap chat "Help me with Flask routing"
# AI has full project context + all past learnings!
```

> **🆕 Now with Claude Sonnet 4.5!** llmswap supports Anthropic's latest and most advanced coding model. Use `--model claude-sonnet-4-5` or set as default in config. The best AI coding assistant just got better!

**The First AI Tool with Project Memory & Learning Journals** - v5.1.0 introduces revolutionary workspace system that remembers your learning journey across projects. Build apps without vendor lock-in (SDK) or use from terminal (CLI). Works with your existing subscriptions: Claude, OpenAI, Gemini, Cohere, Perplexity, IBM watsonx, Groq, Ollama (8+ providers).

**🎯 Solve These Common Problems:**
- ❌ "I need multiple second brains for different aspects of my life" 🆕
- ❌ "AI strays over time, I need to re-steer it constantly" 🆕
- ❌ "I keep explaining the same context to AI over and over"
- ❌ "AI forgets what I learned yesterday"
- ❌ "I lose track of architecture decisions across projects"
- ❌ "Context switching between projects is exhausting"
- ❌ "I want AI to understand my specific codebase, not generic answers"

**✅ llmswap v5.1.0 Solves All These:**
- ✅ Multiple independent "second brains" per project/life aspect 🆕
- ✅ Persistent context prevents AI from straying 🆕
- ✅ Per-project workspaces that persist context across sessions
- ✅ Auto-tracked learning journals - never forget what you learned
- ✅ Architecture decision logs - all your technical decisions documented
- ✅ Zero context switching - AI loads the right project automatically
- ✅ Project-aware AI - mentor understands YOUR specific tech stack

**Two tools in one:**
- 🐍 **Python SDK** - Build apps without vendor lock-in (started here!)
- ⚡ **CLI tool** - Terminal interface that works with any subscription (bonus!)

**Why llmswap?**
- 🔓 **No vendor lock-in** - Switch providers with 1 line of code (SDK) or 1 command (CLI)
- 🎓 **Teaching-first AI** - Eklavya mentorship system (guru, coach, socrates personas)
- 💰 **Cost optimizer** - Automatic caching saves 50-90% on API calls
- 🔧 **For apps AND terminal** - One tool, two ways to use it

**v5.1.0**: Revolutionary AI mentorship with **project memory**, **workspace-aware context**, **auto-tracked learning journals**, and **persistent mentor relationships**. The first AI tool that truly remembers your learning journey across projects.

**NEW in v5.1.0:**
- 🧠 **Workspace Memory** - Per-project context that persists across sessions
- 📚 **Auto-Learning Journal** - Automatically tracks what you learn in each project
- 🎯 **Context-Aware Mentorship** - AI mentor understands your project and past learnings
- 📖 **Architecture Decision Log** - Document and remember key technical decisions
- 🔄 **Cross-Project Intelligence** - Learn patterns from one project, apply to another
- 💡 **Proactive Learning** - AI suggests next topics based on your progress
- 🗂️ **Project Knowledge Base** - Custom prompt library per workspace

## 🧠 Finally: An Elegant Solution for Multiple Second Brains

**The Problem Industry Leaders Can't Solve:**

> "I still haven't found an elegant solution to the fact that I need several second brains for the various aspects of my life, each with different styles and contexts." - Industry feedback

**The llmswap Solution: Workspace System**

Each aspect of your life gets its own "brain" with independent memory:

- 💼 **Work Projects** - `~/work/api-platform` - Enterprise patterns, team conventions
- 📚 **Learning** - `~/learning/rust` - Your learning journey, struggles, progress
- 🚀 **Side Projects** - `~/personal/automation` - Personal preferences, experiments
- 🌐 **Open Source** - `~/oss/django` - Community patterns, contribution history

**What Makes It "Elegant":**
- ✅ Zero configuration - just `cd` to project directory
- ✅ Auto-switching - AI loads the right "brain" automatically
- ✅ No context bleed - work knowledge stays separate from personal
- ✅ Persistent memory - each brain remembers across sessions
- ✅ Independent personas - different teaching style per project if you want

**Stop Re-Explaining Context. Start Building.**

---

## 🎯 Transform AI Into Your Personal Mentor with Project Memory

**Inspired by Eklavya** - the legendary self-taught archer who learned from dedication and the right guidance - llmswap transforms any AI provider into a personalized mentor that adapts to your learning style **and remembers your journey**.

**The Challenge:** Developers struggle to learn effectively from AI because:
- 🔴 Responses are generic, lack personality, and don't adapt to individual needs
- 🔴 AI loses context between sessions - you repeat the same explanations
- 🔴 No learning history - AI doesn't know what you already learned
- 🔴 Project context is lost - AI doesn't understand your codebase

**Our Solution v5.1.0:** Choose your mentorship style, initialize a workspace, and ANY AI provider becomes **your personalized guide that remembers everything**:

```bash
# 🆕 v5.1.0: Initialize workspace for your project
cd ~/my-flask-app
llmswap workspace init
# Creates .llmswap/ with context.md, learnings.md, decisions.md

# Now your AI mentor KNOWS your project
llmswap chat --mentor guru --alias "Guruji"
# Mentor has full context: your tech stack, past learnings, decisions made

# 🆕 Auto-tracked learning journal
# Every conversation automatically saves key learnings
llmswap workspace journal
# View everything you've learned in this project

# 🆕 Architecture decision log
llmswap workspace decisions
# See all technical decisions documented automatically

# View all your workspaces
llmswap workspace list

# Get wisdom and deep insights from a patient teacher
llmswap chat --mentor guru --alias "Guruji"

# High-energy motivation when you're stuck
llmswap ask "How do I debug this?" --mentor coach

# Collaborative peer learning for exploring ideas
llmswap chat --mentor friend --alias "CodeBuddy"

# Question-based learning for critical thinking
llmswap ask "Explain REST APIs" --mentor socrates

# 🆕 Use Claude Sonnet 4.5 - Best coding model
llmswap chat --provider anthropic --model claude-sonnet-4-5
# Or set as default in config for all queries
```

### 🔄 Rotate Personas to Expose Blind Spots

**Industry Insight:** "Rotate personas: mentor, skeptic, investor, end-user. Each lens exposes blind spots differently."

**Use Case: Reviewing API Design**

```bash
# Round 1: Long-term wisdom
llmswap chat --mentor guru "Design API for multi-tenant SaaS"
# Catches: scalability, technical debt, maintenance

# Round 2: Critical questions
llmswap chat --mentor socrates "Review this API design"
# Catches: assumptions, alternatives, edge cases

# Round 3: Practical execution
llmswap chat --mentor coach "What's the fastest path to v1?"
# Catches: over-engineering, paralysis by analysis
```

**Same project context. Different perspectives. Complete understanding.**

**What Makes v5.1.0 Revolutionary:**
- 🧠 **Works with ANY provider** - Transform Claude, GPT-4, or Gemini into your mentor
- 🎭 **6 Teaching Personas** - Guru, Coach, Friend, Socrates, Professor, Tutor
- 📊 **Project Memory** - Per-project context that persists across sessions ⭐ NEW
- 📚 **Auto-Learning Journal** - Automatically tracks what you learn ⭐ NEW
- 📖 **Decision Tracking** - Documents architecture decisions ⭐ NEW
- 🎓 **Age-Appropriate** - Explanations tailored to your level (--age 10, --age 25, etc.)
- 💰 **Cost Optimized** - Use cheaper providers for learning, premium for complex problems
- 🔄 **Workspace Detection** - Automatically loads project context ⭐ NEW

**Traditional AI tools give you answers. llmswap v5.1.0 gives you a personalized learning journey that REMEMBERS.**

## 🆚 llmswap vs Single-Provider Tools

### For Python Developers Building Apps:

| Your Need | Single-Provider SDKs | llmswap SDK |
|-----------|---------------------|-------------|
| Build chatbot/app | Import `openai` library (locked in) | Import `llmswap` (works with any provider) |
| Switch providers | Rewrite all API calls | Change 1 line: `provider="anthropic"` |
| Try different models | Sign up, new SDK, refactor code | Just change config, same code |
| Cost optimization | Manual implementation | Built-in caching (50-90% savings) |
| Use multiple providers | Maintain separate codebases | One codebase, switch dynamically |

### For Developers Using Terminal:

| Your Need | Vendor CLIs | llmswap CLI |
|-----------|-------------|-------------|
| Have Claude subscription | Install Claude Code (Claude only) | Use llmswap (works with Claude) |
| Have OpenAI subscription | Build your own scripts | Use llmswap (works with OpenAI) |
| Have multiple subscriptions | Install 3+ different CLIs | One CLI for all subscriptions |
| Want AI to teach you | Not available | Built-in Eklavya mentorship |
| Switch providers mid-chat | Can't - locked in | `/switch anthropic` command |

**The Bottom Line:**
- **Building an app?** Use llmswap SDK - no vendor lock-in
- **Using terminal?** Use llmswap CLI - works with your existing subscriptions
- **Both?** Perfect - it's the same tool!

```bash
# 🆕 NEW v5.1.0: Workspace System - Project Memory That Persists
llmswap workspace init
# Creates .llmswap/ directory with:
#   - workspace.json (project metadata)
#   - context.md (editable project description)
#   - learnings.md (auto-tracked learning journal)
#   - decisions.md (architecture decision log)

llmswap workspace list                    # View all your workspaces
llmswap workspace info                    # Show current workspace statistics
llmswap workspace journal                 # View learning journal
llmswap workspace decisions               # View decision log
llmswap workspace context                 # Edit project context

# 🆕 NEW v5.1.0: Context-Aware Mentorship
# AI mentor automatically loads project context, past learnings, and decisions
llmswap chat
# Mentor knows: your tech stack, what you've learned, decisions made

# 🆕 NEW v5.0: Age-Appropriate AI Explanations
llmswap ask "What is Docker?" --age 10
# Output: "Docker is like a magic lunch box! 🥪 When your mom packs..."

llmswap ask "What is blockchain?" --audience "business owner"
# Output: "Think of blockchain like your business ledger system..."

# 🆕 NEW v5.0: Teaching Personas & Personalization  
llmswap ask "Explain Python classes" --teach --mentor developer --alias "Sarah"
# Output: "[Sarah - Senior Developer]: Here's how we handle classes in production..."

# 🆕 NEW v5.0: Conversational Chat with Provider Switching
llmswap chat --age 25 --mentor tutor
# In chat: /switch anthropic  # Switch mid-conversation
# In chat: /provider         # See current provider
# Commands: /help, /switch, /clear, /stats, /quit

# 🆕 NEW v5.0: Provider Management & Configuration
llmswap providers                    # View all providers and their status
llmswap config set provider.models.cohere command-r-plus-08-2024
llmswap config set provider.default anthropic
llmswap config show

# Code Generation (GitHub Copilot CLI Alternative)
llmswap generate "sort files by size in reverse order"
# Output: du -sh * | sort -hr

llmswap generate "Python function to read JSON with error handling" --language python
# Output: Complete Python function with try/catch blocks

# Advanced Log Analysis with AI
llmswap logs --analyze /var/log/app.log --since "2h ago"
llmswap logs --request-id REQ-12345 --correlate

# Code Review & Debugging
llmswap review app.py --focus security
llmswap debug --error "IndexError: list index out of range"
```

```python
# ❌ Problem: Vendor Lock-in
import openai  # Locked to OpenAI forever
client = openai.Client(api_key="sk-...")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
# To switch to Claude? Rewrite everything.

# ✅ Solution: llmswap SDK - Universal Interface
from llmswap import LLMClient

# Works with any provider you're subscribed to
client = LLMClient()  # Auto-detects from env vars
response = client.query("Hello")

# Want Claude instead? Just change provider:
client = LLMClient(provider="anthropic")  # That's it!

# Want to try Gemini? 
client = LLMClient(provider="gemini")  # Same code, different provider

# Built-in cost optimization:
# - Automatic response caching (50-90% savings)
# - Provider cost comparison
# - Smart provider selection based on query type
```

## 🆕 v5.1.0: Workspace System - Real-World Scenarios

### 🎯 **Scenario 1: New Developer Learning Flask**

**Problem:** Junior developer learning Flask keeps asking AI the same questions because AI forgets previous conversations.

**Solution with llmswap v5.1.0:**
```bash
cd ~/my-first-flask-app
llmswap workspace init --name "Learning Flask"

# Day 1: Learn about routing
llmswap chat --mentor professor
"How do Flask routes work?"
# AI explains. Learning auto-saved to learnings.md

# Day 2: Same workspace, AI remembers!
llmswap chat
"Can I use decorators for authentication?"
# AI response: "Building on what you learned about routes yesterday..."
# No need to re-explain basics!

# View your learning journey
llmswap workspace journal
# See: Day 1 - Routes, Day 2 - Authentication, etc.
```

**Result:** 60% faster learning because AI builds on previous knowledge instead of repeating basics.

---

### 🏢 **Scenario 2: Team Onboarding on Legacy Project**

**Problem:** New team member joins 2-year-old codebase. Spends weeks understanding architecture decisions.

**Solution with llmswap v5.1.0:**
```bash
cd ~/legacy-ecommerce-app
llmswap workspace init

# Edit context.md with project overview
llmswap workspace context
# Add: Tech stack, key components, known issues

# Ask questions - AI has full context
llmswap ask "Why did we choose MongoDB over PostgreSQL?" --mentor guru
# AI suggests checking decisions.md
# If documented: "According to your decision log from 2023-05..."
# If not: AI helps document it now

llmswap workspace decisions
# See all past architectural decisions in one place
```

**Result:** Onboarding time reduced from 3 weeks to 1 week.

---

### 💼 **Scenario 3: Freelancer Managing Multiple Projects**

**Problem:** Freelancer switches between 5 client projects daily. Context switching is exhausting.

**Solution with llmswap v5.1.0:**
```bash
# Morning: Client A's React project
cd ~/client-a-dashboard
llmswap chat
# AI loads: React patterns you learned, components built, state management decisions

# Afternoon: Client B's Python API
cd ~/client-b-api
llmswap chat
# AI switches context: Python best practices, API design decisions, database schema

# List all projects
llmswap workspace list
# See: 5 workspaces, each with independent context and learnings

# Each workspace has separate:
# - Learning journal (React patterns vs Python patterns)
# - Decision log (frontend vs backend decisions)
# - Project context (different tech stacks)
```

**Result:** Zero mental overhead for context switching. AI handles it automatically.

---

### 🎓 **Scenario 4: Learning Journey Across Technologies**

**Problem:** Developer learning full-stack wants to track progress across frontend, backend, DevOps.

**Solution with llmswap v5.1.0:**
```bash
# Frontend project
cd ~/react-app
llmswap workspace init --name "React Learning"
llmswap chat --mentor tutor
# Learn: Hooks, State, Components
# All auto-tracked in learnings.md

# Backend project
cd ~/python-api
llmswap workspace init --name "Python API"
llmswap chat --mentor tutor
# Learn: FastAPI, SQLAlchemy, Testing
# Separate learning journal

# View all learning across projects
llmswap workspace list
# See progress in each area

# Each workspace shows:
# - Total queries
# - Learnings count
# - Last accessed
```

**Result:** Complete visibility into learning journey across all technologies.

---

### 🚀 **Scenario 5: Open Source Contributor**

**Problem:** Contributing to 3 different OSS projects. Each has different conventions, patterns, testing approaches.

**Solution with llmswap v5.1.0:**
```bash
# Project 1: Django
cd ~/django-oss
llmswap workspace init
# Document in context.md: Coding style, PR process, testing patterns

# Project 2: FastAPI
cd ~/fastapi-oss
llmswap workspace init
# Different conventions, different patterns

# Ask project-specific questions
cd ~/django-oss
llmswap ask "How should I write tests here?"
# AI knows: This project uses pytest with Django TestCase

cd ~/fastapi-oss
llmswap ask "How should I write tests here?"
# AI knows: This project uses pytest with async fixtures

# Each workspace maintains separate:
# - Testing patterns learned
# - Code review feedback
# - Architecture understanding
```

**Result:** Contribute confidently to multiple projects without mixing up conventions.

---

## 💡 Real-World Use Cases (v5.0 Features)

### 📚 **Learning & Skill Development**
```bash
# Junior developer learning system design
llmswap chat --mentor professor --alias "Dr. Smith"
"Explain microservices architecture"
# Response adapts to teaching style with examples and deep explanations

# Career switcher exploring new domains
llmswap ask "What is Kubernetes?" --age 25 --audience "beginner"
# Age-appropriate explanation without assuming prior DevOps knowledge
```

### 🚀 **Professional Development**
```bash
# Get different perspectives on technical decisions
llmswap ask "Should I use MongoDB or PostgreSQL?" --mentor guru
# Wisdom-based response considering trade-offs and bigger picture

llmswap ask "Should I use MongoDB or PostgreSQL?" --mentor developer
# Practical engineering perspective with production experience
```

### 💼 **Team Collaboration**
```bash
# Explain technical concepts to non-technical stakeholders
llmswap ask "Explain our API architecture" --audience "business owner"
# Business-friendly explanation without jargon

# Onboard new team members
llmswap chat --mentor friend --alias "TeamBuddy"
# Collaborative, approachable learning environment
```

### 🎭 **Same Question, Different Perspectives**

Watch how the SAME question gets tailored responses based on your role:

```bash
# As a Developer: Implementation focus
llmswap ask "Explain Model Context Protocol (MCP)" --audience developer

Response: "MCP is a standardized protocol for connecting AI models to external 
data sources and tools. Unlike traditional chatbots that bundle everything into 
one monolithic system, MCP uses a client-server architecture:

- Server: Exposes tools, resources, and prompts via standard interface
- Client: Your AI application that consumes these capabilities
- Transport: JSON-RPC over stdio/HTTP

Key difference from older chatbots:
OLD: Hardcoded integrations, tight coupling, monolithic deployment
NEW: Pluggable architecture, loose coupling, independent tool servers

Code example:
from mcp import Server
server = Server("my-tools")
@server.tool()
def get_weather(city: str): ..."

---

# As an Architect: System design focus  
llmswap ask "Explain Model Context Protocol (MCP)" --audience architect

Response: "MCP introduces a service-oriented architecture for AI systems, 
addressing key architectural concerns:

**System Architecture:**
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ AI Client   │◄────►│ MCP Protocol │◄────►│ Tool Server │
│ (Claude App)│      │  (JSON-RPC)  │      │ (Resources) │
└─────────────┘      └──────────────┘      └─────────────┘

**Design Patterns:**
- Service Discovery: Dynamic capability negotiation
- Loose Coupling: Clients/servers evolve independently  
- Extensibility: Add new tools without modifying core
- Standardization: Uniform interface across tools

**vs Traditional Chatbots:**
- Monolithic → Microservices for AI tools
- Static → Dynamic capability loading
- Vendor lock-in → Provider-agnostic standard

**Scalability:** Deploy tool servers independently, horizontal scaling per service"

---

# As a Business Leader: ROI and strategy focus
llmswap ask "Explain Model Context Protocol (MCP)" --audience "business leader"

Response: "Model Context Protocol (MCP) is like moving from custom-built 
integrations to standardized APIs - but for AI systems.

**Business Impact:**

1. **Reduced Integration Costs**
   - OLD: $50K-$100K per custom AI integration
   - NEW: Plug-and-play tools, 80% cost reduction
   - Time to market: Weeks instead of months

2. **Vendor Independence**  
   - Not locked to one AI provider
   - Switch between Claude, GPT-4, Gemini seamlessly
   - Negotiating power with vendors

3. **Reusable Components**
   - Build once, use across multiple AI applications
   - Internal tools become valuable assets
   - Ecosystem of third-party MCP tools

4. **Competitive Advantage**
   - Deploy AI features 10x faster than competitors
   - Respond quickly to market changes
   - Lower total cost of ownership

**vs Traditional Chatbots:** Traditional bots were closed systems requiring 
custom development for each feature. MCP creates an open ecosystem where your 
team (or partners) can extend capabilities without vendor dependencies.

**ROI Example:** A company saved $200K in integration costs and reduced 
deployment time from 6 months to 3 weeks using MCP architecture."
```

**The Power:** Same command, same AI provider, completely different responses tailored to what each role needs to know.

## ⚠️ Privacy & Usage Disclaimers

**llmswap is an interface tool only** - all AI interactions and billing are handled directly by your chosen providers.

### 🔒 Context Privacy & Provider Switching
- **No context sharing**: When switching providers mid-conversation, NO conversation history is transferred between providers
- **Fresh start**: Each provider switch starts a completely new conversation thread
- **Legal compliance**: This protects your privacy and complies with provider Terms of Service
- **Your control**: You decide what each provider sees in their separate conversations

### 💰 Cost Information
**Cost estimates** (`~$X.XX estimated`) are approximate based on public pricing and common tokenizers. Actual costs may differ. **You are responsible for all provider costs and billing.**

**Legal Notice**: llmswap provides estimates and interface functionality for convenience only. We are not responsible for billing differences, provider charges, pricing changes, or data handling by individual providers. Always verify costs with your provider's billing dashboard.

## ⚡ Get Started in 30 Seconds

### 🍺 Homebrew (Recommended - macOS/Linux)
```bash
# Add our tap and install
brew tap llmswap/tap
brew install llmswap

# Ready to use immediately!
llmswap --help
```

### 🐍 PyPI (All platforms)
```bash
pip install llmswap
```

**Why Homebrew?** No virtualenv needed, global access, automatic dependency management, and easier updates.

## 🚀 Quick Start with Workspaces (v5.1.0)

### Complete Beginner's Guide - 3 Steps:

**Step 1: Install llmswap**
```bash
pip install llmswap
# or
brew install llmswap
```

**Step 2: Set up API key (one provider is enough)**
```bash
export ANTHROPIC_API_KEY="your-key-here"  # For Claude
# or
export OPENAI_API_KEY="your-key-here"     # For GPT-4
# or any other provider
```

**Step 3: Initialize workspace in your project**
```bash
cd ~/my-project
llmswap workspace init

# Start chatting - AI has full project context!
llmswap chat --mentor guru
# Ask anything about your project
# Learnings automatically tracked
# Decisions automatically documented

# View your learning journey
llmswap workspace journal
```

**That's it!** Your AI mentor now remembers everything about your project. 🎉

### Without Workspace (Classic Mode)
```bash
# Works exactly like v5.0 - no workspace needed
llmswap ask "How do I deploy a Flask app?"
llmswap chat --mentor tutor
llmswap generate "Python function to read CSV"
```

## 📋 Quick Reference - v5.1.0 Commands

### 🆕 Workspace Commands (NEW!)
| Command | Description | Example |
|---------|-------------|---------|
| `llmswap workspace init` | Initialize workspace in current directory | Creates `.llmswap/` with context, learnings, decisions |
| `llmswap workspace init --name` | Initialize with custom project name | `llmswap workspace init --name "My API"` |
| `llmswap workspace info` | Show current workspace statistics | Displays queries, learnings, decisions count |
| `llmswap workspace list` | List all registered workspaces | Shows all projects with llmswap workspaces |
| `llmswap workspace journal` | View learning journal | See everything you've learned |
| `llmswap workspace decisions` | View architecture decision log | See all technical decisions |
| `llmswap workspace context` | Edit project context | Opens context.md in default editor |

### Provider & Config Commands (v5.0)
| Command | Description | Example |
|---------|-------------|---------|
| `llmswap providers` | View all providers and their status | Shows configured/missing API keys |
| `llmswap config set provider.models.<provider> <model>` | Update default model for any provider | `llmswap config set provider.models.cohere command-r-plus-08-2024` |
| `llmswap config list` | View current configuration | Shows all settings and models |
| `/switch` (in chat) | Switch providers mid-conversation | Privacy-compliant provider switching |
| `/provider` (in chat) | Show current provider and available options | Quick status check |

### 🔧 First-Time Setup (v5.0.4 NEW!)
```bash
# First run automatically creates ~/.llmswap/config.yaml with defaults
llmswap ask "Hello world"
# Output: 🔧 Creating config file at ~/.llmswap/config.yaml
#         ✅ Default configuration created

# View all providers and their configuration status
llmswap providers

# Set up your API keys and start using
export ANTHROPIC_API_KEY="your-key-here"
llmswap ask "Explain Docker in simple terms"
```

**💡 Smart Defaults:** llmswap comes pre-configured with sensible model defaults for all 8 providers. No configuration needed to get started!

```python
from llmswap import LLMClient

# Works with any provider you have configured
client = LLMClient()  # Auto-detects from environment/config
response = client.query("Explain quantum computing in 50 words")
print(response.content)
```

## 🎯 Why llmswap v5.1.0 for AI Development?

| Feature | llmswap v5.1.0 | Claude Code | Cursor AI | Aider | LangChain | Direct APIs |
|---------|---------|-----------|---------|-----------|-------------|-------------|
| **Project Memory** | ✅ Workspace system | ❌ No memory | ❌ No memory | ❌ No memory | ❌ Manual | ❌ None |
| **Learning Journal** | ✅ Auto-tracked | ❌ Not available | ❌ Not available | ❌ Not available | ❌ Manual | ❌ None |
| **Context Awareness** | ✅ Project-specific | ❌ Generic | ❌ Generic | ❌ Generic | ❌ Manual | ❌ None |
| **AI Providers** | ✅ 8+ providers, instant switch | ❌ Claude only | ❌ Few providers | ❌ OpenAI only | ⚠️ 50+ complex setup | ❌ 1 per codebase |
| **Conversational Mode** | ✅ Provider-native, all | ✅ Claude only | ✅ Limited | ❌ Not available | ⚠️ Manual setup | ❌ Not available |
| **Memory Usage** | ✅ 99% reduction | ⚠️ Local storage | ⚠️ Local storage | ⚠️ Local storage | ❌ Heavy framework | ❌ Manual |
| **Configuration** | ✅ Git-like, shareable | ⚠️ Basic settings | ⚠️ Basic settings | ⚠️ Basic settings | ❌ Complex files | ❌ None |
| **Cost Analytics** | ✅ Real-time tracking | ❌ No cost info | ❌ No cost info | ❌ No cost info | ❌ External tools | ❌ Manual |
| **Provider Switching** | ✅ Mid-conversation | ❌ Locked to Claude | ⚠️ Limited | ❌ Locked to OpenAI | ❌ Restart required | ❌ New session |
| **Workspace System** | ✅ Per-project context | ❌ Not available | ❌ Not available | ❌ Not available | ❌ Not available | ❌ None |
| **CLI Commands** | ✅ 15+ powerful tools | ⚠️ Limited | ❌ IDE only | ⚠️ Limited | ❌ Separate packages | ❌ None |
| **SDK + CLI** | ✅ Both included | ❌ CLI only | ❌ IDE only | ❌ CLI only | ✅ SDK only | ⚠️ SDK only |
| **Teaching Personas** | ✅ 6 mentors | ❌ Not available | ❌ Not available | ❌ Not available | ❌ Not available | ❌ None |
| **Open Source** | ✅ 100% MIT licensed | ❌ Proprietary | ❌ Proprietary | ✅ Open source | ✅ Open source | ⚠️ Varies |

**Key Differentiators for v5.1.0:**
- 🧠 **Only AI tool with persistent project memory** - Never repeat context again
- 📚 **Automatic learning journals** - Track your progress without manual work
- 🎯 **Workspace-aware mentorship** - AI understands your specific project
- 🔄 **Zero context switching overhead** - Change projects, AI adapts automatically
- 💡 **Learning extraction** - AI summarizes key takeaways from conversations

## 🚀 Three Ways to Use llmswap:

**📚 1. Python Library/SDK**
```python
from llmswap import LLMClient
client = LLMClient()  # Import into any codebase
response = client.query("Analyze this data")
```

**⚡ 2. CLI Tools**  
```bash
llmswap generate "sort files by size"           # GitHub Copilot alternative
llmswap generate "Python function to read JSON" # Multi-language code generation
llmswap ask "Debug this error"                  # Terminal AI assistant
llmswap costs                                    # Cost optimization insights
```

**📊 3. Enterprise Analytics**
```python
stats = client.get_usage_stats()         # Track AI spend
comparison = client.get_provider_comparison()  # Compare costs
```

## 🎯 What's New in v5.1.0

### 🆕 Revolutionary Workspace & Memory Features
- **🧠 Workspace System**: Per-project memory with `.llmswap/` directories (inspired by `.git/`)
- **📚 Auto-Learning Journal**: AI automatically tracks what you learn in `learnings.md`
- **📖 Architecture Decision Log**: Document technical decisions in `decisions.md`
- **🎯 Context-Aware Mentorship**: AI mentor loads project context, past learnings, and decisions
- **🔍 Workspace Detection**: Automatically finds `.llmswap/` in current or parent directories
- **🗂️ Project Knowledge Base**: Editable `context.md` for project-specific information
- **📊 Workspace Statistics**: Track queries, learnings, and decisions per project
- **🌐 Global Workspace Registry**: Manage all workspaces from `~/.llmswap/workspaces/registry.json`
- **💡 Learning Extraction**: Uses fast AI (Groq) to extract key learnings from conversations
- **🔄 Workspace Switching**: Change directories, AI automatically loads different context

### Teaching & Conversational Features (v5.0)
- **🎓 Age-Appropriate AI**: First CLI with age-targeted explanations (`--age 10`, `--audience "teacher"`)
- **🧑‍🏫 Teaching Personas**: 6 AI mentors (teacher, developer, tutor, professor, mentor, buddy)
- **👤 Personalized Aliases**: Custom AI names (`--alias "Sarah"` for your personal tutor)
- **💬 Multi-Provider Chat**: Provider-native conversational mode with mid-chat switching
- **🧠 Zero Local Storage**: 99% memory reduction, all context at provider level
- **⚙️ Git-like Config**: Team-shareable configuration management
- **📊 Session Analytics**: Real-time cost and token tracking

## 🚀 Complete Feature Set

### 1️⃣ **Python SDK** - Multi-Provider Intelligence
```python
from llmswap import LLMClient

# Auto-detects available providers
client = LLMClient()  

# Or specify your preference
client = LLMClient(provider="anthropic")  # Claude 3 Opus/Sonnet/Haiku
client = LLMClient(provider="openai")     # GPT-4, GPT-3.5
client = LLMClient(provider="gemini")     # Google Gemini Pro/Flash
client = LLMClient(provider="watsonx")    # IBM watsonx.ai Granite
client = LLMClient(provider="ollama")     # Llama, Mistral, Phi, 100+ local
client = LLMClient(provider="groq")       # Groq ultra-fast inference
client = LLMClient(provider="cohere")     # Cohere Command models for RAG
client = LLMClient(provider="perplexity") # Perplexity web-connected AI

# Automatic failover
client = LLMClient(fallback=True)
response = client.query("Hello")  # Tries multiple providers

# Save 50-90% with intelligent caching
client = LLMClient(cache_enabled=True)
response1 = client.query("Expensive question")  # $$$ API call
response2 = client.query("Expensive question")  # FREE from cache

# 🆕 v5.1.0: Workspace-Aware SDK (Auto-detects .llmswap/)
from llmswap import LLMClient

# SDK automatically detects workspace in current directory
client = LLMClient()  # Loads workspace context if .llmswap/ exists

# Query with full project context
response = client.query("How should I structure my API?")
# AI has access to: project context, past learnings, architecture decisions

# Check if workspace is loaded
if client.workspace_manager:
    workspace_data = client.workspace_manager.load_workspace()
    print(f"Working in: {workspace_data['project_name']}")
    print(f"Learnings tracked: {workspace_data['statistics']['learnings_count']}")

# Learnings are automatically saved after each query
# No manual tracking needed!

# 🆕 v5.1.0: Eklavya Mentor Integration with Workspace
from llmswap import LLMClient
from llmswap.eklavya.mentor import EklavyaMentor

# Initialize client and mentor
client = LLMClient(provider="anthropic")
mentor = EklavyaMentor(persona="guru", alias="Guruji")

# Generate teaching system prompt with workspace context
teaching_prompt = mentor.generate_system_prompt()

# Use mentor for teaching-focused responses
response = client.query(
    "Explain Python decorators",
    system_prompt=teaching_prompt
)
print(response.content)  # Guru-style teaching response

# Different personas for different learning styles
coach = EklavyaMentor(persona="coach", alias="Coach Sarah")  # Motivational
friend = EklavyaMentor(persona="friend", alias="CodeBuddy")  # Collaborative
socrates = EklavyaMentor(persona="socrates")  # Question-based learning

# 🆕 v5.0: Conversational Sessions (Provider-Native)
client.start_chat_session()
response = client.chat("Tell me about Python")  # Context maintained
response = client.chat("What are its best features?")  # Remembers previous
client.end_chat_session()  # Clean provider-level cleanup

# 🆕 v5.0: Async Support for High Performance
import asyncio
from llmswap import AsyncLLMClient

async def main():
    async_client = AsyncLLMClient()
    response = await async_client.query_async("Process this data")
    
asyncio.run(main())
```

### 2️⃣ **CLI Suite** - 15+ Powerful Terminal Commands

#### 🆕 v5.1.0: Workspace Commands
```bash
# Initialize workspace in current project
llmswap workspace init
llmswap workspace init --name "My Flask App"

# View workspace information
llmswap workspace info                    # Current workspace stats
llmswap workspace list                    # All workspaces
llmswap workspace journal                 # View learning journal
llmswap workspace decisions               # View decision log
llmswap workspace context                 # Edit project context

# Workspace automatically detected when you run:
llmswap chat                              # Loads workspace context
llmswap ask "How do I test this?"         # Uses project-specific context
```

#### CLI Commands (All Features)
```bash
# 🆕 v5.0: Conversational Chat with Provider-Native Context
llmswap chat  # Interactive AI assistant with memory

# 🆕 v5.0: Configuration Management (Git-like)
llmswap config set provider.default anthropic
llmswap config export --file team-config.yaml

# Generate code from natural language (GitHub Copilot alternative)
llmswap generate "sort files by size in reverse order"
llmswap generate "Python function to read JSON file" --language python
llmswap generate "find large files over 100MB" --execute

# Ask one-line questions
llmswap ask "How to optimize PostgreSQL queries?"

# Interactive AI chat
llmswap chat

# AI code review
llmswap review app.py --focus security

# Debug errors instantly
llmswap debug --error "ConnectionTimeout at line 42"

# Analyze logs with AI
llmswap logs --analyze app.log --since "2h ago"
```

### 3️⃣ **Provider Management & Model Configuration** (v5.0.4 NEW!)

**🎯 View All Providers and Models:**
```bash
# Beautiful table showing all providers, their status, and default models
llmswap providers
```

**Output Example:**
```
🤖 llmswap Provider Status Report
============================================================
| Provider   | Default Model              | Status            | Issue                    |
|============|============================|===================|==========================| 
| ANTHROPIC  | claude-3-5-sonnet-20241022 | ✅ CONFIGURED     |                          |
| OPENAI     | gpt-4o                     | ❌ NOT CONFIGURED | OPENAI_API_KEY missing   |
| GEMINI     | gemini-1.5-pro             | ✅ CONFIGURED     |                          |
| COHERE     | command-r-plus-08-2024     | ❌ NOT CONFIGURED | COHERE_API_KEY missing   |
| PERPLEXITY | sonar-pro                  | ✅ CONFIGURED     |                          |
| WATSONX    | granite-13b-chat           | ✅ CONFIGURED     |                          |
| GROQ       | llama-3.3-70b-versatile    | ✅ CONFIGURED     |                          |
| OLLAMA     | llama3.1                   | ⚠️ NOT RUNNING   | Local server not running |

📊 Summary: 5/8 providers available
```

**🔧 Model Configuration:**
```bash
# Update any provider's default model
llmswap config set provider.models.openai gpt-4o-mini
llmswap config set provider.models.cohere command-r-plus-08-2024
llmswap config set provider.models.anthropic claude-3-5-haiku-20241022

# Set default provider
llmswap config set provider.default anthropic

# View current configuration
llmswap config list

# Export/import team configurations
llmswap config export team-config.yaml
llmswap config import team-config.yaml --merge
```

**🚀 Handle Model Deprecations:**
When providers deprecate models (like Cohere's `command-r-plus` → `command-r-plus-08-2024`):
```bash
# Simply update your config - no code changes needed!
llmswap config set provider.models.cohere command-r-plus-08-2024
llmswap providers  # Verify the change
```

**⚙️ Configuration File Location:**
- **User config:** `~/.llmswap/config.yaml` (created automatically on first run)
- **Custom location:** Set `LLMSWAP_CONFIG_HOME` environment variable
- **Team sharing:** Export/import YAML configs for team standardization

**💬 Interactive Chat Commands:**
```bash
llmswap chat  # Start interactive conversation

# Available commands in chat:
/help      # Show all commands
/provider  # Show current provider and available providers
/switch    # Switch to different provider (privacy-compliant)
/clear     # Clear conversation history
/stats     # Show session statistics
/quit      # Exit chat

# Example session:
[0] > Hello, I'm working on a Python project
[anthropic] Hi! I'd be happy to help with your Python project...

[1] > /switch
📋 Available providers: anthropic, gemini, perplexity, watsonx, groq
Enter provider name: gemini

🔒 PRIVACY NOTICE: Switching to gemini
   ✅ NO conversation history will be shared with the new provider
   ✅ This protects your privacy and complies with provider Terms of Service
Continue? (y/n): y

✅ Switched to gemini
💬 Starting fresh conversation with gemini
```

### 4️⃣ **Analytics & Cost Optimization** (v4.0 NEW!)
```bash
# Compare provider costs before choosing
llmswap compare --input-tokens 1000 --output-tokens 500
# Output: Gemini $0.0005 | OpenAI $0.014 | Claude $0.011

# Track your actual usage and spending
llmswap usage --days 30 --format table
# Shows: queries, tokens, costs by provider, response times

# Get AI spend optimization recommendations
llmswap costs
# Suggests: Switch to Gemini, enable caching, use Ollama for dev
```

```python
# Python SDK - Full analytics suite
client = LLMClient(analytics_enabled=True)

# Automatic conversation memory
response = client.chat("What is Python?")
response = client.chat("How is it different from Java?")  # Remembers context

# Real-time cost tracking
stats = client.get_usage_stats()
print(f"Total queries: {stats['totals']['queries']}")
print(f"Total cost: ${stats['totals']['cost']:.4f}")
print(f"Avg response time: {stats['avg_response_time_ms']}ms")

# Cost optimization insights
analysis = client.get_cost_breakdown()
print(f"Potential savings: ${analysis['optimization_opportunities']['potential_provider_savings']:.2f}")
print(f"Recommended provider: {analysis['recommendations'][0]}")

# Compare providers for your specific use case
comparison = client.get_provider_comparison(input_tokens=1500, output_tokens=500)
print(f"Cheapest: {comparison['cheapest']} (${comparison['cheapest_cost']:.6f})")
print(f"Savings vs current: {comparison['max_savings_percentage']:.1f}%")
```

### 4️⃣ **Advanced Features**

**Async/Streaming Support**
```python
import asyncio
from llmswap import AsyncLLMClient

async def main():
    client = AsyncLLMClient()
    
    # Async queries
    response = await client.query("Explain AI")
    
    # Streaming responses
    async for chunk in client.stream("Write a story"):
        print(chunk, end="")
```

**Multi-User Security**
```python
# Context-aware caching for multi-tenant apps
response = client.query(
    "Get user data",
    cache_context={"user_id": "user123"}  # Isolated cache
)
```

**Provider Comparison**
```python
# Compare responses from different models
comparison = client.compare_providers(
    "Solve this problem",
    providers=["anthropic", "openai", "gemini"]
)
```

## 📊 Real-World Use Cases & Examples

### 🏢 **Enterprise: Content Generation at Scale**
**Netflix-style recommendation descriptions for millions of items:**
```python
from llmswap import LLMClient

# Start with OpenAI, switch to Gemini for 96% cost savings
client = LLMClient(provider="gemini", cache_enabled=True)

def generate_descriptions(items):
    for item in items:
        # Cached responses save 90% on similar content
        description = client.query(
            f"Create engaging description for {item['title']}",
            cache_context={"category": item['category']}
        )
        yield description.content

# Cost: $0.0005 per description vs $0.015 with OpenAI
```

### 👨‍💻 **Developers: AI-Powered Code Review**
**GitHub Copilot alternative for your team:**
```python
# CLI for instant code review
$ llmswap review api_handler.py --focus security

# Python SDK for CI/CD integration
from llmswap import LLMClient

client = LLMClient(analytics_enabled=True)
review = client.query(f"Review this PR for bugs: {pr_diff}")

# Track costs across your team
stats = client.get_usage_stats()
print(f"This month's AI costs: ${stats['totals']['cost']:.2f}")
```

### 🎓 **Education: AI Tutoring Platform**
**Khan Academy-style personalized learning:**
```python
client = LLMClient(provider="ollama")  # Free for schools!

def ai_tutor(student_question, subject):
    # Use watsonx for STEM, Ollama for general subjects
    if subject in ["math", "science"]:
        client.set_provider("watsonx")
    
    response = client.query(
        f"Explain {student_question} for a {subject} student",
        cache_context={"grade_level": student.grade}
    )
    return response.content

# Zero cost with Ollama, enterprise-grade with watsonx
```

### 🚀 **Startups: Multi-Modal Customer Support**
**Shopify-scale merchant assistance:**
```python
from llmswap import LLMClient

# Start with Anthropic, fallback to others if rate-limited
client = LLMClient(fallback=True, cache_enabled=True)

async def handle_support_ticket(ticket):
    # 90% of questions are similar - cache saves thousands
    response = await client.aquery(
        f"Help with: {ticket.issue}",
        cache_context={"type": ticket.category}
    )
    
    # Auto-escalate complex issues
    if response.confidence < 0.8:
        client.set_provider("anthropic")  # Use best model
        response = await client.aquery(ticket.issue)
    
    return response.content
```

### 📱 **Content Creators: Writing Assistant**
**Medium/Substack article generation:**
```bash
# Quick blog post ideas
llmswap ask "10 trending topics in AI for developers"

# Full article draft
llmswap chat
> Write a 1000-word article on prompt engineering
> Make it more technical
> Add code examples
```

### 🔧 **DevOps Engineers: Infrastructure as Code**
**Kubernetes and Docker automation:**
```bash
# Generate Kubernetes deployment
llmswap generate "Kubernetes deployment for React app with 3 replicas" --save k8s-deploy.yaml

# Docker multi-stage build
llmswap generate "Docker multi-stage build for Node.js app with Alpine" --language dockerfile

# Terraform AWS infrastructure
llmswap generate "Terraform script for AWS VPC with public/private subnets" --save main.tf
```

### 🎯 **Data Scientists: Analysis Workflows**
**Pandas, visualization, and ML pipeline generation:**
```bash
# Data analysis scripts
llmswap generate "Pandas script to clean CSV and handle missing values" --language python

# Visualization code
llmswap generate "Matplotlib script for correlation heatmap" --save plot.py

# ML pipeline
llmswap generate "scikit-learn pipeline for text classification with TF-IDF" --language python
```

### 💬 **App Developers: Full Applications**
**Complete app generation with modern frameworks:**
```bash
# Streamlit chatbot
llmswap generate "Streamlit chatbot app with session state and file upload" --save chatbot.py

# FastAPI REST API
llmswap generate "FastAPI app with CRUD operations for user management" --save api.py

# React component
llmswap generate "React component for data table with sorting and filtering" --language javascript --save DataTable.jsx
```

### 🤖 **AI/ML Engineers: Model Deployment**
**Production-ready ML workflows and deployments:**
```bash
# LangChain RAG pipeline
llmswap generate "LangChain RAG system with ChromaDB and OpenAI embeddings" --language python --save rag_pipeline.py

# Hugging Face model fine-tuning
llmswap generate "Script to fine-tune BERT for sentiment analysis with Hugging Face" --save finetune.py

# Gradio ML demo app
llmswap generate "Gradio app for image classification with drag and drop" --save demo.py

# Vector database setup
llmswap generate "Pinecone vector database setup for semantic search" --language python
```

### 🔒 **Security Engineers: Vulnerability Scanning**  
**Security automation and compliance scripts:**
```bash
# Security audit script
llmswap generate "Python script to scan for exposed API keys in codebase" --save security_scan.py

# OAuth2 implementation
llmswap generate "FastAPI OAuth2 with JWT tokens implementation" --language python

# Rate limiting middleware
llmswap generate "Redis-based rate limiting for Express.js" --language javascript
```

### 🛠️ **AI Agent Development: Tool Creation**
**Build tools and functions for AI agents (inspired by Anthropic's writing tools):**
```bash
# Create tool functions for agents
llmswap generate "Python function for web scraping with BeautifulSoup error handling" --save tools/scraper.py

# Database interaction tools
llmswap generate "SQLAlchemy functions for CRUD operations with type hints" --save tools/database.py

# File manipulation utilities
llmswap generate "Python class for safe file operations with context managers" --save tools/file_ops.py

# API integration tools
llmswap generate "Async Python functions for parallel API calls with rate limiting" --save tools/api_client.py

# Agent orchestration
llmswap generate "LangChain agent with custom tools for research tasks" --language python
```

### 🏆 **Hackathon Power Kit: Win Your Next Hackathon**
**Build complete MVPs in minutes, not hours:**
```bash
# RAG Chatbot for Document Q&A (Most requested hackathon project)
llmswap generate "Complete RAG chatbot with OpenAI embeddings, Pinecone vector store, and Streamlit UI for PDF document Q&A" --save rag_chatbot.py

# Full-Stack SaaS Starter (0 to production in 5 minutes)
llmswap generate "Next.js 14 app with Clerk auth, Stripe payments, Prisma ORM, and PostgreSQL schema for SaaS platform" --save saas_mvp.js
```

## 🛠️ Installation & Setup

```bash
# Install package
pip install llmswap

# Set any API key (one is enough to get started)
export ANTHROPIC_API_KEY="sk-..."       # For Claude
export OPENAI_API_KEY="sk-..."          # For GPT-4
export GEMINI_API_KEY="..."             # For Google Gemini
export WATSONX_API_KEY="..."            # For IBM watsonx
export WATSONX_PROJECT_ID="..."         # watsonx project
export GROQ_API_KEY="gsk_..."           # For Groq ultra-fast inference
export COHERE_API_KEY="co_..."            # For Cohere Command models
export PERPLEXITY_API_KEY="pplx-..."      # For Perplexity web search
# Or run Ollama locally for 100% free usage
```

## 📈 Token Usage Guidelines

| Task Type | Input Tokens | Output Tokens | Estimated Cost |
|-----------|--------------|---------------|----------------|
| Simple Q&A | 100 | 50 | ~$0.001 |
| Code Review | 1000 | 300 | ~$0.010 |
| Document Analysis | 3000 | 800 | ~$0.025 |
| Creative Writing | 500 | 2000 | ~$0.020 |

## 🔗 Quick Links

- **GitHub**: [github.com/sreenathmmenon/llmswap](https://github.com/sreenathmmenon/llmswap)
- **Documentation**: [Full API Reference](https://github.com/sreenathmmenon/llmswap#readme)
- **PyPI**: [pypi.org/project/llmswap](https://pypi.org/project/llmswap)
- **Issues**: [Report bugs or request features](https://github.com/sreenathmmenon/llmswap/issues)

## 🚀 Get Started Now

```bash
pip install llmswap
```

```python
from llmswap import LLMClient
client = LLMClient()
print(client.query("Hello, AI!").content)
```

**That's it!** You're now using AI with automatic provider detection, failover support, and cost optimization.

---

## 🔍 Keywords & SEO

**AI Development Tools:** AI mentor, AI assistant, AI CLI, AI SDK, machine learning tools, LLM orchestration, AI development platform

**Project Memory & Context:** project memory AI, context-aware AI, workspace AI, learning journal AI, AI that remembers, persistent AI context, project-specific AI

**Multi-Provider AI:** multi-provider LLM, AI provider switching, vendor-agnostic AI, universal AI SDK, provider-independent AI, LLM abstraction layer

**AI Learning & Mentorship:** AI mentor, AI tutor, AI teacher, personalized AI learning, AI coaching, teaching personas, Eklavya AI mentor, AI learning journey

**Developer Productivity:** developer AI tools, coding AI assistant, AI for developers, programming AI mentor, software development AI, AI code helper

**Python SDK & CLI:** Python AI SDK, AI CLI tool, terminal AI assistant, command-line AI, Python LLM library, AI development kit

**Cost Optimization:** AI cost tracking, LLM cost optimization, AI analytics, provider cost comparison, AI usage statistics

**Competitors:** Claude Code alternative, Cursor AI alternative, GitHub Copilot alternative, ChatGPT alternative, Aider alternative, Continue.dev alternative

**Technical Keywords:** LangChain alternative, OpenAI SDK alternative, Anthropic SDK alternative, multi-LLM framework, AI orchestration platform, LLM wrapper

**Use Cases:** AI for learning, AI for education, AI for freelancers, AI for teams, AI onboarding tool, AI documentation, AI architecture decisions

---

## 🌐 Links & Resources

- **Website:** [llmswap.org](https://llmswap.org)
- **Documentation:** [llmswap.org/docs](https://llmswap.org/docs)
- **CLI Reference:** [llmswap.org/docs/cli.html](https://llmswap.org/docs/cli.html)
- **SDK Guide:** [llmswap.org/docs/sdk.html](https://llmswap.org/docs/sdk.html)
- **GitHub Repository:** [github.com/sreenathmmenon/llmswap](https://github.com/sreenathmmenon/llmswap)
- **PyPI Package:** [pypi.org/project/llmswap](https://pypi.org/project/llmswap)
- **Homebrew Tap:** [github.com/llmswap/homebrew-tap](https://github.com/llmswap/homebrew-tap)
- **Issues & Support:** [github.com/sreenathmmenon/llmswap/issues](https://github.com/sreenathmmenon/llmswap/issues)
- **Twitter/X:** [@llmswap](https://twitter.com/llmswap)

---

## 📊 Stats & Achievements

- **Downloads:** 12,000+ on PyPI
- **Version:** v5.1.0 (latest)
- **License:** MIT (100% open source)
- **Python Support:** 3.8+
- **Providers Supported:** 8+ (Anthropic, OpenAI, Google, IBM, Groq, Cohere, Perplexity, Ollama)
- **Installation:** pip, Homebrew, or from source
- **Active Development:** Regular updates and feature releases

---

Built with ❤️ for developers who value simplicity, efficiency, and learning. Star us on [GitHub](https://github.com/sreenathmmenon/llmswap) if llmswap saves you time, money, or helps you learn faster!

**v5.1.0 Release:** The first AI tool that truly remembers your learning journey. 🚀