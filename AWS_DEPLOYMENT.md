# AWS Deployment Guide for Anime Recommender System

This guide outlines the steps to deploy your Anime Recommender application on Amazon Web Services (AWS) using an EC2 instance, Docker, and Minikube.

> [!NOTE]
> **Free Tier Warning**: Minikube requires at least 2 vCPUs and 2GB of free memory. The standard AWS Free Tier instance (`t2.micro`) only provides 1 vCPU and 1GB RAM, which is **insufficient** and will likely cause the instance to crash.
>
> **Recommendation**: Use **`t2.medium`** (2 vCPUs, 4 GiB RAM) or **`t3.medium`** for a stable experience. This is not free but costs very little (~$0.04/hour) if you terminate the instance after testing.

---

## 1. Initial Setup: Create AWS EC2 Instance

### Step 1.1: Launch Instance
1.  Log in to the **AWS Management Console**.
2.  Navigate to **EC2** Dashboard.
3.  Click the orange **Launch instance** button.

### Step 1.2: Configure Instance Details
-   **Name**: `llmops-anime-server`
-   **OS Images (AMI)**: Select **Ubuntu** -> **Ubuntu Server 24.04 LTS (HVM), SSD Volume Type**.
-   **Instance Type**:
    -   Select **`t2.medium`** (Recommended for Kubernetes/Minikube).
    -   *If you strictly must try Free Tier (`t2.micro`), Minikube may fail to start.*
-   **Key Pair (Login)**:
    -   Click **Create new key pair**.
    -   Name: `llmops-key`.
    -   Type: `RSA`.
    -   Format: `.pem` (for OpenSSH).
    -   Click **Create key pair** and **download the file**. Keep this file safe!

### Step 1.3: Network Settings (Security Group)
-   Click **Edit** in the Network settings section.
-   **Security Group Name**: `llmops-sg`.
-   **Inbound Security Group Rules**:
    1.  **SSH** (TCP 22) - Source: `My IP` (or `0.0.0.0/0` for access from anywhere).
    2.  **Custom TCP** (TCP 8501) - Source: `0.0.0.0/0` (To access Streamlit app).
    3.  *(Optional)* **Custom TCP** (TCP 3000-10000) - Source: `0.0.0.0/0` (For Grafana/NodePort ranges if needed).

### Step 1.4: Storage
-   Change the storage size to **above 20 GiB** (e.g., `30 GiB`) to accommodate Docker images and Kubernetes clusters.
    -   *Note: Free tier allows up to 30 GB of EBS storage.*

### Step 1.5: Launch
-   Click **Launch instance**.
-   Wait for the "Instance state" to turn **Running**.

---

## 2. Connect to the VM

1.  Open your local terminal (or Git Bash on Windows).
2.  Navigate to the folder where you downloaded `llmops-key.pem`.
3.  Change permissions (required for SSH):
    ```bash
    chmod 400 llmops-key.pem
    ```
4.  Connect using the Public IPv4 address of your instance:
    ```bash
    ssh -i "llmops-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
    ```
    *(Type `yes` when asked about authenticity)*

---

## 3. Configure VM Instance

Once logged in, run the following commands to set up the environment.

### 3.1 Clone your Repository
```bash
git clone https://github.com/data-guru0/TESTING-9.git
cd TESTING-9
ls  # Verify project files
```

### 3.2 Install Docker
```bash
# Update packages
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# Create directory for keyrings
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add repo to Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify
sudo docker run hello-world
```

### 3.3 Configure Docker (Run without sudo)
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world  # Should work without sudo now
```

### 3.4 Enable Docker on Boot
```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

---

## 4. Configure Minikube

### 4.1 Install Minikube
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### 4.2 Start Minikube Cluster
```bash
# Start Minikube (uses Docker driver by default)
minikube start --driver=docker
```

### 4.3 Install kubectl
```bash
sudo snap install kubectl --classic
kubectl version --client
```

### 4.4 Check Status
```bash
minikube status
kubectl get nodes
```

---

## 5. Build and Deploy Application

### 5.1 Build Docker Image in Minikube
```bash
# Point your shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Build the image (this makes it available to the cluster)
docker build -t llmops-app:latest .
```

### 5.2 Create Secrets (API Keys)
Replace the quotes `""` with your actual keys.
```bash
kubectl create secret generic llmops-secrets \
  --from-literal=GROQ_API_KEY="your_groq_key_here" \
  --from-literal=HUGGINGFACEHUB_API_TOKEN="your_hf_token_here"
```

### 5.3 Deploy to Kubernetes
```bash
kubectl apply -f llmops-k8s.yaml
```

**Verify Deployment:**
```bash
kubectl get pods
# Wait until Status is 'Running'
```

---

## 6. Access the Application

Since this is a headless server (AWS EC2), we need to expose the port.

1.  **Start Minikube Tunnel** (Run in a separate terminal session or using background `&`):
    ```bash
    minikube tunnel
    ```
    *Note: If `minikube tunnel` asks for sudo password, provide it.*

2.  **Port Forward** (To expose K8s service to EC2 host port):
    In a new terminal window (connect via SSH again):
    ```bash
    kubectl port-forward svc/llmops-service 8501:80 --address 0.0.0.0
    ```

3.  **Open in Browser**:
    Go to `http://<YOUR_EC2_PUBLIC_IP>:8501`

---

## 7. Grafana Cloud Monitoring (Optional)

Setup is identical to the previous guide.

```bash
kubectl create ns monitoring

# Install Helm
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

# Create values.yaml with your Grafana credentials
nano values.yaml
# (Paste config from Grafana Cloud)

# Deploy Agent
helm repo add grafana https://grafana.github.io/helm-charts &&
helm repo update &&
helm upgrade --install --atomic --timeout 300s grafana-k8s-monitoring grafana/k8s-monitoring \
    --namespace "monitoring" --create-namespace --values values.yaml
```
