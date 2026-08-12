# 🚀 Deploy to Render

Click the button below to deploy DataBound AI to Render with a single click.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/himanshudevatwal03-lgtm/databound-ai)

---

## 📋 Deployment Steps

### **Step 1: Click the Deploy Button** (Above)

You'll be taken to Render's deployment page.

### **Step 2: Fill in Required Secrets**

You'll see a form asking for these values:

| Secret Name | Description | Where to Get |
|---|---|---|
| **LLM_API_KEY** | OpenAI API Key | https://platform.openai.com/api-keys |
| **JWT_SECRET** | Random secret for JWT | Generate: `openssl rand -hex 32` |

### **Step 3: Get Your Secrets**

#### **OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Copy the key
4. Paste into Render form

#### **JWT Secret:**
Run this command:
```bash
openssl rand -hex 32
```

Or just use any random string:
```
my-super-secret-key-databound-ai-2024
```

### **Step 4: Click "Deploy"**

Render will automatically:
- ✅ Create PostgreSQL database
- ✅ Build and deploy backend
- ✅ Build and deploy frontend
- ✅ Connect all services
- ✅ Configure environment variables

### **Step 5: Wait for Deployment** (8-10 minutes)

You'll see logs showing:
```
Building backend...
✓ Backend deployed
Building frontend...
✓ Frontend deployed
All services running
```

---

## 🎯 After Deployment

Once complete, you'll have:

```
🔗 Frontend: https://databound-frontend.onrender.com
🔗 Backend:  https://databound-backend.onrender.com
🔗 API Docs: https://databound-backend.onrender.com/docs
💾 Database: PostgreSQL connected
```

---

## ⚡ What Gets Deployed

### Services Created:

1. **databound-db** (PostgreSQL 16)
   - Free tier database
   - 90-day data retention

2. **databound-backend** (FastAPI)
   - Free tier web service
   - Spins down after 15 min inactivity
   - Runs on port 8000

3. **databound-frontend** (React + Vite)
   - Free tier web service
   - Spins down after 15 min inactivity
   - Runs on port 5173

---

## 💡 Free Tier Limitations

| Limit | Behavior |
|-------|----------|
| **Inactivity** | Services spin down after 15 min (wake up on request) |
| **Database** | Data kept for 90 days only |
| **Uptime** | Not guaranteed for production |
| **Resources** | 512 MB RAM, 0.1 CPU |

**For production use:** Upgrade to Starter plan ($7-12/month per service)

---

## 🔧 Environment Variables

All environment variables are automatically configured:

```yaml
# Database (auto-connected)
DATABASE_URL=postgresql://...

# LLM (you provide)
LLM_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# Embeddings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai

# RAG Settings
TOP_K=5
SIMILARITY_THRESHOLD=0.5
MAX_FILE_SIZE=52428800

# JWT (you provide)
JWT_SECRET=...
JWT_ALGORITHM=HS256

# Environment
ENVIRONMENT=production
```

---

## ✅ Verify Deployment

After services are running:

### **Test Backend:**
```bash
curl https://databound-backend.onrender.com/api/health
# Expected: {"status":"ok","service":"databound-ai-backend"}
```

### **Test Frontend:**
```
Open: https://databound-frontend.onrender.com
Expected: See "🚀 DataBound AI" with "Backend: connected" ✅
```

### **Test API Docs:**
```
Open: https://databound-backend.onrender.com/docs
Expected: See Swagger UI with health endpoints
```

---

## 🆘 Troubleshooting

### **Issue: "Service is spinning down"**
- Free tier services sleep after 15 min of no use
- Just reload the page and wait 30 seconds
- **Fix:** Upgrade to Starter plan

### **Issue: "Database connection error"**
- Wait 2-3 minutes for database to fully initialize
- Check Render dashboard for database status
- Restart backend service

### **Issue: "Frontend shows 'Backend: disconnected'"**
- Check `VITE_API_URL` environment variable
- Verify backend is running
- Check CORS settings

### **Issue: Deployment fails**
- Check Render logs for error messages
- Verify your LLM_API_KEY is valid
- Ensure JWT_SECRET is set

---

## 📊 Monitor Deployment

1. Go to https://dashboard.render.com
2. Select **"Production"** environment
3. View logs for each service:
   - **databound-db** → Database logs
   - **databound-backend** → Backend logs
   - **databound-frontend** → Frontend logs

---

## 🎉 You're Live!

Once deployed, you can:

✅ Access your application from anywhere
✅ Share URLs with others
✅ Scale up (upgrade plans) when needed
✅ Monitor performance in Render dashboard

---

## 📝 Next Phase

After deployment is confirmed working, Phase 2 will add:
- User registration & login
- JWT authentication
- Password hashing
- User data isolation

---

**Ready to deploy?** Click the **"Deploy to Render"** button at the top! 🚀
