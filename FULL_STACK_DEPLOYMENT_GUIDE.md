# Full-Stack Deployment Guide

## Overview
This guide will help you deploy both the React frontend (to Vercel) and Python backend (to Railway) for a complete AI girlfriend chat application.

## Prerequisites
- GitHub account
- Vercel account (free)
- Railway account (free tier available)
- Mistral API key

## Step 1: Deploy Backend to Railway

### 1.1 Prepare Your Repository
1. **Commit all changes**:
   ```bash
   git add .
   git commit -m "Add full-stack deployment configuration"
   git push
   ```

### 1.2 Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python app

### 1.3 Configure Environment Variables
In Railway dashboard, go to your project → Variables tab and add:
```
MISTRAL_API_KEY=your_mistral_api_key_here
FLASK_ENV=production
```

### 1.4 Get Your Backend URL
1. Railway will provide a URL like: `https://your-app-name.railway.app`
2. **Copy this URL** - you'll need it for the frontend

## Step 2: Update Frontend Configuration

### 2.1 Update API URL
1. Open `frontend/src/services/api.ts`
2. Replace `https://your-backend-url.railway.app/api` with your actual Railway URL:
   ```typescript
   const API_BASE_URL = isProduction ? 'https://your-actual-railway-url.railway.app/api' : 'http://localhost:5000/api';
   ```

### 2.2 Commit Frontend Changes
```bash
git add frontend/src/services/api.ts
git commit -m "Update frontend to use Railway backend URL"
git push
```

## Step 3: Deploy Frontend to Vercel

### 3.1 Connect to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up/login with GitHub
3. Click "New Project" → Import your repository

### 3.2 Configure Build Settings
Vercel should automatically detect the `vercel.json` configuration:
- Build Command: `cd frontend && npm run build`
- Output Directory: `frontend/build`
- Install Command: `cd frontend && npm install`

### 3.3 Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Your app will be available at `https://your-app-name.vercel.app`

## Step 4: Test Your Deployment

### 4.1 Test Backend
Visit: `https://your-railway-url.railway.app/api/health`
Should return: `{"status": "healthy", ...}`

### 4.2 Test Frontend
1. Visit your Vercel URL
2. Click "Start Conversation"
3. Send a message
4. You should get real AI responses!

## Step 5: Get Your Mistral API Key

### 5.1 Sign Up for Mistral
1. Go to [console.mistral.ai](https://console.mistral.ai)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key

### 5.2 Add to Railway
1. Copy your API key
2. Go to Railway → Your Project → Variables
3. Add: `MISTRAL_API_KEY=your_key_here`
4. Redeploy if needed

## Troubleshooting

### Backend Issues
- **Health check fails**: Check Railway logs for errors
- **API key issues**: Verify `MISTRAL_API_KEY` is set correctly
- **CORS errors**: Check that your Vercel URL is in the CORS origins list

### Frontend Issues
- **404 errors**: Ensure `vercel.json` is in the root directory
- **API connection fails**: Verify the Railway URL in `api.ts` is correct
- **Build fails**: Check that all dependencies are in `frontend/package.json`

### Common Solutions
1. **Check logs**: Both Railway and Vercel provide detailed logs
2. **Redeploy**: Sometimes a simple redeploy fixes issues
3. **Environment variables**: Double-check all required variables are set
4. **URLs**: Ensure all URLs are correct and accessible

## Cost Information
- **Vercel**: Free tier includes 100GB bandwidth/month
- **Railway**: Free tier includes $5 credit/month (usually enough for small apps)
- **Mistral**: Pay-per-use API pricing

## Next Steps
Once deployed, you can:
- Customize the AI personality in `girlfriend_agent.py`
- Add more features to the frontend
- Set up custom domains
- Add monitoring and analytics

## Support
If you encounter issues:
1. Check the logs in both Railway and Vercel
2. Verify all environment variables are set
3. Test the backend health endpoint
4. Check browser console for frontend errors
