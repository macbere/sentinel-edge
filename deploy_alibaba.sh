#!/bin/bash
set -e

echo "🚀 Alibaba Cloud Deployment Script for Sentinel Edge"
echo "===================================================="
echo ""

# Check if user is logged in to Alibaba Cloud CLI
if ! command -v aliyun &> /dev/null; then
    echo "❌ Alibaba Cloud CLI not found."
    echo "📦 Install it from: https://www.alibabacloud.com/help/en/cli/install-aliyun-cli"
    exit 1
fi

# Configuration
REGION="us-west-1"  # Change to your preferred region
INSTANCE_TYPE="ecs.t6-c1m1.large"  # 2 vCPU, 2GB RAM - sufficient for edge AI
IMAGE_ID="ubuntu_22_04_x64_20G_alibase_20231221.vhd"
SECURITY_GROUP="sg-sentinel-edge"
KEY_PAIR="sentinel-edge-key"

echo "📋 Deployment Configuration:"
echo "   Region: $REGION"
echo "   Instance Type: $INSTANCE_TYPE"
echo "   OS: Ubuntu 22.04"
echo ""

# Step 1: Build Docker image locally
echo "🔨 Step 1: Building Docker image..."
docker build -t sentinel-edge:latest .
echo "✅ Docker image built successfully"
echo ""

# Step 2: Create ECS instance (if not exists)
echo "🖥️  Step 2: Checking/Creating ECS instance..."
INSTANCE_ID=$(aliyun ecs DescribeInstances \
    --RegionId $REGION \
    --InstanceName "sentinel-edge-server" \
    --output cols=InstanceId rows=Instances.Instance[] | tail -n +2)

if [ -z "$INSTANCE_ID" ]; then
    echo "   Creating new ECS instance..."
    INSTANCE_ID=$(aliyun ecs CreateInstance \
        --RegionId $REGION \
        --InstanceType $INSTANCE_TYPE \
        --ImageId $IMAGE_ID \
        --InstanceName "sentinel-edge-server" \
        --SecurityGroupId $SECURITY_GROUP \
        --KeyPairName $KEY_PAIR \        --InternetMaxBandwidthOut 5 \
        --output cols=InstanceId | tail -n +2)
    echo "✅ Instance created: $INSTANCE_ID"
    
    # Allocate public IP
    aliyun ecs AllocatePublicIpAddress --InstanceId $INSTANCE_ID
    PUBLIC_IP=$(aliyun ecs DescribeInstanceAttribute --InstanceId $INSTANCE_ID --output cols=PublicIpAddress rows=PublicIpAddress.IpAddress[] | tail -n +2)
    echo "✅ Public IP: $PUBLIC_IP"
else
    echo "✅ Using existing instance: $INSTANCE_ID"
    PUBLIC_IP=$(aliyun ecs DescribeInstanceAttribute --InstanceId $INSTANCE_ID --output cols=PublicIpAddress rows=PublicIpAddress.IpAddress[] | tail -n +2)
fi
echo ""

# Step 3: Deploy application
echo "📤 Step 3: Deploying application to ECS..."
echo "   Copying files to server..."
scp -i ~/.ssh/$KEY_PAIR.pem -r ./* root@$PUBLIC_IP:/opt/sentinel-edge/

echo "   Installing dependencies on server..."
ssh -i ~/.ssh/$KEY_PAIR.pem root@$PUBLIC_IP << 'REMOTE_EOF'
    cd /opt/sentinel-edge
    apt-get update
    apt-get install -y docker.io docker-compose
    systemctl start docker
    systemctl enable docker
    
    # Build and run container
    docker build -t sentinel-edge .
    docker run -d \
        --name sentinel-edge \
        --restart unless-stopped \
        -p 5000:5000 \
        --env-file .env \
        sentinel-edge
    
    echo "✅ Application deployed successfully"
REMOTE_EOF

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "===================================================="
echo "🌐 Access your application at: http://$PUBLIC_IP:5000"
echo "📊 Dashboard: http://$PUBLIC_IP:5000/dashboard"
echo "❤️  Health Check: http://$PUBLIC_IP:5000/health"
echo ""
echo "📝 Next Steps:"
echo "   1. Update .env on server with your Qwen API key"
echo "   2. Restart container: docker restart sentinel-edge"
echo "   3. Test endpoints with curl"echo ""
