# Changelog

## [1.4.0] - 2025-08-07
### Added
- GPT-OSS support via Ollama integration
  - gpt-oss-20b model support (16GB RAM requirement)
  - gpt-oss-120b model support (80GB VRAM requirement)
- Complete documentation for Ollama model support
  - Llama 3.1 and 3.2 model families (1B to 405B parameters)
  - Mistral models including Codestral and Nemo variants
  - Google Gemma 2 and 3 model series
  - Qwen 2.5 models with coder-specific variants
  - Microsoft Phi 3 and 4 models
  - IBM Granite Code models and other specialized options
- Updated documentation with model specifications and usage examples

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