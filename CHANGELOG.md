# Changelog

## [1.4.0] - 2025-08-07
### Added
- **GPT-OSS Support** - OpenAI's open-weight models via Ollama
  - `gpt-oss-20b` (16GB RAM) for efficient local reasoning
  - `gpt-oss-120b` (80GB VRAM) for advanced reasoning tasks
- **Comprehensive Ollama Model Documentation** - 100+ supported models
  - Llama 3.1/3.2 family (1B to 405B parameters)
  - Mistral models including Codestral and Nemo
  - Google Gemma 2/3 series
  - Qwen 2.5 including specialized coder variants
  - Microsoft Phi 3/4 models
  - IBM Granite Code and other specialized models
- **Enhanced Documentation** - Detailed model specifications and usage examples

## [1.0.4] - 2025-08-07
### Added
- Comprehensive pytest test suite
- GitHub Actions CI/CD pipeline
- Enhanced SEO keywords and package description
### Changed
- Improved project documentation and professionalism
### Added
- GPT-OSS provider support

## [1.5.0] - Planned  
### Added
- IBM watsonx provider support

## [1.0.3] - 2025-08-03
### Changed
- Renamed package from any-llm to llmswap

## [1.0.2] - 2025-08-02
### Fixed
- PyPI naming conflict with existing package

## [1.0.1] - 2025-08-02
### Added
- Automatic fallback to next available provider
- Method to check provider availability

## [1.0.0] - 2025-08-01
### Added
- Initial release
- Support for Anthropic, OpenAI, Google Gemini, and Ollama
- Auto-detection of providers via environment variables