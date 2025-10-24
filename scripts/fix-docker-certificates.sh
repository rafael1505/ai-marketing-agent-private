#!/bin/bash
# This script helps fix Docker certificate issues in corporate environments

# Set colors for console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Docker Corporate Certificate Fix ===${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run this script as root (use sudo).${NC}"
  exit 1
fi

echo -e "This script will help fix Docker certificate issues in corporate environments."
echo -e "It will allow Docker to pull images from Docker Hub through your corporate proxy."
echo

# Step 1: Configure Docker daemon to accept insecure registries
echo -e "Step 1: Configuring Docker daemon..."

mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOT'
{
  "insecure-registries": ["registry-1.docker.io"],
  "allow-nondistributable-artifacts": true
}
EOT

echo -e "${GREEN}✅ Created /etc/docker/daemon.json${NC}"

# Step 2: Set up Docker proxy settings
echo -e "\nStep 2: Setting up Docker proxy configuration..."

# Ask for proxy details
read -p "Enter your corporate HTTP proxy (e.g., http://proxy.example.com:8080): " HTTP_PROXY
read -p "Enter your corporate HTTPS proxy (e.g., http://proxy.example.com:8080): " HTTPS_PROXY
read -p "Enter domains to bypass (comma separated, e.g., localhost,127.0.0.1,.internal): " NO_PROXY

# Create the systemd override directory
mkdir -p /etc/systemd/system/docker.service.d/

# Create the http-proxy.conf file
cat > /etc/systemd/system/docker.service.d/http-proxy.conf << EOT
[Service]
Environment="HTTP_PROXY=${HTTP_PROXY}"
Environment="HTTPS_PROXY=${HTTPS_PROXY}"
Environment="NO_PROXY=${NO_PROXY}"
EOT

echo -e "${GREEN}✅ Created proxy configuration for Docker daemon${NC}"

# Step 3: Configure Docker client
echo -e "\nStep 3: Configuring Docker client..."

mkdir -p /root/.docker
cat > /root/.docker/config.json << EOT
{
  "proxies": {
    "default": {
      "httpProxy": "${HTTP_PROXY}",
      "httpsProxy": "${HTTPS_PROXY}",
      "noProxy": "${NO_PROXY}"
    }
  }
}
EOT

echo -e "${GREEN}✅ Created Docker client configuration${NC}"

# Step 4: Add Philips CA certificates if available
echo -e "\nStep 4: Adding corporate certificates..."

mkdir -p /etc/docker/certs.d/registry-1.docker.io/

echo -e "${YELLOW}Would you like to add a corporate CA certificate? (y/n)${NC}"
read ADD_CERT

if [[ "$ADD_CERT" == "y" || "$ADD_CERT" == "Y" ]]; then
  read -p "Enter the path to your corporate CA certificate file: " CA_CERT_PATH
  if [ -f "$CA_CERT_PATH" ]; then
    cp "$CA_CERT_PATH" /etc/docker/certs.d/registry-1.docker.io/ca.crt
    echo -e "${GREEN}✅ Added corporate certificate${NC}"
  else
    echo -e "${RED}Certificate file not found. Skipping...${NC}"
  fi
else
  echo -e "${YELLOW}Skipping certificate setup.${NC}"
fi

# Step 5: Restart Docker
echo -e "\nStep 5: Restarting Docker service..."

systemctl daemon-reload
systemctl restart docker

echo -e "${GREEN}✅ Docker service restarted${NC}"

# Check if Docker is running
if systemctl is-active --quiet docker; then
  echo -e "\n${GREEN}Docker is running!${NC}"
else
  echo -e "\n${RED}Docker service failed to start. Please check your settings.${NC}"
  exit 1
fi

# Test Docker connectivity
echo -e "\nTesting Docker connectivity..."
docker info > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Docker daemon is responding${NC}"
else
  echo -e "${RED}❌ Docker daemon is not responding properly${NC}"
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "You should now be able to pull images from Docker Hub."
echo -e "Test with: ${YELLOW}docker pull hello-world${NC}"
echo
