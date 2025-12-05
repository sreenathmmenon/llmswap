# 🛡️ COMPATIBILITY RULES - LLMSwap

**Critical:** We have **22,000+ downloads**. Breaking changes affect real users.

---

## ⚠️ **GOLDEN RULE: NEVER BREAK EXISTING CODE**

### **Rule 1: Backward Compatibility is MANDATORY**

Every change MUST work with existing user code. If users have this:

```python
from llmswap import LLMClient

client = LLMClient(provider="anthropic")
response = client.query("Hello")
print(response)
```

This code MUST continue working in ALL future versions.

---

## 🌐 **Rule 2: ALL Providers & Models MUST Work**

Any feature, fix, or enhancement MUST work for:

### **ALL 10 Providers:**
1. ✅ Anthropic (Claude)
2. ✅ OpenAI (GPT)
3. ✅ Google (Gemini)
4. ✅ Groq
5. ✅ Cohere
6. ✅ Perplexity
7. ✅ WatsonX (IBM)
8. ✅ xAI (Grok)
9. ✅ Ollama (Local)
10. ✅ Sarvam AI

### **ALL Models:**
- Claude: opus-4-5, sonnet-4-5, haiku-4-5, etc.
- OpenAI: gpt-5.1, gpt-4.5, gpt-4o, etc.
- Gemini: gemini-3-pro, gemini-3-deep-think, etc.
- And all others...

**No provider-specific or model-specific code allowed!**

---

## 🚫 **WHAT'S PROHIBITED**

### **❌ Never Do:**

1. **Break existing imports:**
   ```python
   # BAD: Removing old imports
   # from llmswap import LLMClient  # REMOVED
   
   # GOOD: Keep all existing imports working
   from llmswap import LLMClient  # ✅ Always works
   ```

2. **Break existing parameters:**
   ```python
   # BAD: Changing parameter names
   LLMClient(provider="anthropic")  # Used to work
   LLMClient(llm_provider="anthropic")  # NEW - breaks existing code ❌
   
   # GOOD: Add new parameters, keep old ones
   LLMClient(provider="anthropic")  # ✅ Still works
   LLMClient(provider="anthropic", new_param=True)  # ✅ Optional new feature
   ```

3. **Make provider-specific changes:**
   ```python
   # BAD: Feature only for OpenAI
   if provider == "openai":
       response = special_handling()
   else:
       response = basic_handling()  # Others get less features ❌
   
   # GOOD: Universal feature for all
   response = universal_handling()  # ✅ Works for all 10 providers
   ```

4. **Change return types:**
   ```python
   # BAD: Breaking return format
   def query(prompt):
       return {"content": "response"}  # NEW - breaks existing code ❌
   
   # GOOD: Keep same return type, add optional fields
   def query(prompt):
       return LLMResponse(content="response")  # ✅ Still works
   ```

5. **Remove existing functionality:**
   ```python
   # BAD: Deprecating without migration path
   # client.stream()  # REMOVED ❌
   
   # GOOD: Deprecate gracefully with warnings
   def stream(self, prompt):
       warnings.warn("stream() is deprecated, use stream_query()", DeprecationWarning)
       return self.stream_query(prompt)  # ✅ Still works, guides to new method
   ```

---

## ✅ **WHAT'S ALLOWED**

### **✓ Safe Changes:**

1. **Add new optional parameters:**
   ```python
   # ✅ GOOD: Old code still works
   LLMClient(provider="anthropic")  # Works as before
   LLMClient(provider="anthropic", debug=True)  # New optional feature
   ```

2. **Add new methods:**
   ```python
   # ✅ GOOD: Doesn't affect existing code
   client.query("test")  # Old method still works
   client.query_with_retry("test")  # New method, optional
   ```

3. **Add new exception types:**
   ```python
   # ✅ GOOD: More specific exceptions (old code still works)
   try:
       response = client.query("test")
   except ProviderError as e:  # Catches RateLimitError too
       print(e)
   
   # New code can be more specific:
   except RateLimitError as e:  # More precise handling
       print(e)
   ```

4. **Enhance error messages:**
   ```python
   # ✅ GOOD: Better messages, same exceptions
   # Old: "Rate limit exceeded"
   # New: "Rate limit exceeded. Try: client.set_provider('openai')"
   # Exception type unchanged, user code still works
   ```

5. **Add new providers:**
   ```python
   # ✅ GOOD: More options, doesn't break existing
   LLMClient(provider="anthropic")  # Still works
   LLMClient(provider="new_provider")  # New option
   ```

---

## 📋 **PRE-RELEASE CHECKLIST**

Before ANY release, verify:

### **1. Backward Compatibility Tests:**
```bash
# Test with OLD code patterns (from docs/examples v1.0.0)
python3 tests/test_backward_compatibility.py
```

### **2. All Providers Work:**
```bash
# Test each provider individually
for provider in anthropic openai gemini groq cohere perplexity watsonx xai ollama sarvam
do
    python3 -c "from llmswap import LLMClient; LLMClient(provider='$provider')"
done
```

### **3. Existing Examples Run:**
```bash
# All examples from previous versions must work
python3 examples/basic_usage.py
python3 examples/provider_switching.py
python3 examples/streaming.py
```

### **4. Import Tests:**
```bash
# All documented imports must work
python3 -c "from llmswap import LLMClient, LLMResponse, Tool, MCPClient"
python3 -c "from llmswap import ProviderError, ConfigurationError"
```

### **5. No Breaking Changes in CHANGELOG:**
```bash
# Review CHANGELOG.md
# Ensure no "BREAKING CHANGE" entries without migration guide
grep -i "breaking" CHANGELOG.md
```

---

## 🔄 **DEPRECATION PROCESS**

If you MUST remove something (rarely needed):

### **Step 1: Deprecation Warning (v5.x)**
```python
def old_method(self):
    warnings.warn(
        "old_method() is deprecated and will be removed in v6.0. "
        "Use new_method() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()  # Still works!
```

### **Step 2: Keep for 6+ Months**
- Release v5.4.0 with warning (Dec 2025)
- Keep working until v6.0.0 (Jun 2026+)

### **Step 3: Document Migration**
```markdown
# CHANGELOG.md

## v5.4.0 - Deprecations
- `old_method()` is deprecated. Use `new_method()` instead.
  Migration: Change `client.old_method()` to `client.new_method()`

## v6.0.0 - Breaking Changes (Future)
- Removed `old_method()`. Use `new_method()`.
```

### **Step 4: Only Remove in Major Version**
- v5.x → No removals
- v6.0.0 → Can remove (with 6+ months notice)

---

## 🎯 **DEVELOPMENT GUIDELINES**

### **When Adding Features:**

1. **Design universally:**
   ```python
   # BAD: Provider-specific
   def query(self, prompt):
       if self.provider == "anthropic":
           return self._anthropic_query(prompt)
       elif self.provider == "openai":
           return self._openai_query(prompt)
       # ❌ Have to update for every provider!
   
   # GOOD: Universal
   def query(self, prompt):
       return self.current_provider.query(prompt)
       # ✅ Works for all providers automatically!
   ```

2. **Test with all providers:**
   ```python
   @pytest.mark.parametrize("provider", [
       "anthropic", "openai", "gemini", "groq", "cohere",
       "perplexity", "watsonx", "xai", "ollama", "sarvam"
   ])
   def test_feature(provider):
       client = LLMClient(provider=provider)
       # Test feature works for this provider
   ```

3. **Document for all:**
   ```markdown
   # BAD: Provider-specific docs
   ## Streaming (OpenAI only)
   
   # GOOD: Universal docs
   ## Streaming (All Providers)
   Works with: Anthropic, OpenAI, Gemini, Groq, Cohere,
               Perplexity, WatsonX, xAI, Ollama, Sarvam
   ```

---

## 📊 **VERSION STRATEGY**

### **Semantic Versioning:**

- **v5.4.0 → v5.4.1** (Patch)
  - ✅ Bug fixes
  - ✅ Documentation updates
  - ✅ Security patches
  - ❌ No new features
  - ❌ No API changes

- **v5.4.0 → v5.5.0** (Minor)
  - ✅ New features
  - ✅ New optional parameters
  - ✅ New methods
  - ✅ New providers
  - ❌ No breaking changes

- **v5.4.0 → v6.0.0** (Major)
  - ✅ Breaking changes (after 6+ months warning)
  - ✅ Removal of deprecated features
  - ✅ Major architecture changes
  - ⚠️ RARE - Avoid if possible

---

## 🛡️ **PROTECTION MECHANISMS**

### **1. Automated Tests:**
```python
# tests/test_backward_compatibility.py
def test_v1_api_still_works():
    """Ensure v1.0.0 code patterns still work."""
    # Original v1.0.0 usage
    from llmswap import LLMClient
    client = LLMClient(provider="anthropic")
    response = client.query("test")
    assert isinstance(response, str) or hasattr(response, 'content')
```

### **2. CI/CD Checks:**
```yaml
# .github/workflows/compatibility.yml
name: Compatibility Check
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test all providers
        run: |
          for provider in anthropic openai gemini groq cohere perplexity watsonx xai ollama sarvam
          do
            pytest tests/test_${provider}.py
          done
```

### **3. Documentation:**
```markdown
# Every README example must work in current version
# Every example/ file must be tested
# Every CHANGELOG entry must note compatibility
```

---

## 📝 **COMMIT MESSAGE RULES**

When committing changes:

```bash
# GOOD: Clear about compatibility
git commit -m "Add streaming support for all 10 providers

- Works universally with Anthropic, OpenAI, Gemini, etc.
- Backward compatible (query() still works)
- New optional method: stream_query()
- All existing code continues working"

# BAD: Unclear about impact
git commit -m "Update providers"  # ❌ What changed? Does it break anything?
```

---

## 🎯 **SUMMARY**

### **The Rules:**

1. ✅ **Backward compatibility is MANDATORY**
2. ✅ **All changes work for ALL 10 providers**
3. ✅ **All changes work for ALL models**
4. ✅ **Never break existing user code**
5. ✅ **Test with all providers before release**
6. ✅ **Document migration paths for any deprecations**
7. ✅ **Keep deprecated features for 6+ months**
8. ✅ **Only break in major versions (v6.0.0+)**

### **Remember:**

**22,000+ users trust LLMSwap.**  
**Every change affects production systems.**  
**Stability > New features.**

---

## 🚨 **EMERGENCY: If You Break Compatibility**

1. **Immediate rollback:**
   ```bash
   git revert <commit>
   git push origin main
   ```

2. **Release patch:**
   ```bash
   # v5.4.1 with fix
   python3 -m build
   python3 -m twine upload dist/*
   ```

3. **Notify users:**
   ```markdown
   # GitHub Release Notes
   ## v5.4.1 - Critical Compatibility Fix
   
   We accidentally broke X in v5.4.0. This is now fixed.
   Please upgrade immediately: pip install --upgrade llmswap
   ```

4. **Learn and prevent:**
   - Add test case for what broke
   - Update CI/CD to catch similar issues
   - Document in this file

---

## ✅ **THIS IS A CONTRACT WITH OUR USERS**

By contributing to LLMSwap, you agree to:

- ✅ Never break backward compatibility without 6+ months notice
- ✅ Test all changes with all 10 providers
- ✅ Keep user code working across versions
- ✅ Prioritize stability over features

**Our users depend on us. We will not let them down.** 🛡️

---

**Last Updated:** December 5, 2025  
**Applies to:** v5.4.0 and all future versions  
**Status:** MANDATORY for all contributors
