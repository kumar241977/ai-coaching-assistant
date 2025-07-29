# 🚀 Setup GitHub Models for AI Coaching

Your GitHub Copilot access gives you **FREE** access to GitHub Models! No OpenAI API key needed.

## ✅ **What You Get:**
- **Free AI model access** (GPT-4o, GPT-4o-mini, and more)
- **No additional costs** beyond your existing Copilot subscription
- **Production-grade models** for unlimited coaching conversations
- **Same OpenAI-compatible API**

## 🔧 **Setup Options:**

### **Option 1: Use Built-in GITHUB_TOKEN (Recommended)**

Since you're in **GitHub Codespaces**, you already have access! The built-in `GITHUB_TOKEN` automatically has GitHub Models access.

In your **GitHub Codespace terminal**:

```bash
# Use the built-in token (already available in Codespaces)
export GITHUB_TOKEN=$GITHUB_TOKEN

# Restart the app
python app.py
```

### **Option 2: Create Fine-Grained Personal Access Token**

If Option 1 doesn't work, create a fine-grained token:

1. Go to: [https://github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
2. **Token name**: `AI Coaching App`
3. **Resource owner**: Select yourself
4. **Repository access**: `All repositories` or `Selected repositories`
5. **Account permissions**: Look for any model-related permissions
6. **Generate token** and copy it

```bash
export GITHUB_TOKEN="github_pat_your_token_here"
python app.py
```

### **Option 3: Classic Token with Basic Scopes**

If neither works, try a classic token with basic permissions:

1. Go to: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. **Generate new token (classic)**
3. **Select scopes**: Just check `repo` and `user` (basic access)
4. **Generate token**

```bash
export GITHUB_TOKEN="ghp_your_classic_token_here"
python app.py
```

## 🧪 **Test Which Method Works:**

When you start the app, look for:
- ✅ **"GITHUB MODELS: Using GitHub Models API for intelligent coaching responses."**
- ❌ **"DEMO MODE: Using demo responses..."**

## 🔍 **If Still Having Issues:**

Try these troubleshooting steps:

1. **Check your Copilot access**: Visit [https://github.com/settings/copilot](https://github.com/settings/copilot)
2. **Verify Models access**: Try accessing [https://github.com/marketplace/models](https://github.com/marketplace/models)
3. **Test in browser**: Check if you can use GitHub Models in the playground

## 💡 **Alternative: Fallback to Demo Mode**

If GitHub Models isn't accessible yet, the app will automatically use intelligent demo responses that are much better than the old repetitive ones. Just run:

```bash
python app.py
```

The improved demo mode provides varied, contextual coaching responses!

**Let's try Option 1 first - it should work automatically in Codespaces!** 🚀 