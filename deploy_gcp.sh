#!/bin/bash

# AluuGPT Google Cloud Run Deployment Script
# -----------------------------------------

# 1. Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="aluugpt"
REGION="us-central1"

echo "Using Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"

# 2. Build and Push using Cloud Build
echo "Building and pushing image to Artifact Registry..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "MODELS=$(grep MODELS .env | cut -d '=' -f2)" \
  --set-env-vars "API_KEYS=$(grep API_KEYS .env | cut -d '=' -f2)" \
  --set-env-vars "BASE_URLS=$(grep BASE_URLS .env | cut -d '=' -f2)"

echo "------------------------------------------------"
echo "Deployment Complete!"
