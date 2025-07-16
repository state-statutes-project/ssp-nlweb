# Deploying NLWeb to Railway

This guide walks you through deploying NLWeb to Railway, a modern cloud platform that makes deployment simple.

## Prerequisites

1. A [Railway account](https://railway.app)
2. Railway CLI installed (optional): `npm install -g @railway/cli`
3. Your configured environment variables ready

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository has:
- ✅ `Dockerfile` (already exists)
- ✅ `railway.json` (just created)
- ✅ Your Qdrant database already populated with state data

### 2. Create a New Railway Project

#### Option A: Using Railway Dashboard (Recommended)
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select your repository
5. Railway will automatically detect the Dockerfile

#### Option B: Using Railway CLI
```bash
# From your project directory
railway login
railway link
railway up
```

### 3. Configure Environment Variables

In the Railway dashboard for your project:

1. Go to your service settings
2. Click on "Variables"
3. Add the following required variables:

**Required for Basic Functionality:**
```
# LLM Provider (choose one)
OPENAI_API_KEY=your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key

# Qdrant Vector Database
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-api-key

# Logging configuration
NLWEB_LOGGING_PROFILE=production
```

**Optional OAuth Configuration (if you want login functionality):**
```
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Other OAuth providers as needed...
```

### 4. Deploy

If using GitHub integration:
- Simply push to your connected branch
- Railway will automatically build and deploy

If using CLI:
```bash
railway up
```

### 6. Access Your Application

Once deployed:
1. Railway will provide you with a URL like `https://your-app.railway.app`
2. Your NLWeb interface will be available at this URL
3. The chat interface will be at the root path `/`

## Important Considerations

### Memory and Performance
- Since you're using Qdrant (external vector database), Railway resource requirements are minimal
- The free Railway tier (512MB RAM) should be sufficient for the web service
- For better performance, consider:
  - Hobby plan ($5/month) for more resources
  - Using Railway's autoscaling features for high traffic

### Database Connection
- If using an external vector database (recommended for production):
  - Ensure your database is accessible from Railway's network
  - Use connection strings with proper SSL/TLS configuration
  - Consider using Railway's private networking for databases

### Monitoring
- Use Railway's built-in metrics to monitor:
  - Memory usage
  - CPU usage
  - Response times
  - Error rates

### Scaling Options
1. **Vertical Scaling**: Upgrade to higher memory/CPU tiers
2. **Horizontal Scaling**: Use Railway's replica feature
3. **Database Optimization**: Use external managed vector databases

## Troubleshooting

### Common Issues

1. **Connection to Qdrant Failed**
   - Ensure QDRANT_URL is accessible from Railway
   - Check if QDRANT_API_KEY is correct
   - Verify Qdrant allows connections from Railway's IP range

2. **Slow Response Times**
   - Check Qdrant query performance
   - Consider upgrading Railway tier for more CPU

3. **Connection Timeouts**
   - Increase health check timeout in `railway.json`
   - Ensure your vector database is properly configured

### Debugging
- Check logs: `railway logs`
- SSH into container: `railway shell`
- Monitor metrics in Railway dashboard

## Production Recommendations

1. **Use External Services**:
   - Vector Database: Qdrant Cloud, Pinecone, or Weaviate
   - Consider using Railway's database offerings

2. **Environment-Specific Config**:
   - Use different environment variables for staging vs production
   - Implement proper secret management

3. **Monitoring and Alerts**:
   - Set up Railway's alerting for high memory/CPU usage
   - Implement custom health checks

4. **Backup Strategy**:
   - Regular backups of your vector database
   - Version control for your state data

## Cost Estimation

Based on Railway's pricing (as of 2024):
- **Free Tier**: Should work fine for testing/development
- **Hobby Plan** ($5/month): Recommended for production with better performance
- **Pro Plan** ($20/month): For high traffic or multiple replicas
- Additional costs:
  - Bandwidth (if high traffic)
  - Your external Qdrant service