# Troubleshooting: "Thinking..." Stuck

## 🐛 Problem
The chat shows "Thinking..." spinner but never responds.

## 🔍 Root Cause
**Your quota is exhausted** - The API call is hanging because:
1. Gemini API is rejecting requests (429 error)
2. The request times out after 30 seconds
3. Error handling now catches this and shows a clear message

## ✅ What I Fixed

1. **Added 30-second timeout** - Won't hang forever
2. **Better error messages** - Shows quota error clearly
3. **Message persistence** - Your messages won't disappear

## 🔄 What to Do Now

### Option 1: Wait for Quota Reset (Recommended)
- **Time**: 24 hours from when you first hit the limit
- **After reset**: Everything will work instantly
- **Your documents**: Already processed, ready to use

### Option 2: Upgrade to Paid Tier
- Visit: https://ai.google.dev/pricing
- Get immediate access
- Higher limits

## 🧪 Test After Quota Resets

1. **Restart the app**: `streamlit run app/app.py`
2. **Ask a question**: Should respond in 2-5 seconds
3. **Check sidebar**: Should show source pages

## 📊 Current Status

- ✅ **Documents processed**: Vector DB exists
- ✅ **Code fixed**: Timeout and error handling added
- ❌ **Quota exhausted**: Can't generate responses until reset

## 💡 Why It Was Hanging

The API call was waiting indefinitely for a response that never came because:
- Quota limit = API rejects requests
- No timeout = App waits forever
- No error handling = Silent failure

**Now fixed**: 30-second timeout + clear error messages!

