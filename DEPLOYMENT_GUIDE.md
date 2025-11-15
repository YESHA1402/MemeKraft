# MemeKraft Deployment Guide

## 🚀 Quick Start Deployment

This guide will help you deploy your AI-powered meme book generator to production.

### Prerequisites
- GitHub account (you have this ✓)
- Railway account (free tier available)
- Vercel account (free tier available)
- Docker (for local testing)

---

## 📋 Step 1: GitHub Actions Secrets (Already Done!)

You've already added these 4 secrets:
- ✅ RAILWAY_TOKEN
- ✅ VERCEL_TOKEN
- ✅ VERCEL_ORG_ID
- ✅ VERCEL_PROJECT_ID

Great! These are stored securely at:
`https://github.com/YESHA1402/MemeKraft/settings/secrets/actions`

---

## 🐳 Step 2: Local Testing with Docker

### Test Everything Locally First

```bash
# Clone and navigate to your repository
cd MemeKraft

# Start both services with Docker Compose
docker-compose up

# Frontend will be available at: http://localhost:3000
# Backend API will be available at: http://localhost:5000
```

### Verify Services

```bash
# In another terminal, test the backend health check
curl http://localhost:5000/health

# Test the frontend is running
curl http://localhost:3000
```

---

## 🚀 Step 3: Deploy to Production

### Option A: Automatic Deployment (Recommended)

Once you push to the `main` branch, GitHub Actions will automatically:

1. ✅ Run tests on backend (Python 3.9, 3.10, 3.11)
2. ✅ Run tests on frontend (Node 18.x, 20.x)
3. ✅ Build Docker images
4. ✅ Push images to GitHub Container Registry
5. ✅ Deploy backend to Railway
6. ✅ Deploy frontend to Vercel

**How to trigger deployment:**

```bash
# Make changes to your code
git add .
git commit -m "Deploy MemeKraft"
git push origin main

# GitHub Actions will automatically run!
# Monitor progress at: https://github.com/YESHA1402/MemeKraft/actions
```

### Option B: Manual Deployment

If automatic deployment fails, deploy manually:

**Backend (Railway):**
```bash
npm install -g @railway/cli
railway login
railway up --service backend
```

**Frontend (Vercel):**
```bash
npm install -g vercel
vercel --prod
```

---

## 📊 Step 4: Monitor Your Deployment

### GitHub Actions Workflows
- **Tests Workflow**: https://github.com/YESHA1402/MemeKraft/actions/workflows/test.yml
- **Deploy Workflow**: https://github.com/YESHA1402/MemeKraft/actions/workflows/deploy.yml

Watch for green checkmarks ✅ indicating successful deployment.

### Railway Dashboard
- **URL**: https://railway.app/dashboard
- View logs, environment variables, and deployment status
- Your backend will be available at a Railway-provided URL

### Vercel Dashboard
- **URL**: https://vercel.com/dashboard
- View deployments, analytics, and preview URLs
- Your frontend will be available at: `https://memekraft.vercel.app`

---

## 🔑 Step 5: Configure Environment Variables

### Backend Environment Variables (Railway)

In Railway dashboard, set these for your backend service:

```bash
FLASK_ENV=production
FLASK_APP=app.py
PYTHONUNBUFFERED=1
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=your_database_url_if_needed
```

### Frontend Environment Variables (Vercel)

In Vercel dashboard, set these for your project:

```bash
REACT_APP_API_URL=https://your-railway-backend-url.railway.app
NODE_ENV=production
```

---

## 🐛 Troubleshooting

### Deployment Failed?

1. **Check GitHub Actions logs**:
   - Go to your repo → Actions tab
   - Click on the failed workflow
   - Look for error messages in red

2. **Missing or incorrect secrets?**
   - Go to Settings → Secrets → Actions
   - Verify all 4 secrets are present and correct
   - Regenerate tokens if they're expired

3. **Docker build issues?**
   - Test locally: `docker-compose up`
   - Check Dockerfile syntax
   - Ensure `requirements.txt` and `package.json` exist

4. **Railway deployment issues?**
   - Check Railway logs: https://railway.app/dashboard
   - Verify `requirements.txt` includes `gunicorn`
   - Ensure Python version is 3.11 or compatible

5. **Vercel deployment issues?**
   - Check Vercel logs: https://vercel.com/dashboard
   - Verify `npm run build` works locally
   - Check `package.json` has a `build` script

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Frontend loads at Vercel URL
- [ ] Backend API responds at Railway URL
- [ ] Backend health check returns 200 OK
- [ ] Frontend can communicate with backend API
- [ ] Meme generation works end-to-end
- [ ] Books can be downloaded in multiple languages
- [ ] GitHub Actions shows green checkmarks on latest push

---

## 🔄 Continuous Deployment Workflow

Once set up, your workflow is:

1. Make changes locally
2. Push to GitHub (`git push origin main`)
3. GitHub Actions automatically:
   - Runs tests
   - Builds Docker images
   - Deploys to Railway (backend)
   - Deploys to Vercel (frontend)
4. Check deployment status in Actions tab
5. Access your live application

---

## 📞 Support Resources

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Docker Docs**: https://docs.docker.com

---

## 🎉 You're All Set!

Your MemeKraft meme book generator is now set up for continuous deployment. Every time you push to the `main` branch, your application will be automatically tested and deployed to production.

Happy meme generating! 🚀📚