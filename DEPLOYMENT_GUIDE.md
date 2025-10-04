# Vercel Deployment Guide

## Frontend-Only Deployment (Current Setup)

This project is configured to deploy only the React frontend to Vercel. The backend Python server is not included in this deployment.

### What's Included:
- ✅ React frontend with TypeScript
- ✅ Mock API responses for demo mode
- ✅ Character sprites and UI components
- ✅ Responsive design

### What's NOT Included:
- ❌ Python backend server
- ❌ AI conversation functionality
- ❌ Real-time streaming responses

### Deployment Steps:

1. **Push your changes to GitHub** (if not already done)
2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will automatically detect the `vercel.json` configuration

3. **Deploy**:
   - Vercel will automatically build and deploy your React app
   - The app will work in "demo mode" with mock responses

### Testing Locally:

To test the full application with the backend:

1. **Start the backend server**:
   ```bash
   python api_server.py
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Access the app**: http://localhost:3000

### Full-Stack Deployment (Optional)

If you want to deploy both frontend and backend, you'll need to:

1. Convert the Python Flask app to serverless functions
2. Update the Vercel configuration
3. Set up environment variables for API keys

This is more complex and requires additional configuration.
