# Lab 06 – Stateful Backends with Kubernetes: Database + API Integration

## Overview

In Lab 04, you learned the **guarantees** that StatefulSets provide:
- Stable, persistent pod identity
- Stable DNS names
- Persistent storage per pod
- Ordered deployment and scaling

In this lab, you'll **apply** those guarantees to build real systems that depend on them.

You'll work through three progressively independent sections:
1. **Fully Guided**: Build a complete PostgreSQL + FastAPI system (reference implementation)
2. **Semi-Guided**: Deploy a Redis cache system by completing partial manifests
3. **Independent**: Design and implement a task queue system from scratch

By the end of this lab, you'll understand **why** StatefulSets exist through hands-on practice with real application code, not just theory.

---

## Prerequisites

Before starting this lab, ensure you have:

- Kubernetes cluster running (Minikube, kind, or Docker Desktop)
- Docker installed and running
- kubectl configured and working
- **Docker Hub account** (free account at https://hub.docker.com)
- Basic understanding of StatefulSets from Lab 04

### Important: Docker Hub Workflow

**This lab uses Docker Hub as a container registry.** The workflow is:

1. **Build** the image locally with Docker
2. **Tag** the image with your Docker Hub username
3. **Push** the image to Docker Hub
4. **Pull** the image from Docker Hub when deploying to Kubernetes

**Why Docker Hub?**
- Matches production workflows used in real companies
- Works with any Kubernetes cluster (local or remote)
- Teaches proper container registry management
- Images are accessible from anywhere
- Free for public repositories

### Setup: Docker Hub Login

Before starting, log in to Docker Hub:

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

**Important**: Replace `<your-dockerhub-username>` with your actual Docker Hub username throughout this lab.

---

## Learning Objectives

By completing this lab, you will:

1. **Build** production-ready stateful applications with proper separation of concerns
2. **Apply** StatefulSet guarantees to real database and cache workloads
3. **Connect** stateless applications to stateful backends using DNS
4. **Demonstrate** data persistence and pod identity across failures
5. **Explain** why certain components need StatefulSets while others don't
6. **Design** a complete stateful system from requirements

---

## Lab Structure

This lab follows industry best practices with clear separation between application code and Kubernetes configuration:

```
lab-06-stateful-backend-architecture/
│
├── section-1-fully-guided/          # Complete reference implementation
│   ├── api/                          # FastAPI application
│   │   ├── main.py                   # Application code
│   │   ├── .env                      # Configuration
│   │   └── Dockerfile                # Container image
│   ├── postgres/                     # Database configuration
│   │   ├── init.sql                  # Schema (optional)
│   │   ├── .env                      # Database config
│   │   └── README.md                 # Documentation
│   └── k8s/                          # Kubernetes manifests
│       ├── postgres-headless.yaml
│       ├── postgres-statefulset.yaml
│       └── api-deployment.yaml
│
├── section-2-semi-guided/           # Partial implementation
│   ├── api/                          # Complete application
│   │   ├── main.py                   # Ready to use
│   │   ├── .env.example              # Template to fill
│   │   └── Dockerfile                # Ready to use
│   └── k8s/                          # Partial manifests
│       ├── redis-headless.yaml       # Fill TODOs
│       ├── redis-statefulset.yaml    # Fill TODOs
│       └── cache-api-deployment.yaml # Fill TODOs
│
├── section-3-independent/           # Design from scratch
│   ├── README.md                     # Requirements
│   └── design-decisions.md           # Template
│
└── lab.md                            # This document
```

---

## System Architecture

### The Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌────────────────────┐         ┌──────────────────────┐   │
│  │   API Deployment   │────────▶│  Database StatefulSet │   │
│  │   (FastAPI)        │         │                        │   │
│  │                    │         │  ┌──────┐  ┌──────┐   │   │
│  │  Replicas: 2       │         │  │ db-0 │  │ db-1 │   │   │
│  │  Stateless         │         │  └──┬───┘  └──┬───┘   │   │
│  └────────────────────┘         │     │         │        │   │
│                                  │  ┌──▼───┐  ┌─▼────┐   │   │
│  Uses DNS:                       │  │ PVC  │  │ PVC  │   │   │
│  db-0.db-headless                │  └──────┘  └──────┘   │   │
│                                  │                        │   │
│                                  │  Headless Service:     │   │
│                                  │  db-headless           │   │
│                                  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

**Database/Cache as a StatefulSet:**
- **Needs stable identity**: Each instance must have a predictable name
- **Needs persistent storage**: Data must survive pod restarts
- **Needs stable DNS**: Applications connect to specific instances
- **Order matters**: Initialization and replication require controlled startup

**API as a Deployment:**
- **Stateless**: No local data storage needed
- **Interchangeable**: Any API pod can handle any request
- **Scalable**: Can add/remove replicas freely
- **No identity needed**: Pods don't need stable names or DNS

This is a **fundamental pattern** in Kubernetes: stateful backends (databases, caches, queues) use StatefulSets, while stateless frontends (APIs, web servers) use Deployments.

---

## Section 1 – Fully Guided (Reference Implementation)

### Goal

Build a working PostgreSQL database + FastAPI system step-by-step. This section gives you a **complete reference** to understand how all pieces fit together in a production-ready structure.

**Key principle**: Application code is separate from Kubernetes manifests. No inline code in YAML files.

### Step 1.1: Understand the Application Structure

Navigate to the section-1-fully-guided directory:

```bash
cd section-1-fully-guided
```

Examine the structure:

```bash
tree
```

You should see:
- `api/` - FastAPI application with Dockerfile
- `postgres/` - Database configuration
- `k8s/` - Kubernetes manifests

**Important**: The API creates database tables automatically on startup. No manual `kubectl exec` commands needed.

### Step 1.2: Review the API Application

Examine the FastAPI application:

```bash
cat api/main.py
```

**Key features**:
- Connects to PostgreSQL using environment variables
- Creates database schema automatically on startup
- Implements retry logic for database connections
- Provides health check endpoints
- Uses proper error handling

Review the environment configuration:

```bash
cat api/.env
```

Notice the `DB_HOST` value: `postgres-0.postgres-headless` - this is the stable DNS name from the StatefulSet.

### Step 1.3: Build, Tag, and Push the API Docker Image

**Build the API container image:**

```bash
docker build -t user-api:1.0 ./api
```

Verify the image was created:

```bash
docker images | grep user-api
```

Expected output:
```
user-api    1.0    <image-id>    <time>    <size>
```

**Tag the image with your Docker Hub username:**

```bash
docker tag user-api:1.0 <your-dockerhub-username>/user-api:1.0
```

Replace `<your-dockerhub-username>` with your actual Docker Hub username.

Example:
```bash
docker tag user-api:1.0 johndoe/user-api:1.0
```

**Push the image to Docker Hub:**

```bash
docker push <your-dockerhub-username>/user-api:1.0
```

You'll see output showing the image layers being pushed:
```
The push refers to repository [docker.io/johndoe/user-api]
a1b2c3d4e5f6: Pushed
...
1.0: digest: sha256:abc123... size: 1234
```

**Update the Deployment manifest:**

Edit `k8s/api-deployment.yaml` and change the image field:

```yaml
# Change from:
image: user-api:1.0

# To:
image: <your-dockerhub-username>/user-api:1.0
```

Save the file.

### Step 1.4: Create the PostgreSQL Headless Service

A **headless Service** (ClusterIP: None) creates DNS records for individual pods instead of load-balancing.

Review the manifest:

```bash
cat k8s/postgres-headless.yaml
```

**Why headless?**
- Creates DNS: `postgres-0.postgres-headless.default.svc.cluster.local`
- Applications can connect to **specific** database pods
- No load balancing (databases handle their own replication)

Apply it:

```bash
kubectl apply -f k8s/postgres-headless.yaml
```

Verify:

```bash
kubectl get svc postgres-headless
```

Expected output:
```
NAME                TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
postgres-headless   ClusterIP   None         <none>        5432/TCP   5s
```

### Step 1.5: Create the PostgreSQL StatefulSet

Review the StatefulSet manifest:

```bash
cat k8s/postgres-statefulset.yaml
```

**Key StatefulSet features**:

1. **`serviceName: postgres-headless`**
   - Links StatefulSet to headless Service
   - Enables DNS: `<pod-name>.<service-name>`

2. **`volumeClaimTemplates`**
   - Creates one PVC per pod automatically
   - PVC names: `postgres-storage-postgres-0`, `postgres-storage-postgres-1`
   - PVCs persist even if pods are deleted

3. **Stable identity**
   - Pods named: `postgres-0`, `postgres-1`
   - Names never change, even after deletion

4. **Production features**
   - Resource limits
   - Liveness and readiness probes
   - Proper PostgreSQL configuration

Apply it:

```bash
kubectl apply -f k8s/postgres-statefulset.yaml
```

Watch pods start **in order**:

```bash
kubectl get pods -l app=postgres -w
```

You'll see:
1. `postgres-0` starts first
2. Only after `postgres-0` is Running, `postgres-1` starts

Press `Ctrl+C` to stop watching.

### Step 1.6: Verify StatefulSet Guarantees

**Guarantee 1: Stable Pod Names**

```bash
kubectl get pods -l app=postgres
```

Expected output:
```
NAME         READY   STATUS    RESTARTS   AGE
postgres-0   1/1     Running   0          2m
postgres-1   1/1     Running   0          1m
```

**Guarantee 2: Persistent Volumes Created**

```bash
kubectl get pvc
```

Expected output:
```
NAME                         STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
postgres-storage-postgres-0   Bound    pvc-abc123...                              1Gi        RWO            standard       2m
postgres-storage-postgres-1   Bound    pvc-def456...                              1Gi        RWO            standard       1m
```

Notice:
- **One PVC per pod**
- PVC names include pod name: `postgres-storage-postgres-0`
- Status: `Bound` (attached to a volume)

**Guarantee 3: Stable DNS**

Test DNS resolution using the fully qualified domain name:

```bash
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup postgres-0.postgres-headless.default.svc.cluster.local
```

Expected output:
```
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local

Name:      postgres-0.postgres-headless.default.svc.cluster.local
Address 1: 10.244.0.5 postgres-0.postgres-headless.default.svc.cluster.local
```

**DNS Name Breakdown:**
- `postgres-0` - Pod name (from StatefulSet ordinal)
- `postgres-headless` - Headless Service name
- `default` - Namespace
- `svc.cluster.local` - Cluster domain

**Short form in application code:**
Within the same namespace, your application can use the short form: `postgres-0.postgres-headless`

This DNS name is **stable** – it always points to `postgres-0`, even after restarts.

### Step 1.7: Deploy the API

Review the API Deployment manifest:

```bash
cat k8s/api-deployment.yaml
```

**Why a Deployment?**
- API is **stateless** – stores no data locally
- Pods are **interchangeable** – any pod can handle any request
- **Scalable** – can add/remove replicas without coordination
- **No persistent storage needed**

Notice:
- Uses the locally built image: `user-api:1.0`
- Environment variables point to `postgres-0.postgres-headless`
- Includes health checks and resource limits
- Also creates a Service for the API

Apply it:

```bash
kubectl apply -f k8s/api-deployment.yaml
```

Wait for pods to be ready:

```bash
kubectl get pods -l app=user-api
```

Expected output:
```
NAME                        READY   STATUS    RESTARTS   AGE
user-api-7f8d9c5b6d-abc12   1/1     Running   0          30s
user-api-7f8d9c5b6d-def34   1/1     Running   0          30s
```

Notice:
- **Random suffixes** (not `user-api-0`, `user-api-1`)
- Pods are **interchangeable**
- No PVCs created

### Step 1.8: Test the API

Port-forward to access the API:

```bash
kubectl port-forward svc/user-api 8000:8000
```

In a **new terminal**, test the endpoints:

**Health check:**

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"healthy","database":"connected","host":"postgres-0.postgres-headless"}
```

**Get users (initially empty or with seed data):**

```bash
curl http://localhost:8000/users
```

Expected output:
```json
{"users":[],"count":0}
```

**Create a new user:**

```bash
curl -X POST "http://localhost:8000/users?name=Alice&email=alice@example.com"
```

Expected output:
```json
{"user":{"id":1,"name":"Alice","email":"alice@example.com","created_at":"2024-01-07T..."},"message":"User created successfully"}
```

**Create more users:**

```bash
curl -X POST "http://localhost:8000/users?name=Bob&email=bob@example.com"
curl -X POST "http://localhost:8000/users?name=Charlie&email=charlie@example.com"
```

**Verify all users:**

```bash
curl http://localhost:8000/users
```

Expected output:
```json
{"users":[{"id":1,"name":"Alice","email":"alice@example.com",...},{"id":2,"name":"Bob",...},{"id":3,"name":"Charlie",...}],"count":3}
```

Stop the port-forward with `Ctrl+C` in the first terminal.

### Step 1.9: Critical Experiment – Database Pod Deletion

This experiment demonstrates **why** StatefulSets matter.

**Current state:**
- Database has 3 users
- API is connected and working

**Predict BEFORE executing:**
- Will the pod name change after deletion?
- Will the data persist?
- Will the API need reconfiguration?

**Delete the database pod:**

```bash
kubectl delete pod postgres-0
```

**Observe StatefulSet behavior:**

```bash
kubectl get pods -l app=postgres -w
```

You'll see:
1. `postgres-0` terminates
2. StatefulSet **immediately recreates** `postgres-0` (same name!)
3. New `postgres-0` pod starts

**Key observation:** The pod name is **identical** – `postgres-0` (not `postgres-2` or a random name).

Press `Ctrl+C` to stop watching.

**Check PVCs:**

```bash
kubectl get pvc
```

Expected output:
```
NAME                         STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
postgres-storage-postgres-0   Bound    pvc-abc123...                              1Gi        RWO            standard       10m
postgres-storage-postgres-1   Bound    pvc-def456...                              1Gi        RWO            standard       9m
```

**Critical insight:** The PVC `postgres-storage-postgres-0` is **still bound** to the same volume. The new pod reattaches to the **same storage**.

**Verify data persistence:**

Wait for `postgres-0` to be Running:

```bash
kubectl wait --for=condition=ready pod/postgres-0 --timeout=60s
```

**Test the API again:**

```bash
kubectl port-forward svc/user-api 8000:8000
```

In another terminal:

```bash
curl http://localhost:8000/users
```

Expected output:
```json
{"users":[{"id":1,"name":"Alice",...},{"id":2,"name":"Bob",...},{"id":3,"name":"Charlie",...}],"count":3}
```

**All data is intact!**

Stop the port-forward with `Ctrl+C`.

### Step 1.10: Why This Works

**StatefulSet guarantees applied:**

1. **Stable identity**
   - Pod recreated with **same name**: `postgres-0`
   - DNS remains valid: `postgres-0.postgres-headless`
   - API doesn't need to change configuration

2. **Persistent storage**
   - PVC `postgres-storage-postgres-0` survives pod deletion
   - New pod reattaches to **same PVC**
   - Data persists across restarts

3. **Predictable DNS**
   - API uses `postgres-0.postgres-headless`
   - DNS always resolves to the current `postgres-0` pod
   - No connection reconfiguration needed

**What would happen with a Deployment?**

If PostgreSQL ran as a Deployment:
- Pod would get a **new random name** after deletion
- DNS would break (no stable `postgres-0` name)
- PVC wouldn't automatically reattach (Deployments don't use volumeClaimTemplates)
- **Data would be lost**

This is **why** databases need StatefulSets.

### Step 1.11: Experiment – API Pod Deletion

Now delete an API pod:

```bash
# Get an API pod name
kubectl get pods -l app=user-api

# Delete one
kubectl delete pod <api-pod-name>
```

**Observe:**
- New pod gets a **different random name**
- No data loss (API is stateless)
- System continues working

This demonstrates that **stateless** applications work fine with Deployments.

---

## Section 2 – Semi-Guided (Guided Construction)

### Goal

Apply your understanding by **completing** partial manifests. You'll fill in missing fields based on StatefulSet concepts from Lab 04 and Section 1.

### Scenario

You're deploying a **Redis cache** as a StatefulSet with a Python API that reads/writes cache entries.

**Key difference from Section 1**: Application code is complete, but Kubernetes manifests have TODOs you must fill.

### Step 2.1: Navigate and Review

Navigate to the section-2-semi-guided directory:

```bash
cd ../section-2-semi-guided
```

Review the complete API application:

```bash
cat api/main.py
```

This API is **complete** – you don't modify it. It connects to Redis and provides cache operations.

### Step 2.2: Configure the API Environment

Copy the example environment file:

```bash
cp api/.env.example api/.env
```

Edit `api/.env` and fill in the values:

```bash
nano api/.env  # or your preferred editor
```

**Your task**: Fill in the correct Redis connection details:
- `REDIS_HOST`: What will be the stable DNS name for `redis-0`?
- `REDIS_PORT`: What port does Redis use?

**Hint**: Format is `<pod-name>.<headless-service-name>`

### Step 2.3: Build, Tag, and Push the Cache API Image

**Build the API container image:**

```bash
docker build -t cache-api:1.0 ./api
```

Verify the image was created:

```bash
docker images | grep cache-api
```

**Tag the image with your Docker Hub username:**

```bash
docker tag cache-api:1.0 <your-dockerhub-username>/cache-api:1.0
```

**Push the image to Docker Hub:**

```bash
docker push <your-dockerhub-username>/cache-api:1.0
```

**Update the Deployment manifest:**

Edit `k8s/cache-api-deployment.yaml` and change the image field:

```yaml
# Change from:
image: cache-api:1.0

# To:
image: <your-dockerhub-username>/cache-api:1.0
```

Save the file.

### Step 2.4: Complete the Redis Headless Service

Open the partial manifest:

```bash
cat k8s/redis-headless.yaml
```

You'll see TODOs for:
- App labels
- `clusterIP` value
- Selector

**Your tasks:**

1. Fill in the missing `app` label (metadata and selector)
2. Set `clusterIP` to make this a headless Service
3. Ensure the selector matches the pods you'll create

**Questions to answer BEFORE applying:**
- What value for `clusterIP` creates individual pod DNS records?
- What DNS name will `redis-0` have?

Edit the file:

```bash
nano k8s/redis-headless.yaml
```

**Solution hints** (try yourself first):
- Headless Service needs: `clusterIP: None`
- App label should be: `redis`
- DNS will be: `redis-0.redis-headless`

Save and apply:

```bash
kubectl apply -f k8s/redis-headless.yaml
```

Verify:

```bash
kubectl get svc redis-headless
```

Expected: `CLUSTER-IP` should show `None`.

### Step 2.5: Complete the Redis StatefulSet

Open the partial manifest:

```bash
cat k8s/redis-statefulset.yaml
```

You'll see TODOs for:
- `serviceName`
- Labels
- `replicas`
- Volume mount name
- VolumeClaimTemplate name
- Access mode
- Storage size

**Your tasks:**

1. Fill in `serviceName` to link to your headless Service
2. Complete all label fields consistently
3. Choose number of replicas
4. Name the volumeClaimTemplate (this becomes part of PVC names)
5. Set the correct `accessModes` (hint: only one pod writes to each volume)
6. Choose an appropriate storage size

**Questions to answer BEFORE applying:**
- What will the PVC names be? (Pattern: `<template-name>-<statefulset-name>-<ordinal>`)
- Which StatefulSet guarantee does `serviceName` enable?
- Why does Redis need persistent storage?

Edit the file:

```bash
nano k8s/redis-statefulset.yaml
```

**Solution hints** (try yourself first):
- `serviceName: redis-headless`
- All labels should be: `redis`
- `replicas: 2` (or your choice)
- Volume/template name: `redis-storage`
- Access mode: `ReadWriteOnce`
- Storage: `500Mi` or `1Gi`

Save and apply:

```bash
kubectl apply -f k8s/redis-statefulset.yaml
```

**Verify your work:**

```bash
# Check pods created in order
kubectl get pods -l app=redis -w
# Press Ctrl+C after both pods are Running

# Check PVCs created
kubectl get pvc

# Check DNS resolution (use FQDN for reliability)
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup redis-0.redis-headless.default.svc.cluster.local
```

### Step 2.6: Complete the API Deployment

Open the partial manifest:

```bash
cat k8s/cache-api-deployment.yaml
```

You'll see TODOs for:
- Number of replicas
- Labels
- `REDIS_HOST` environment variable

**Your tasks:**

1. Choose number of replicas (consider: is the API stateful?)
2. Complete all labels consistently
3. Set `REDIS_HOST` to the stable DNS name of `redis-0`

**Questions to answer BEFORE applying:**
- Why doesn't this API need a StatefulSet?
- What's the full DNS name for `redis-0`? (Format: `<pod>.<service>`)
- Could you scale this API to 5 replicas? Why or why not?

Edit the file:

```bash
nano k8s/cache-api-deployment.yaml
```

**Solution hints** (try yourself first):
- `replicas: 2` (or more - API is stateless)
- All labels should be: `cache-api`
- `REDIS_HOST: redis-0.redis-headless`

Save and apply:

```bash
kubectl apply -f k8s/cache-api-deployment.yaml
```

### Step 2.7: Test the Cache API

Port-forward to access the API:

```bash
kubectl port-forward svc/cache-api 8000:8000
```

In another terminal:

**Health check:**

```bash
curl http://localhost:8000/health
```

**Store a value:**

```bash
curl -X POST http://localhost:8000/cache/mykey/myvalue
```

Expected output:
```json
{"key":"mykey","value":"myvalue","status":"stored"}
```

**Retrieve it:**

```bash
curl http://localhost:8000/cache/mykey
```

Expected output:
```json
{"key":"mykey","value":"myvalue","status":"found"}
```

**Store more values:**

```bash
curl -X POST http://localhost:8000/cache/username/alice
curl -X POST http://localhost:8000/cache/session/abc123
```

**List all keys:**

```bash
curl http://localhost:8000/cache
```

### Step 2.8: Critical Experiment – Delete redis-0

**Predict BEFORE running:**
- Will the pod name change?
- Will the PVC be deleted?
- Will cached data persist?

**Delete the pod:**

```bash
kubectl delete pod redis-0
```

**Observe:**

```bash
kubectl get pods -l app=redis -w
```

Press `Ctrl+C` after `redis-0` is Running again.

**Verify your predictions:**

```bash
# Wait for pod to be ready
kubectl wait --for=condition=ready pod/redis-0 --timeout=60s

# Test the API again
curl http://localhost:8000/cache/mykey
```

**Expected**: Data persists! Redis was configured with AOF (Append-Only File) persistence.

**Reflection questions:**

1. Which StatefulSet guarantee prevented data loss?
2. Why didn't the API need reconfiguration after redis-0 restarted?
3. What would happen if you scaled the StatefulSet to 3 replicas?

---

## Section 3 – Independent (Mini Project)

### Goal

Design and implement a complete stateful system **from scratch**. No YAML provided – you make all architectural decisions.

### Navigate to Section 3

```bash
cd ../section-3-independent
```

### Read the Requirements

```bash
cat README.md
```

This file contains:
- Complete project requirements
- Success criteria
- Implementation steps
- Hints and examples
- Validation checklist

### Review the Design Template

```bash
cat design-decisions.md
```

This template guides you through:
- Architecture decisions
- Controller selection
- Network configuration
- Storage planning
- Failure recovery analysis

### Your Task

Build a **task queue system** with:

1. **A message queue** (Redis or PostgreSQL)
   - Must persist messages across restarts
   - Must have stable network identity
   - Must use appropriate controller type

2. **A worker application** (Python)
   - Connects to the queue
   - Processes messages
   - Must use appropriate controller type

### Success Criteria

Your system must demonstrate:

1. **Persistent message storage** – Messages survive pod deletion
2. **Stable identity** – Pod names don't change
3. **Correct storage reattachment** – PVCs persist and reattach
4. **Appropriate controller usage** – Justified StatefulSet vs Deployment choices

### Deliverables

1. Application code (Python files, Dockerfiles, .env files)
2. Kubernetes manifests (all YAML files)
3. Completed `design-decisions.md`
4. Test results (commands and output)

### Evaluation

Your project will be evaluated on:
- **Correctness** (40%) – System works as specified
- **Design Quality** (30%) – Proper use of Kubernetes primitives
- **Documentation** (20%) – Clear explanations and comments
- **Understanding** (10%) – Demonstrates mastery of concepts

**Refer to `README.md` in section-3-independent for complete details.**

---

## Cleanup

**Important:** StatefulSets do **not** automatically delete PVCs. You must clean them up manually.

### Cleanup Section 1

```bash
cd section-1-fully-guided

# Delete Deployment
kubectl delete -f k8s/api-deployment.yaml

# Delete StatefulSet
kubectl delete -f k8s/postgres-statefulset.yaml

# Delete Service
kubectl delete -f k8s/postgres-headless.yaml

# Manually delete PVCs
kubectl delete pvc postgres-storage-postgres-0
kubectl delete pvc postgres-storage-postgres-1
```

### Cleanup Section 2

```bash
cd ../section-2-semi-guided

# Delete Deployment
kubectl delete -f k8s/cache-api-deployment.yaml

# Delete StatefulSet
kubectl delete -f k8s/redis-statefulset.yaml

# Delete Service
kubectl delete -f k8s/redis-headless.yaml

# Manually delete PVCs
kubectl delete pvc redis-storage-redis-0
kubectl delete pvc redis-storage-redis-1
```

### Cleanup Section 3

```bash
cd ../section-3-independent

# Delete your resources
kubectl delete -f <your-files>

# Manually delete your PVCs
kubectl get pvc  # List them first
kubectl delete pvc <your-pvc-names>
```

### Verify Cleanup

```bash
kubectl get all
kubectl get pvc
kubectl get pv
```

All resources should be gone.

**Why manual PVC deletion?**
- Prevents accidental data loss
- Allows you to preserve data if needed
- Gives you explicit control over storage lifecycle

---

## Mental Model Summary

### What StatefulSets Guarantee

| Guarantee | What It Means | Why It Matters |
|-----------|---------------|----------------|
| **Stable Identity** | Pods have predictable names (e.g., `db-0`, `db-1`) | Applications can connect to specific instances |
| **Stable DNS** | Each pod gets a DNS name: `<pod>.<service>` | DNS names survive restarts |
| **Persistent Storage** | Each pod gets its own PVC via `volumeClaimTemplates` | Data survives pod deletion |
| **Ordered Operations** | Pods start/stop in sequence (0, 1, 2...) | Databases can initialize safely |

### What Deployments Guarantee

| Guarantee | What It Means | Why It Matters |
|-----------|---------------|----------------|
| **Interchangeable Pods** | All pods are identical and replaceable | Easy horizontal scaling |
| **Random Names** | Pods get random suffixes (e.g., `api-7f8d9c5b6d-abc12`) | No identity needed |
| **No Persistent Storage** | No automatic PVC creation | Suitable for stateless apps |
| **Parallel Operations** | All pods start/stop simultaneously | Fast scaling |

### The Fundamental Pattern

**Stateful backends (StatefulSet):**
- Databases, caches, message queues
- Need stable identity and persistent storage
- Connect via stable DNS: `<pod>.<headless-service>`

**Stateless frontends (Deployment):**
- APIs, web servers, workers
- No local state, interchangeable pods
- Connect to backends via DNS

**This pattern appears in nearly every production Kubernetes system.**

---

## Key Differences from Traditional Labs

### What's New in This Lab

1. **Real application code** – No inline code in YAML
2. **Proper file structure** – Separate directories for apps and manifests
3. **Docker images** – Build real containers locally
4. **Environment variables** – Configuration via .env files
5. **Production features** – Health checks, resource limits, proper error handling
6. **Automatic schema creation** – API handles database initialization

### Why This Matters

This lab structure matches what you'll see in real jobs:
- Application developers write code in their own repos
- DevOps engineers write Kubernetes manifests
- Clear separation of concerns
- Reproducible builds
- Version-controlled configuration

---

## Common Mistakes to Avoid

### Mistake 1: Using Deployment for a Database

**Why it fails:**
- Pods get random names → DNS breaks
- No automatic PVC creation → Data lost on restart
- No stable identity → Can't connect to specific instances

**Correct approach:** Use StatefulSet for databases, caches, queues.

### Mistake 2: Expecting PVCs to Auto-Delete

**The mistake:**
```bash
kubectl delete statefulset postgres
# Assumes PVCs are also deleted
```

**Reality:** PVCs persist to prevent accidental data loss.

**Correct approach:** Manually delete PVCs when you're sure you don't need the data.

### Mistake 3: Hardcoding IP Addresses

**The mistake:**
```yaml
env:
- name: DB_HOST
  value: "10.244.0.5"  # Pod IP - will change!
```

**Why it fails:** Pod IPs change on every restart.

**Correct approach:** Use DNS names:
```yaml
env:
- name: DB_HOST
  value: "postgres-0.postgres-headless"  # Stable DNS
```

### Mistake 4: Inline Application Code in YAML

**The mistake:**
```yaml
command: ["/bin/sh", "-c"]
args:
  - |
    pip install fastapi &&
    cat > /app/main.py <<'EOF'
    # 100 lines of Python code here...
```

**Why it's wrong:**
- Hard to maintain and version control
- No proper testing
- Doesn't match industry practices

**Correct approach:** Separate application code, build Docker images.

### Mistake 5: Forgetting the Headless Service

**The mistake:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless  # Service doesn't exist!
```

**Why it fails:** StatefulSet requires a headless Service to create DNS records.

**Correct approach:** Always create the headless Service **before** the StatefulSet.

### Mistake 6: Wrong Access Mode for PVCs

**The mistake:**
```yaml
volumeClaimTemplates:
- metadata:
    name: storage
  spec:
    accessModes: [ "ReadWriteMany" ]  # Allows multiple pods to write
```

**Why it's usually wrong:** Most databases can't handle multiple pods writing to the same volume simultaneously.

**Correct approach:** Use `ReadWriteOnce` for single-pod access.

---

## Reflection Questions

### Question 1: System Resilience

**Question:** Why does this system survive database pod restarts without losing data or requiring reconfiguration?

**Think about:**
- Which StatefulSet guarantee preserves data?
- Which guarantee keeps DNS valid?
- What would happen with a Deployment instead?

### Question 2: Identity Dependency

**Question:** What part of this system's design depends on stable pod identity?

**Think about:**
- How does the API find the database?
- What would break if pod names changed?
- Could you use a regular (non-headless) Service instead?

### Question 3: Controller Selection

**Question:** For each component below, which controller would you use and why?

- Web server serving static files
- PostgreSQL primary database
- Redis cache
- Nginx load balancer
- Kafka message broker
- React frontend application

**Think about:**
- Does it store state locally?
- Does it need stable identity?
- Does it need persistent storage?
- Are instances interchangeable?

### Question 4: Scaling Behavior

**Question:** What happens if you scale the PostgreSQL StatefulSet from 2 to 3 replicas?

**Think about:**
- What will the new pod be named?
- Will it get a PVC?
- Will it have a DNS name?
- Will it automatically replicate data from existing pods?

**Test it:**
```bash
kubectl scale statefulset postgres --replicas=3
kubectl get pods -l app=postgres
kubectl get pvc
```

---

## What You've Learned

By completing this lab, you've demonstrated the ability to:

✅ **Build production-ready stateful applications** with proper separation of concerns

✅ **Apply StatefulSet guarantees** to real workloads (databases, caches)

✅ **Connect stateless applications** to stateful backends using DNS

✅ **Demonstrate data persistence** across pod failures

✅ **Explain controller selection** based on workload requirements

✅ **Design complete systems** using appropriate Kubernetes primitives

### Key Takeaway

**StatefulSets exist to provide guarantees that certain applications depend on:**
- Databases need stable identity and persistent storage
- Caches need predictable DNS names
- Message queues need ordered startup and persistent state

**Deployments are for everything else:**
- APIs, web servers, workers that don't store state locally
- Applications where pods are interchangeable
- Workloads that scale horizontally without coordination

**The pattern you've learned is fundamental:**
- Stateful backends → StatefulSet
- Stateless frontends → Deployment
- Connect them via DNS
- Separate application code from Kubernetes configuration

This pattern appears in nearly every production Kubernetes system.

---

## Next Steps

Now that you understand StatefulSets through practice with real applications, you're ready to:

1. **Explore database replication** (primary-replica patterns with StatefulSets)
2. **Learn about Operators** (automated StatefulSet management)
3. **Study persistent volume types** (local vs network storage)
4. **Investigate backup strategies** for stateful workloads
5. **Implement CI/CD pipelines** for containerized applications

You've built a solid foundation. Keep applying these concepts to real systems.

---

## Additional Resources

### Kubernetes Documentation
- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

### Best Practices
- [Configuration Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

### Application Development
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [12-Factor App](https://12factor.net/)

---

**Congratulations on completing Lab 06!** You now understand how to build and deploy stateful applications in Kubernetes using industry best practices.
