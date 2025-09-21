class Llmswap < Formula
  desc "Universal AI CLI with multi-provider support, teaching features, and cost optimization"
  homepage "https://github.com/sreenathmmenon/llmswap"
  url "https://files.pythonhosted.org/packages/source/l/llmswap/llmswap-5.0.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_AFTER_PYPI_RELEASE"
  license "MIT"
  version "5.0.0"

  depends_on "python@3.11"

  resource "anthropic" do
    url "https://files.pythonhosted.org/packages/source/a/anthropic/anthropic-0.34.2.tar.gz"
    sha256 "efb3c533199d4a0ead3e4a19b4f3b2495fe8b1c5c9e47fbca073a4a4fe3b58f2"
  end

  resource "openai" do
    url "https://files.pythonhosted.org/packages/source/o/openai/openai-1.52.2.tar.gz"
    sha256 "87e3d0cc6841cf41e7064e911c17b74cad8c7fd6bea1b7ca7b72c967d2e6c32e"
  end

  resource "google-generativeai" do
    url "https://files.pythonhosted.org/packages/source/g/google-generativeai/google_generativeai-0.8.3.tar.gz"
    sha256 "90003f77cdbe5e7c8c74dafe9dd0ddc92a90d017e10e3b44d7f4c2166b8e56bb"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/source/r/requests/requests-2.32.3.tar.gz"
    sha256 "55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/source/p/python-dotenv/python_dotenv-1.0.1.tar.gz"
    sha256 "e324ee90a023d808f1959c46bcbc04446a10ced277783dc6ee09987c37ec10ca"
  end

  resource "ibm-watsonx-ai" do
    url "https://files.pythonhosted.org/packages/source/i/ibm-watsonx-ai/ibm_watsonx_ai-1.1.18.tar.gz"
    sha256 "c1b4e36b2b59471b7cf9ed4de94b43b80ba3a8e0cba0a4e80c3c8f6e5a7e0ef7"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/source/h/httpx/httpx-0.27.2.tar.gz"
    sha256 "f7c2be1d2f3c3c3160d441802406b206c2b76f5947b11115e6df10c6c65e66c0"
  end

  resource "aiohttp" do
    url "https://files.pythonhosted.org/packages/source/a/aiohttp/aiohttp-3.10.11.tar.gz"
    sha256 "81c6a2678b6c419ad1ec0ce0e2e2d39b52b21105e91ec9cd5b4ecb6a5de5e0f8"
  end

  resource "aiofiles" do
    url "https://files.pythonhosted.org/packages/source/a/aiofiles/aiofiles-24.1.0.tar.gz"
    sha256 "22a075c9dd0fdbf9f9c4d6c707d36a40c2d32d9e98d6b3e542a8b77b7c70fbb1"
  end

  resource "groq" do
    url "https://files.pythonhosted.org/packages/source/g/groq/groq-0.11.0.tar.gz"
    sha256 "5b00b87b3c5a12674897e44fa8074f9b9f0e3b915fcf1a52f8d6b2abc52de063"
  end

  resource "cohere" do
    url "https://files.pythonhosted.org/packages/source/c/cohere/cohere-5.11.3.tar.gz"
    sha256 "bceb6f10050c9f38e3065b2f6e7d528f7b1aa0a0ddd24c0de57d154e0c3c23c2"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test version
    assert_match "5.0.0", shell_output("#{bin}/llmswap --version")
    
    # Test help command
    help_output = shell_output("#{bin}/llmswap --help")
    assert_match "Universal AI CLI", help_output
    assert_match "conversational", help_output
    
    # Test config functionality (should work without API keys)
    config_output = shell_output("#{bin}/llmswap config show 2>&1", 0)
    assert_match "provider:", config_output
    
    # Test cost comparison (should work without API keys)
    costs_output = shell_output("#{bin}/llmswap costs --input-tokens 100 --output-tokens 50")
    assert_match "Provider Cost Comparison", costs_output
    assert_match "estimated", costs_output
  end
end