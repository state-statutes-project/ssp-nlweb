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
- ✅ Your state data loaded (using the multi-state loading scripts)

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
# Choose your LLM provider (at least one required)
OPENAI_API_KEY=your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key
# OR
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key

# Choose your vector store (at least one required)
# For development/testing, you can use Milvus Lite:
MILVUS_ENDPOINT=/app/data/milvus.db

# OR for production Qdrant:
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key

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

### 4. Configure Persistent Storage (Important!)

Since you're using state data files, you need persistent storage:

1. In Railway dashboard, go to your service
2. Click "Settings" → "Mounts"
3. Add a new mount:
   - Mount Path: `/app/data`
   - This will persist your vector database and loaded state data

### 5. Deploy

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
- The free Railway tier provides 512MB RAM and 1GB disk
- For production with all states loaded, you'll need at least:
  - 8GB RAM (Hobby plan or higher)
  - 10GB persistent storage
  - Consider using Railway's autoscaling features

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

1. **Out of Memory Errors**
   - Solution: Upgrade to a higher tier or load fewer states
   - Alternative: Use external vector database instead of file-based

2. **Slow Startup**
   - This is normal if loading many states
   - Consider implementing a health check endpoint that returns early

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
- **Hobby Plan** ($5/month): Good for testing with a few states
- **Pro Plan** ($20/month): Suitable for production with all states
- Additional costs for:
  - Persistent storage
  - Bandwidth
  - External database services