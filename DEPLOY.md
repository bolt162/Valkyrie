# Deploying Valkyrie to Render.com

This guide will help you deploy Valkyrie PTaaS Platform to Render.com for free.

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Render.com account (free)

## Step 1: Push to GitHub

If you haven't already, push your code to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

## Step 2: Deploy to Render

### Option A: Blueprint Deployment (Recommended)

1. Go to [render.com](https://render.com) and sign in
2. Click **New** → **Blueprint**
3. Connect your GitHub account if not already connected
4. Select your repository (LLM-Canvas)
5. Render will detect the `render.yaml` file and show:
   - `valkyrie-api` (Backend - Web Service)
   - `valkyrie-app` (Frontend - Static Site)
6. Click **Apply** to deploy both services

### Option B: Manual Deployment

If blueprint doesn't work, deploy manually:

#### Deploy Backend First:

1. Click **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `valkyrie-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Select **Free** plan
5. Click **Create Web Service**
6. **Copy the URL** once deployed (e.g., `https://valkyrie-api.onrender.com`)

#### Deploy Frontend:

1. Click **New** → **Static Site**
2. Connect the same GitHub repo
3. Configure:
   - **Name**: `valkyrie-app`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: Your backend URL from step 6 (e.g., `https://valkyrie-api.onrender.com`)
5. Click **Create Static Site**

## Step 3: Update Frontend API URL (if needed)

If you deployed manually, update `frontend/.env.production`:

```
VITE_API_URL=https://your-actual-backend-name.onrender.com
```

Then redeploy the frontend (push a commit or trigger manual deploy).

## Step 4: Verify Deployment

1. Visit your frontend URL: `https://valkyrie-app.onrender.com`
2. The app should load and show the landing page
3. Navigate to Dashboard - it should fetch data from the backend

## Important Notes

### Free Tier Limitations

- **Cold Starts**: Free services spin down after 15 minutes of inactivity. The first request after sleeping takes ~30 seconds.
- **Data Persistence**: SQLite database resets on redeploy. For production, consider upgrading to a managed database.

### Custom Domain (Optional)

To add a custom domain:
1. Go to your service on Render
2. Click **Settings** → **Custom Domains**
3. Add your domain and configure DNS as instructed

### Environment Variables

You can add optional environment variables in Render dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | For LLM testing features | No |

## Troubleshooting

### Frontend shows "Loading..." forever
- Check browser console for errors
- Verify `VITE_API_URL` is set correctly
- Ensure backend is running (check Render logs)

### Backend returns 500 errors
- Check Render logs for the backend service
- Ensure all dependencies are in `requirements.txt`

### CORS errors
- Backend already allows all origins (`*`)
- If issues persist, check the backend CORS configuration in `main.py`

## Your URLs

After deployment, your app will be available at:
- **Frontend**: `https://valkyrie-app.onrender.com`
- **Backend API**: `https://valkyrie-api.onrender.com`
- **Health Check**: `https://valkyrie-api.onrender.com/health`

---

Good luck with your YC application! 🚀
