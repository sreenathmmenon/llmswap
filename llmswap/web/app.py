"""
LLMSwap Web UI - Flask Application

Provides HTTP server, routes, and HTML interface for model comparison.
All code is original - no copied snippets from external sources.

Copyright (c) 2025 Sreenath M Menon
Licensed under the MIT License
"""

import os
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, Response
from flask_cors import CORS

from .comparison import compare_models, compare_models_streaming
from .workspace_integration import (
    save_comparison,
    list_workspaces,
    get_workspace,
    get_workspace_stats,
)


def create_app(testing=False):
    """
    Create and configure Flask app.

    Args:
        testing: If True, configure for testing

    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    app.config["TESTING"] = testing

    # Enable CORS
    CORS(app)

    # Get template path
    template_path = Path(__file__).parent / "templates" / "index.html"

    # Read template
    if template_path.exists():
        with open(template_path, "r") as f:
            INDEX_HTML = f.read()
    else:
        # Inline template as fallback
        INDEX_HTML = get_inline_template()

    @app.route("/")
    def index():
        """Serve main page"""
        return render_template_string(INDEX_HTML)

    @app.route("/health")
    def health():
        """Health check endpoint"""
        return jsonify({"status": "ok"})

    @app.route("/compare", methods=["POST"])
    def compare():
        """
        Compare models endpoint.

        Expects JSON:
        {
            "prompt": "...",
            "models": ["model1", "model2"]
        }

        Returns SSE stream or JSON with results
        """
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        prompt = data.get("prompt", "").strip()
        models = data.get("models", [])

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        if not models or len(models) == 0:
            return jsonify({"error": "At least one model is required"}), 400

        try:
            # Check if streaming is requested
            accept_header = request.headers.get("Accept", "")

            if "text/event-stream" in accept_header:
                # Streaming response
                return Response(
                    stream_comparison(prompt, models), mimetype="text/event-stream"
                )
            else:
                # Regular JSON response
                from llmswap import LLMClient

                client = LLMClient()
                results = compare_models(prompt, models, client)

                return jsonify(
                    {
                        "prompt": prompt,
                        "timestamp": datetime.now().isoformat(),
                        "results": results,
                    }
                )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/workspaces", methods=["GET"])
    def get_workspaces():
        """Get list of available workspaces"""
        try:
            workspaces = list_workspaces()
            return jsonify(workspaces)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/provider-status", methods=["GET"])
    def provider_status():
        """Get configured provider status"""
        import os

        providers = {
            "OpenAI": {
                "key": "OPENAI_API_KEY",
                "models": ["gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"],
            },
            "Anthropic": {
                "key": "ANTHROPIC_API_KEY",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            },
            "Google": {
                "key": "GEMINI_API_KEY",
                "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro"],
            },
            "xAI": {"key": "XAI_API_KEY", "models": ["grok-beta"]},
            "Groq": {"key": "GROQ_API_KEY", "models": ["llama-3.3-70b-versatile"]},
            "Perplexity": {"key": "PERPLEXITY_API_KEY", "models": ["sonar-pro"]},
            "Cohere": {"key": "COHERE_API_KEY", "models": ["command-r-plus-08-2024"]},
        }

        status = []
        for name, info in providers.items():
            configured = os.getenv(info["key"]) is not None
            status.append(
                {
                    "provider": name,
                    "configured": configured,
                    "models": info["models"],
                    "env_var": info["key"],
                }
            )

        # Return as HTML for easy viewing
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Provider Status - LLMSwap</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50 p-8">
            <div class="max-w-4xl mx-auto">
                <h1 class="text-3xl font-bold mb-6">Provider Status</h1>
                <div class="bg-white rounded-lg shadow-sm overflow-hidden">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Models Available</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Setup</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
        """

        for item in status:
            status_icon = "✅" if item["configured"] else "❌"
            status_text = "Configured" if item["configured"] else "Not Configured"
            status_color = "text-green-600" if item["configured"] else "text-red-600"

            html += f"""
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap font-medium">{item['provider']}</td>
                                <td class="px-6 py-4 whitespace-nowrap {status_color}">{status_icon} {status_text}</td>
                                <td class="px-6 py-4 text-sm text-gray-600">{', '.join(item['models'][:2])}</td>
                                <td class="px-6 py-4 text-sm">
                                    <code class="bg-gray-100 px-2 py-1 rounded text-xs">export {item['env_var']}="..."</code>
                                </td>
                            </tr>
            """

        html += """
                        </tbody>
                    </table>
                </div>
                <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 class="font-semibold text-blue-900 mb-2">💡 Quick Setup</h3>
                    <p class="text-sm text-blue-800">Add API keys to your environment, then restart the web UI:</p>
                    <pre class="mt-2 text-xs bg-blue-100 p-2 rounded overflow-x-auto">export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
llmswap web</pre>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    @app.route("/api/save-comparison", methods=["POST"])
    def save_comparison_route():
        """Save comparison results to workspace"""
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        workspace_name = data.get("workspace")
        prompt = data.get("prompt")
        results = data.get("results", [])

        if not workspace_name:
            return jsonify({"error": "Workspace name is required"}), 400

        try:
            workspace = get_workspace(workspace_name)

            if not workspace:
                return jsonify({"error": "Workspace not found"}), 404

            # Save comparison
            saved_path = save_comparison(workspace, data)

            return jsonify({"success": True, "path": saved_path}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/models", methods=["GET"])
    def get_models():
        """Get available models from dynamic system"""
        try:
            from .models import get_available_models, get_featured_models

            all_models = get_available_models()
            featured = get_featured_models()

            return jsonify({"models": all_models, "featured": featured})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


def stream_comparison(prompt: str, models: list):
    """
    Stream comparison results as Server-Sent Events.

    Streams token-by-token updates for real-time side-by-side comparison.

    Yields:
        SSE formatted events with model updates
    """
    from llmswap import LLMClient
    from .comparison import detect_winner

    client = LLMClient()
    all_results = []

    for update in compare_models_streaming(prompt, models, client):
        # Send each update immediately
        event_data = json.dumps(update)
        yield f"data: {event_data}\n\n"

        # Track completed results for winner detection
        if update.get("done") and not update.get("error"):
            all_results.append(update)

    # After all models complete, detect winner
    if all_results:
        winner_info = detect_winner(all_results)
        yield f"data: {json.dumps({'event': 'winner', 'data': winner_info})}\n\n"

    # Send completion event
    yield f"data: {json.dumps({'event': 'complete'})}\n\n"


def get_inline_template():
    """
    Return inline HTML template as fallback.

    Returns:
        HTML template string
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLMSwap - Model Comparison</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <!-- Syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        /* Markdown styles */
        .markdown-content h1 { font-size: 1.875rem; font-weight: bold; margin-top: 1.5rem; margin-bottom: 1rem; }
        .markdown-content h2 { font-size: 1.5rem; font-weight: bold; margin-top: 1.25rem; margin-bottom: 0.75rem; }
        .markdown-content h3 { font-size: 1.25rem; font-weight: bold; margin-top: 1rem; margin-bottom: 0.5rem; }
        .markdown-content p { margin-bottom: 1rem; line-height: 1.625; }
        .markdown-content ul, .markdown-content ol { margin-left: 1.5rem; margin-bottom: 1rem; }
        .markdown-content li { margin-bottom: 0.5rem; }
        .markdown-content code { background-color: #f3f4f6; padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-size: 0.875rem; }
        .markdown-content pre { background-color: #f6f8fa; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-bottom: 1rem; position: relative; }
        .markdown-content pre code { background-color: transparent; padding: 0; }
        .markdown-content strong { font-weight: 600; }
        .markdown-content blockquote { border-left: 4px solid #e5e7eb; padding-left: 1rem; color: #6b7280; margin-bottom: 1rem; }
        /* Code block copy button */
        .code-copy-btn {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: #374151;
            color: white;
            border: none;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s;
        }
        .markdown-content pre:hover .code-copy-btn { opacity: 1; }
        .code-copy-btn:hover { background: #1f2937; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-7xl">
        <header class="mb-8">
            <div class="flex justify-between items-start">
                <div>
                    <h1 class="text-4xl font-bold text-gray-900">LLMSwap</h1>
                    <p class="text-gray-600 mt-2">Compare AI models side-by-side</p>
                </div>
                <a href="/api/provider-status" target="_blank" class="text-sm text-blue-600 hover:text-blue-800">
                    View Provider Status
                </a>
            </div>
        </header>

        <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <form id="compareForm">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Prompt
                        <span class="text-xs text-gray-500 font-normal ml-2">
                            💡 Supports code, markdown, and multi-line input
                        </span>
                    </label>
                    <textarea
                        id="prompt"
                        name="prompt"
                        rows="8"
                        class="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                        placeholder="Enter your prompt here...

Examples:
• Explain this code: [paste code]
• Write a function that...
• Compare approaches to...
• Debug this error: [paste error]"
                        required
                    ></textarea>
                    <div class="flex justify-between items-center mt-2">
                        <div class="text-xs text-gray-500" id="charCount">0 characters</div>
                        <button type="button" onclick="clearPrompt()"
                                class="text-xs text-gray-500 hover:text-gray-700">
                            Clear
                        </button>
                    </div>
                </div>

                <div class="mb-4">
                    <div class="flex justify-between items-center mb-2">
                        <label class="text-sm font-medium text-gray-700">
                            Select Models <span id="selectedCount" class="text-gray-500 font-normal">(0 selected)</span>
                        </label>
                        <button type="button" onclick="clearModels()"
                                class="text-sm text-gray-500 hover:text-gray-700 hover:underline">
                            Clear All
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        <!-- OpenAI -->
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="gpt-4" class="mr-2">
                            <div>
                                <div class="font-medium">GPT-4</div>
                                <div class="text-xs text-gray-500">OpenAI</div>
                            </div>
                        </label>
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="gpt-4o-mini" class="mr-2">
                            <div>
                                <div class="font-medium">GPT-4o Mini</div>
                                <div class="text-xs text-gray-500">OpenAI • Fast & Cheap</div>
                            </div>
                        </label>

                        <!-- Anthropic -->
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="claude-3-5-sonnet-20241022" class="mr-2">
                            <div>
                                <div class="font-medium">Claude Sonnet 4.5</div>
                                <div class="text-xs text-gray-500">Anthropic • Best Coding</div>
                            </div>
                        </label>
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="claude-3-5-haiku-20241022" class="mr-2">
                            <div>
                                <div class="font-medium">Claude Haiku</div>
                                <div class="text-xs text-gray-500">Anthropic • Fast</div>
                            </div>
                        </label>

                        <!-- Google -->
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="gemini-2.0-flash-exp" class="mr-2">
                            <div>
                                <div class="font-medium">Gemini 2.0 Flash</div>
                                <div class="text-xs text-gray-500">Google • Experimental</div>
                            </div>
                        </label>
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="gemini-1.5-pro" class="mr-2">
                            <div>
                                <div class="font-medium">Gemini 1.5 Pro</div>
                                <div class="text-xs text-gray-500">Google</div>
                            </div>
                        </label>

                        <!-- xAI -->
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="grok-beta" class="mr-2">
                            <div>
                                <div class="font-medium">Grok Beta</div>
                                <div class="text-xs text-gray-500">xAI</div>
                            </div>
                        </label>

                        <!-- Groq -->
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="llama-3.3-70b-versatile" class="mr-2">
                            <div>
                                <div class="font-medium">Llama 3.3 70B</div>
                                <div class="text-xs text-gray-500">Groq • Ultra Fast</div>
                            </div>
                        </label>

                        <!-- Perplexity -->
                        <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                            <input type="checkbox" name="models" value="sonar-pro" class="mr-2">
                            <div>
                                <div class="font-medium">Sonar Pro</div>
                                <div class="text-xs text-gray-500">Perplexity • Search-Enhanced</div>
                            </div>
                        </label>
                    </div>

                    <!-- More Models (hidden by default) -->
                    <div id="moreModels" class="hidden mt-3">
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            <!-- More OpenAI -->
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="gpt-4o" class="mr-2">
                                <div>
                                    <div class="font-medium">GPT-4o</div>
                                    <div class="text-xs text-gray-500">OpenAI • Fast & Smart</div>
                                </div>
                            </label>
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="o1-preview" class="mr-2">
                                <div>
                                    <div class="font-medium">o1 Preview</div>
                                    <div class="text-xs text-gray-500">OpenAI • Reasoning</div>
                                </div>
                            </label>
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="o1-mini" class="mr-2">
                                <div>
                                    <div class="font-medium">o1 Mini</div>
                                    <div class="text-xs text-gray-500">OpenAI • Fast Reasoning</div>
                                </div>
                            </label>

                            <!-- More Anthropic -->
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="claude-3-opus-20240229" class="mr-2">
                                <div>
                                    <div class="font-medium">Claude Opus</div>
                                    <div class="text-xs text-gray-500">Anthropic • Best Quality</div>
                                </div>
                            </label>

                            <!-- More Google -->
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="gemini-1.5-flash" class="mr-2">
                                <div>
                                    <div class="font-medium">Gemini 1.5 Flash</div>
                                    <div class="text-xs text-gray-500">Google • Fast</div>
                                </div>
                            </label>
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="gemini-1.0-pro" class="mr-2">
                                <div>
                                    <div class="font-medium">Gemini Pro</div>
                                    <div class="text-xs text-gray-500">Google • Legacy</div>
                                </div>
                            </label>

                            <!-- More Groq -->
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="llama-3.1-8b-instant" class="mr-2">
                                <div>
                                    <div class="font-medium">Llama 3.1 8B</div>
                                    <div class="text-xs text-gray-500">Groq • Fastest</div>
                                </div>
                            </label>
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="mixtral-8x7b-32768" class="mr-2">
                                <div>
                                    <div class="font-medium">Mixtral 8x7B</div>
                                    <div class="text-xs text-gray-500">Groq • Balanced</div>
                                </div>
                            </label>

                            <!-- More Perplexity -->
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="sonar" class="mr-2">
                                <div>
                                    <div class="font-medium">Sonar</div>
                                    <div class="text-xs text-gray-500">Perplexity • Standard</div>
                                </div>
                            </label>

                            <!-- Ollama (local) -->
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="llama3.3" class="mr-2">
                                <div>
                                    <div class="font-medium">Llama 3.3 (Local)</div>
                                    <div class="text-xs text-gray-500">Ollama • Free</div>
                                </div>
                            </label>
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="mistral" class="mr-2">
                                <div>
                                    <div class="font-medium">Mistral (Local)</div>
                                    <div class="text-xs text-gray-500">Ollama • Free</div>
                                </div>
                            </label>

                            <!-- Sarvam AI (Indian) -->
                            <label class="flex items-center p-2 border rounded hover:bg-gray-50">
                                <input type="checkbox" name="models" value="sarvam-2b" class="mr-2">
                                <div>
                                    <div class="font-medium">Sarvam 2B</div>
                                    <div class="text-xs text-gray-500">Sarvam AI • Indian Model</div>
                                </div>
                            </label>
                        </div>
                    </div>

                    <!-- Expand/Collapse Button -->
                    <div class="mt-3 text-center">
                        <button type="button" id="moreBtn" onclick="toggleMoreModels()"
                                class="text-sm text-blue-600 hover:text-blue-800 hover:underline">
                            + 12 more models
                        </button>
                    </div>
                </div>

                <button
                    type="submit"
                    class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
                >
                    Compare Models
                </button>
            </form>
        </div>

        <div id="loading" class="hidden text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-gray-600">Comparing models...</p>
        </div>

        <!-- Summary Stats (shows after first result) -->
        <div id="summary" class="hidden bg-white rounded-lg shadow-sm p-6 mb-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <h3 class="text-sm font-medium text-gray-500 mb-2">⚡ Speed Ranking</h3>
                    <div id="speedRanking" class="text-sm"></div>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500 mb-2">💰 Cost Comparison</h3>
                    <div id="costChart" class="text-sm"></div>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500 mb-2">📊 Stats</h3>
                    <div id="overallStats" class="text-sm"></div>
                </div>
            </div>
        </div>

        <!-- Results (vertical list) -->
        <div id="results" class="space-y-4"></div>
    </div>

    <script>
        const form = document.getElementById('compareForm');
        const resultsDiv = document.getElementById('results');
        const loading = document.getElementById('loading');
        const summary = document.getElementById('summary');
        const promptTextarea = document.getElementById('prompt');
        const charCount = document.getElementById('charCount');

        let allResults = [];
        let completedCount = 0;
        const responseTexts = {}; // Store raw response text for copying

        // Character counter
        promptTextarea.addEventListener('input', () => {
            const length = promptTextarea.value.length;
            charCount.textContent = `${length} character${length !== 1 ? 's' : ''}`;
        });

        // Clear prompt function
        function clearPrompt() {
            promptTextarea.value = '';
            charCount.textContent = '0 characters';
            promptTextarea.focus();
        }

        // Clear all selected models
        function clearModels() {
            document.querySelectorAll('input[name="models"]').forEach(cb => cb.checked = false);
            updateSelectedCount();
        }

        // Update selected count and button state
        function updateSelectedCount() {
            const count = document.querySelectorAll('input[name="models"]:checked').length;
            const selectedCountSpan = document.getElementById('selectedCount');
            const submitBtn = document.querySelector('button[type="submit"]');

            // Update count text
            selectedCountSpan.textContent = `(${count} selected)`;

            // Enable/disable submit button
            if (count === 0) {
                submitBtn.disabled = true;
                submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                submitBtn.disabled = false;
                submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        }

        // Load saved preferences from localStorage
        function loadPreferences() {
            try {
                const savedModels = localStorage.getItem('llmswap_selected_models');
                if (savedModels) {
                    const models = JSON.parse(savedModels);
                    models.forEach(model => {
                        const checkbox = document.querySelector(`input[value="${model}"]`);
                        if (checkbox) checkbox.checked = true;
                    });

                    // Show welcome back message
                    if (models.length > 0) {
                        showToast(`👋 Welcome back! Restored your ${models.length} favorite model${models.length !== 1 ? 's' : ''}`);
                    }
                }
            } catch (e) {
                console.log('localStorage not available or error loading preferences');
            }
        }

        // Save preferences to localStorage
        function savePreferences() {
            try {
                const selectedModels = Array.from(document.querySelectorAll('input[name="models"]:checked'))
                    .map(cb => cb.value);
                localStorage.setItem('llmswap_selected_models', JSON.stringify(selectedModels));
            } catch (e) {
                console.log('localStorage not available or error saving preferences');
            }
        }

        // Show toast notification
        function showToast(message, duration = 3000) {
            const toast = document.createElement('div');
            toast.className = 'fixed bottom-4 right-4 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), duration);
        }

        // Listen to checkbox changes
        document.addEventListener('DOMContentLoaded', () => {
            // Load saved preferences first
            loadPreferences();

            // Show first-time tip
            const isFirstTime = !localStorage.getItem('llmswap_has_used');
            if (isFirstTime) {
                setTimeout(() => {
                    showToast('💡 Tip: Select 2-4 models to see side-by-side comparisons', 5000);
                    localStorage.setItem('llmswap_has_used', 'true');
                }, 1000); // Delay so it doesn't conflict with welcome back message
            }

            // Attach change listeners
            document.querySelectorAll('input[name="models"]').forEach(cb => {
                cb.addEventListener('change', () => {
                    updateSelectedCount();
                    savePreferences(); // Save on every change
                });
            });
            updateSelectedCount(); // Initialize count
        });

        // Toggle more models
        function toggleMoreModels() {
            const moreDiv = document.getElementById('moreModels');
            const moreBtn = document.getElementById('moreBtn');
            const isHidden = moreDiv.classList.contains('hidden');

            if (isHidden) {
                moreDiv.classList.remove('hidden');
                moreBtn.textContent = '− Hide extra models';

                // Attach change listeners to newly revealed checkboxes
                moreDiv.querySelectorAll('input[name="models"]').forEach(cb => {
                    cb.addEventListener('change', updateSelectedCount);
                });
            } else {
                moreDiv.classList.add('hidden');
                moreBtn.textContent = '+ 12 more models';
            }
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const prompt = document.getElementById('prompt').value;
            const selectedModels = Array.from(document.querySelectorAll('input[name="models"]:checked'))
                .map(cb => cb.value);

            if (selectedModels.length === 0) {
                showToast('💡 Please select at least one model to compare', 3000);
                // Highlight the model selection area
                const modelSection = document.querySelector('input[name="models"]').closest('.mb-4');
                modelSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }

            // Reset state
            resultsDiv.innerHTML = '';
            summary.classList.add('hidden');
            loading.classList.remove('hidden');
            allResults = [];
            completedCount = 0;

            // Create placeholder cards immediately
            selectedModels.forEach(model => createPlaceholderCard(model));

            // Query all models concurrently (live updates!)
            const promises = selectedModels.map(model => queryModel(prompt, model));

            try {
                await Promise.all(promises);
                loading.classList.add('hidden');
            } catch (error) {
                loading.classList.add('hidden');
                console.error('Comparison error:', error);
            }
        });

        function createPlaceholderCard(model) {
            const card = document.createElement('div');
            card.id = `card-${model}`;
            card.className = 'bg-white rounded-lg shadow-sm p-6 border-2 border-gray-100';

            card.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900">${model}</h3>
                        <div class="text-sm text-gray-500 mt-1" id="badge-${model}"></div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm text-gray-500" id="time-${model}">⏳ Waiting...</div>
                        <div class="text-xs text-gray-400 mt-1" id="cost-${model}"></div>
                    </div>
                </div>
                <div class="flex items-center justify-center py-8" id="spinner-${model}">
                    <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                </div>
                <div class="hidden" id="content-${model}">
                    <div class="markdown-content text-gray-700 mb-4" id="response-${model}"></div>
                    <div class="flex justify-between items-center border-t pt-3">
                        <div class="text-xs text-gray-500" id="meta-${model}"></div>
                        <button onclick="copyResponse('${model}')"
                                class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1">
                            📋 Copy
                        </button>
                    </div>
                </div>
            `;

            resultsDiv.appendChild(card);
        }

        async function queryModel(prompt, model) {
            try {
                const response = await fetch('/compare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt, models: [model] })
                });

                const data = await response.json();
                const result = data.results[0];

                updateCard(model, result);
                allResults.push(result);
                completedCount++;

                updateSummary();

            } catch (error) {
                updateCard(model, {
                    model,
                    error: error.message,
                    time: 0,
                    tokens: 0,
                    cost: 0
                });
            }
        }

        function updateCard(model, result) {
            const spinner = document.getElementById(`spinner-${model}`);
            const content = document.getElementById(`content-${model}`);
            const timeDiv = document.getElementById(`time-${model}`);
            const costDiv = document.getElementById(`cost-${model}`);
            const responseDiv = document.getElementById(`response-${model}`);
            const metaDiv = document.getElementById(`meta-${model}`);

            spinner.classList.add('hidden');
            content.classList.remove('hidden');

            if (result.error) {
                responseDiv.className = 'text-red-600 mb-4 whitespace-pre-wrap text-sm';
                responseDiv.textContent = result.error;
                timeDiv.textContent = '❌ Error';
            } else {
                // Store raw text for copying
                responseTexts[model] = result.response;

                // Render markdown with syntax highlighting
                responseDiv.innerHTML = marked.parse(result.response);

                // Apply syntax highlighting to code blocks
                responseDiv.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });

                // Add copy buttons to code blocks
                addCopyButtonsToCodeBlocks(responseDiv);

                // Calculate tokens per second (efficiency metric)
                const tokensPerSec = Math.round(result.tokens / result.time);
                timeDiv.textContent = `⏱️ ${result.time}s (${tokensPerSec} tok/s)`;

                // Show FREE for $0 costs
                const costDisplay = result.cost === 0 ? 'FREE (local)' : `$${result.cost.toFixed(4)}`;
                costDiv.textContent = `💰 ${costDisplay}`;

                // Add response length indicator
                let lengthIndicator = '';
                if (result.tokens < 200) lengthIndicator = '📝 Brief';
                else if (result.tokens < 500) lengthIndicator = '📄 Detailed';
                else lengthIndicator = '📚 Comprehensive';

                metaDiv.textContent = `${result.tokens} tokens • ${lengthIndicator}`;
            }
        }

        function updateSummary() {
            if (allResults.length === 0) return;

            summary.classList.remove('hidden');

            // Sort by time for speed ranking
            const sorted = [...allResults].filter(r => !r.error).sort((a,b) => a.time - b.time);

            // Speed badges
            const badges = ['⚡ Fastest!', '🥈 2nd', '🥉 3rd'];
            sorted.forEach((result, i) => {
                if (i < 3) {
                    const badge = document.getElementById(`badge-${result.model}`);
                    if (badge) badge.textContent = badges[i];
                }
            });

            // Speed ranking
            const speedRanking = document.getElementById('speedRanking');
            speedRanking.innerHTML = sorted.slice(0, 3).map((r, i) =>
                `<div class="py-1">${i+1}. ${r.model.split('-')[0]} - ${r.time}s</div>`
            ).join('');

            // Cost chart
            const maxCost = Math.max(...sorted.map(r => r.cost));
            const costChart = document.getElementById('costChart');
            costChart.innerHTML = sorted.map(r => {
                // Fix: Ensure minimum 1% width for visibility, handle $0 costs
                const widthPercent = r.cost === 0 ? 1 : Math.max(1, (r.cost / maxCost) * 100);
                const savings = maxCost > 0 ? `(${Math.round((1 - r.cost/maxCost) * 100)}% cheaper)` : '';
                // Show "FREE" for $0 costs instead of $0.0000
                const costDisplay = r.cost === 0 ? 'FREE' : `$${r.cost.toFixed(4)}`;
                return `
                    <div class="py-1">
                        <div class="flex items-center gap-2">
                            <div class="w-24 text-xs truncate">${r.model.split('-')[0]}</div>
                            <div class="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
                                <div class="bg-gradient-to-r from-green-400 to-blue-500 h-full"
                                     style="width: ${widthPercent}%"></div>
                            </div>
                            <div class="text-xs w-20 text-right">${costDisplay}</div>
                        </div>
                        ${savings ? `<div class="text-xs text-green-600 ml-28">${savings}</div>` : ''}
                    </div>
                `;
            }).join('');

            // Overall stats
            const totalCost = sorted.reduce((sum, r) => sum + r.cost, 0);
            const avgTime = sorted.reduce((sum, r) => sum + r.time, 0) / sorted.length;
            const succeeded = allResults.filter(r => !r.error).length;
            const failed = allResults.filter(r => r.error).length;
            const overallStats = document.getElementById('overallStats');
            overallStats.innerHTML = `
                <div class="py-1">Total Cost: $${totalCost.toFixed(4)}</div>
                <div class="py-1">Avg Time: ${avgTime.toFixed(1)}s</div>
                <div class="py-1">✅ Succeeded: ${succeeded}/${allResults.length}</div>
                ${failed > 0 ? `<div class="py-1 text-red-600">❌ Failed: ${failed}</div>` : ''}
            `;
        }

        function addCopyButtonsToCodeBlocks(container) {
            // Add copy button to each code block
            container.querySelectorAll('pre').forEach((pre) => {
                const codeBlock = pre.querySelector('code');
                if (!codeBlock) return;

                // Create copy button
                const copyBtn = document.createElement('button');
                copyBtn.className = 'code-copy-btn';
                copyBtn.textContent = 'Copy';
                copyBtn.onclick = (e) => {
                    e.stopPropagation();
                    const code = codeBlock.textContent;
                    navigator.clipboard.writeText(code);

                    // Change button text temporarily
                    copyBtn.textContent = '✓ Copied!';
                    setTimeout(() => {
                        copyBtn.textContent = 'Copy';
                    }, 2000);
                };

                pre.appendChild(copyBtn);
            });
        }

        function copyResponse(model) {
            // Copy raw markdown text instead of rendered HTML
            const text = responseTexts[model] || document.getElementById(`response-${model}`).textContent;
            navigator.clipboard.writeText(text);

            // Show toast
            const toast = document.createElement('div');
            toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg';
            toast.textContent = '✅ Copied to clipboard!';
            document.body.appendChild(toast);

            setTimeout(() => toast.remove(), 2000);
        }
    </script>
</body>
</html>"""


def start_server(host="127.0.0.1", port=5005, debug=False, open_browser=True):
    """
    Start the Flask development server.

    Args:
        host: Host to bind to
        port: Port to listen on (default: 5005)
        debug: Enable debug mode
        open_browser: Auto-open browser
    """
    app = create_app()

    # Open browser after short delay
    if open_browser and not debug:
        import threading

        def open_browser_delayed():
            import time

            time.sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    print(f"\n🚀 LLMSwap Web UI starting...")
    print(f"📍 Local: http://{host}:{port}")
    print(f"\nPress Ctrl+C to stop\n")

    app.run(host=host, port=port, debug=debug)
