#!/bin/bash

echo "Set up K3s..."

is_k3s_installed() {
  if command -v k3s > /dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Install k3s if it is not already installed
if is_k3s_installed; then
  echo "K3s is already installed, moving on.."
else
  echo "K3s not found, installing..."
  curl -sfL https://get.k3s.io | sh -

  # Check if k3s was installed successfully
  if [ $? -ne 0 ]; then
    echo "K3s installation failed."
    exit 1
  fi

  echo "K3s installed successfully."

  # Wait for k3s to be fully up and running
  echo "Waiting for K3s to be ready..."
  sleep 30
fi

echo "Creating namespaces..."

# Function to create a namespace if it doesn't exist
create_namespace() {
  local ns=$1
  if kubectl get namespace "$ns" > /dev/null 2>&1; then
    echo "Namespace '$ns' already exists."
  else
    echo "Creating namespace '$ns'..."
    kubectl create namespace "$ns"
    if [ $? -ne 0 ]; then
      echo "Failed to create namespace '$ns'."
      exit 1
    fi
    echo "Namespace '$ns' created successfully."
  fi
}

# Create namespaces
create_namespace "gen"
create_namespace "edit"


echo "Adding localhost as an insecure registry for containers..."

REGISTRIES_CONF="/etc/containers/registries.conf"
NEW_REGISTRY="
[[registry]]
insecure = true
location = \"localhost:5000\"
"

# Check if the entry already exists
if grep -q 'location = "localhost:5000"' "$REGISTRIES_CONF"; then
    echo "The registry entry for localhost:5000 already exists in $REGISTRIES_CONF."
else
    # Append the new registry configuration
    echo "Adding the new registry entry to $REGISTRIES_CONF."
    echo "$NEW_REGISTRY" | sudo tee -a "$REGISTRIES_CONF" > /dev/null

    if [ $? -eq 0 ]; then
        echo "The new registry entry has been added successfully."
    else
        echo "Failed to add the new registry entry."
    fi
fi

echo "Spinning up the local registry..."

# Check if the container 'registry' is already running
if [ "$(podman ps -q -f name=registry)" ]; then
    echo "Container 'registry' is already running."
else
    # Check if the container 'registry' exists but is not running
    if [ "$(podman ps -aq -f name=registry)" ]; then
        echo "Container 'registry' exists but is not running. Starting the container..."
        podman start registry
    else
        echo "Container 'registry' does not exist. Creating and running the container..."
        podman run -d -p 5000:5000 --name registry registry:2.7
    fi
fi
if [ $? -ne 0 ]; then
  echo "Failed to create local registry."
  exit 1
fi



echo "=================================="
echo "Kubernetes configuration set up successfully."
