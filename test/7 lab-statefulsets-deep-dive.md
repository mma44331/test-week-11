# Lab 04: StatefulSets Deep Dive

## Overview

This lab explores StatefulSets through progressive learning. You'll work through the same system three times with decreasing guidance, building a mental model of how StatefulSets guarantee identity, storage, DNS, and ordering.

**What you'll build**: A 3-replica StatefulSet with persistent storage and stable network identity.

**What you'll learn**:
- How StatefulSets differ from Deployments at the implementation level
- Why Headless Services are required and what they provide
- How pod identity, DNS, and storage are guaranteed
- When StatefulSets are the right choice (and when they're not)

**Prerequisites**:
- Running Kubernetes cluster with dynamic volume provisioning
- `kubectl` configured and working
- Understanding of Pods, Services, Deployments, and PersistentVolumes

---

## Lab Structure

This lab has **three sections** that build the same system with different levels of guidance:

1. **Section 1 - Fully Guided**: Complete YAML, explicit commands, detailed explanations
2. **Section 2 - Semi-Guided**: Partial YAML, hints, guided discovery questions
3. **Section 3 - Independent**: Only objectives and validation criteria

**Recommendation**: Complete Section 1 fully before moving to Section 2. Complete Section 2 before attempting Section 3.

---

# SECTION 1: FULLY GUIDED

## 1.1 Setup and Context

### Create the Namespace

```bash
# Create a dedicated namespace for this lab to isolate resources and prevent conflicts
kubectl create namespace statefulset-lab

# Set the current context to use this namespace by default, ensuring all subsequent kubectl commands operate within it
kubectl config set-context --current --namespace=statefulset-lab
```

**Why a dedicated namespace?** Isolation makes cleanup easier and prevents conflicts with other workloads.

### The Problem StatefulSets Solve

Before writing any YAML, understand the problem:

**Deployments** create pods with:
- Random names: `web-7d8f9c-xk2p1`
- No guaranteed order of creation
- Interchangeable identities
- Shared or ephemeral storage

**StatefulSets** create pods with:
- Predictable names: `web-0`, `web-1`, `web-2`
- Sequential, ordered creation
- Stable, unique identities
- Dedicated persistent storage per pod

**When you need StatefulSets**:
- Databases requiring stable hostnames (MongoDB replica sets, Cassandra clusters)
- Distributed systems with leader election (Kafka, Zookeeper, etcd)
- Applications requiring stable storage tied to pod identity

**When you DON'T need StatefulSets**:
- Stateless web applications
- Worker queues where any pod can process any job
- Applications using external storage (S3, cloud databases)

---

## 1.2 Create the Headless Service

StatefulSets require a **Headless Service** for DNS-based pod discovery.

### What is a Headless Service?

A normal Service creates a single virtual IP that load-balances to pods. A Headless Service (`clusterIP: None`) creates individual DNS records for each pod instead.

**Normal Service DNS**:
```
my-service.my-namespace.svc.cluster.local → 10.96.1.5 (virtual IP)
```

**Headless Service DNS**:
```
my-service.my-namespace.svc.cluster.local → pod IPs directly
pod-0.my-service.my-namespace.svc.cluster.local → 10.244.1.10
pod-1.my-service.my-namespace.svc.cluster.local → 10.244.1.11
```

### Create headless-service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
  namespace: statefulset-lab
spec:
  clusterIP: None
  selector:
    app: nginx-stateful
  ports:
  - port: 80
    name: web
```

**Field explanations**:
- `clusterIP: None`: Makes this a Headless Service. No virtual IP is allocated.
- `selector: app: nginx-stateful`: Matches pods with this label. The StatefulSet will create pods with this label.
- `name: web`: Named ports enable service discovery and are required for StatefulSets.

### Apply and Verify

```bash
kubectl apply -f headless-service.yaml
kubectl get svc nginx-headless
```

**Expected output**:
```
NAME             TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
nginx-headless   ClusterIP   None         <none>        80/TCP    5s
```

**CHECKPOINT**: Notice `CLUSTER-IP` is `None`. This confirms it's a Headless Service.

---

## 1.3 Create the StatefulSet

### Create statefulset.yaml

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nginx-stateful
  namespace: statefulset-lab
spec:
  serviceName: "nginx-headless"
  replicas: 3
  selector:
    matchLabels:
      app: nginx-stateful
  template:
    metadata:
      labels:
        app: nginx-stateful
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
        command:
        - "/bin/sh"
        - "-c"
        - |
          echo "Pod: $HOSTNAME" > /usr/share/nginx/html/index.html
          echo "Date: $(date)" >> /usr/share/nginx/html/index.html
          nginx -g 'daemon off;'
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Mi
```

**Critical field explanations**:

- `serviceName: "nginx-headless"`: **Required**. Links this StatefulSet to the Headless Service for DNS. Without this, pods won't get stable DNS names.

- `replicas: 3`: Creates 3 pods named `nginx-stateful-0`, `nginx-stateful-1`, `nginx-stateful-2`.

- `selector.matchLabels`: Must match `template.metadata.labels`. This is how the StatefulSet identifies its pods.

- `volumeMounts`: Mounts the persistent volume into the container at `/usr/share/nginx/html`.

- `command`: Writes the pod's hostname to a file. This lets us verify that each pod keeps its identity and storage even after deletion.

- `volumeClaimTemplates`: **Key difference from Deployments**. Creates a separate PersistentVolumeClaim (PVC) for each pod. The PVC is named `www-nginx-stateful-0`, `www-nginx-stateful-1`, etc.

### Apply the StatefulSet

```bash
kubectl apply -f statefulset.yaml
```

---

## 1.4 Observe Ordered Pod Creation

StatefulSets create pods **sequentially**, not in parallel.

### Watch Pod Creation

```bash
kubectl get pods -w
```

**What you should observe**:

1. `nginx-stateful-0` appears first with status `Pending`
2. It transitions to `ContainerCreating`, then `Running`
3. Only after `nginx-stateful-0` is `Running` and `Ready` does `nginx-stateful-1` start
4. Same pattern for `nginx-stateful-2`

Press `Ctrl+C` to stop watching.

### Verify All Pods Are Running

```bash
kubectl get pods
```

**Expected output**:
```
NAME               READY   STATUS    RESTARTS   AGE
nginx-stateful-0   1/1     Running   0          2m
nginx-stateful-1   1/1     Running   0          1m
nginx-stateful-2   1/1     Running   0          30s
```

**STOP AND THINK**:
- Why does Kubernetes create pods sequentially instead of in parallel?
- What problems could occur if all pods started simultaneously in a database cluster?

**Answer**: Sequential creation ensures that the first pod (often the primary/leader in distributed systems) is fully operational before replicas start. This prevents split-brain scenarios and allows proper initialization order.

---

## 1.5 Verify Persistent Storage

Each pod should have its own PersistentVolumeClaim.

### List PVCs

```bash
kubectl get pvc
```

**Expected output**:
```
NAME                   STATUS   VOLUME                                     CAPACITY   ACCESS MODES
www-nginx-stateful-0   Bound    pvc-abc123...                              100Mi      RWO
www-nginx-stateful-1   Bound    pvc-def456...                              100Mi      RWO
www-nginx-stateful-2   Bound    pvc-ghi789...                              100Mi      RWO
```

**Observations**:
- Three separate PVCs, one per pod
- Naming pattern: `<volumeClaimTemplate-name>-<statefulset-name>-<ordinal>`
- Each is bound to a different PersistentVolume

### Verify Storage Content

Each pod wrote its hostname to `/usr/share/nginx/html/index.html`. Let's verify:

```bash
kubectl exec nginx-stateful-0 -- cat /usr/share/nginx/html/index.html
kubectl exec nginx-stateful-1 -- cat /usr/share/nginx/html/index.html
kubectl exec nginx-stateful-2 -- cat /usr/share/nginx/html/index.html
```

**Expected output** (each pod shows its own hostname):
```
Pod: nginx-stateful-0
Date: ...

Pod: nginx-stateful-1
Date: ...

Pod: nginx-stateful-2
Date: ...
```

**CHECKPOINT**: Each pod has unique content in its persistent volume.

---

## 1.6 Verify DNS Identity

StatefulSets provide stable DNS names for each pod.

### DNS Naming Pattern

Each pod gets a DNS name:
```
<pod-name>.<service-name>.<namespace>.svc.cluster.local
```

For our setup:
```
nginx-stateful-0.nginx-headless.statefulset-lab.svc.cluster.local
nginx-stateful-1.nginx-headless.statefulset-lab.svc.cluster.local
nginx-stateful-2.nginx-headless.statefulset-lab.svc.cluster.local
```

### Test DNS Resolution

Create a temporary pod to test DNS:

```bash
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
```

Inside the debug pod, run:

```sh
nslookup nginx-stateful-0.nginx-headless.statefulset-lab.svc.cluster.local
nslookup nginx-stateful-1.nginx-headless.statefulset-lab.svc.cluster.local
nslookup nginx-stateful-2.nginx-headless.statefulset-lab.svc.cluster.local
```

**Expected output**: Each DNS name resolves to the pod's IP address.

Also test the headless service itself:

```sh
nslookup nginx-headless.statefulset-lab.svc.cluster.local
```

**Expected output**: Returns all three pod IPs (not a single virtual IP).

Type `exit` to leave the debug pod.

**STOP AND THINK**:
- How is this different from a normal Service?
- Why would a database cluster need individual pod DNS names?

**Answer**: Normal Services provide a single entry point with load balancing. StatefulSets need individual pod addresses so replicas can connect to specific pods (e.g., connecting to the primary database node).

---

## 1.7 Test Pod Identity Persistence

The key feature of StatefulSets: **identity survives pod deletion**.

### Delete a Pod and watch its recreation

```bash
kubectl delete pod nginx-stateful-1 && kubectl get pods -w
```

* Use ; instead of && if using Powershell

**What you should observe**:
1. `nginx-stateful-1` enters `Terminating` state
2. After termination completes, a new `nginx-stateful-1` is created
3. The new pod gets the **same name**, **same ordinal**, and **same PVC**

Press `Ctrl+C` to stop watching.

### Verify Storage Persistence

```bash
kubectl exec nginx-stateful-1 -- cat /usr/share/nginx/html/index.html
```

**Expected output**:
```
Pod: nginx-stateful-1
Date: ...
```

**CRITICAL OBSERVATION**: The date is the **original** date from when the pod was first created, not the current time. This proves the new pod reattached to the same persistent volume.

### Verify DNS Persistence

```bash
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
```

Inside the debug pod:

```sh
nslookup nginx-stateful-1.nginx-headless.statefulset-lab.svc.cluster.local
```

The DNS name still resolves (though the IP may have changed if the pod was rescheduled to a different node).

Type `exit` to leave the debug pod.

**STOP AND THINK**:
- What would happen with a Deployment if you deleted a pod?
- Why is this identity persistence critical for databases?

**Answer**: With a Deployment, a new pod would get a random name and potentially different storage. For databases, losing identity means losing the ability to rejoin a cluster or maintain replication relationships.

---

## 1.8 Test Ordered Scaling

StatefulSets scale **in order** when scaling up and **in reverse order** when scaling down.

### Scale Up

```bash
kubectl scale statefulset nginx-stateful --replicas=5 ; kubectl get pods -w
```

**What you should observe**:
1. `nginx-stateful-3` is created first
2. Only after it's `Running` and `Ready`, `nginx-stateful-4` is created
3. Two new PVCs are created: `www-nginx-stateful-3` and `www-nginx-stateful-4`

Press `Ctrl+C` to stop watching.

### Verify New PVCs

```bash
kubectl get pvc
```

You should see 5 PVCs total.

### Scale Down

```bash
kubectl scale statefulset nginx-stateful --replicas=2 ; kubectl get pods -w
```

**What you should observe**:
1. `nginx-stateful-4` is deleted first
2. Only after it's fully terminated, `nginx-stateful-3` is deleted
3. Deletion happens in **reverse ordinal order** (highest to lowest)

Press `Ctrl+C` to stop watching.

### Check PVCs After Scale Down

```bash
kubectl get pvc
```

**CRITICAL OBSERVATION**: You still see 5 PVCs, not 2.

**Why?** StatefulSets **never automatically delete PVCs** when scaling down. This is a safety feature to prevent accidental data loss. If you scale back up, the pods will reattach to their original PVCs.

**STOP AND THINK**:
- Why is reverse-order deletion important?
- What could go wrong if Kubernetes deleted PVCs automatically?

**Answer**: Reverse-order deletion ensures the most recently added replicas (often the least critical) are removed first. Auto-deleting PVCs would cause permanent data loss if someone accidentally scaled down.

---

## 1.9 Test Scale-Up with Existing PVCs

Let's verify that scaling back up reuses the existing PVCs.

### Scale Back Up

```bash
kubectl scale statefulset nginx-stateful --replicas=5
kubectl get pods -w
```

Wait for all pods to be `Running`.

### Verify PVC Reuse

```bash
kubectl exec nginx-stateful-3 -- cat /usr/share/nginx/html/index.html
kubectl exec nginx-stateful-4 -- cat /usr/share/nginx/html/index.html
```

**Expected output**: The original content from when these pods first existed (before scaling down).

**CHECKPOINT**: This proves that StatefulSets maintain the relationship between pod identity and storage across scale operations.

---

## 1.10 Understanding Update Strategies

StatefulSets support different update strategies. Let's observe the default behavior.

### Check Current Update Strategy

```bash
kubectl get statefulset nginx-stateful -o yaml | grep -A 5 updateStrategy
```

**Expected output**:
```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 0
```

**What this means**:
- `RollingUpdate`: Pods are updated one at a time in reverse ordinal order
- `partition: 0`: All pods will be updated (no pods are "partitioned" off)

### Update the Image

```bash
kubectl set image statefulset/nginx-stateful nginx=nginx:1.22
kubectl get pods -w
```

**What you should observe**:
1. `nginx-stateful-4` is terminated and recreated first (highest ordinal)
2. After it's `Running` and `Ready`, `nginx-stateful-3` is updated
3. This continues in reverse order down to `nginx-stateful-0`

Press `Ctrl+C` to stop watching.

**STOP AND THINK**:
- Why update in reverse order (4, 3, 2, 1, 0) instead of forward order?
- What would happen if pod-0 is the primary database node?

**Answer**: Reverse order updates ensure the primary/leader (typically pod-0) is updated last, maintaining cluster stability. If pod-0 were updated first, the cluster might lose its leader during the update.

---

## 1.11 Cleanup Section 1

Before moving to Section 2, clean up the resources:

```bash
kubectl delete statefulset nginx-stateful
kubectl delete svc nginx-headless
kubectl delete pvc --all
```

**Note**: You must manually delete PVCs. They are not automatically removed when you delete the StatefulSet.

Verify cleanup:

```bash
kubectl get all
kubectl get pvc
```

Both should show no resources (or only the debug pod if it's still running).

---

# SECTION 2: SEMI-GUIDED

In this section, you'll build the same system, but with incomplete YAML. You must fill in the missing fields based on what you learned in Section 1.

## 2.1 Setup

```bash
kubectl config set-context --current --namespace=statefulset-lab
```

---

## 2.2 Create the Headless Service

Here's the partial YAML. Fill in the missing fields:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-headless
  namespace: statefulset-lab
spec:
  clusterIP: ___________  # What value makes this a Headless Service?
  selector:
    app: ___________  # What label will your StatefulSet pods have?
  ports:
  - port: 80
    name: ___________  # Choose a descriptive name for this port
```

**Hints**:
- What special value for `clusterIP` creates a Headless Service?
- The selector must match the labels on your StatefulSet pods
- Port names should be descriptive (e.g., "web", "http", "api")

**Validation**:
```bash
kubectl apply -f headless-service.yaml
kubectl get svc web-headless
```

**Success criteria**: `CLUSTER-IP` column shows `None`.

---

## 2.3 Create the StatefulSet

Fill in the missing fields:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
  namespace: statefulset-lab
spec:
  serviceName: "___________"  # Which service provides DNS for this StatefulSet?
  replicas: ___________  # How many pods do you want?
  selector:
    matchLabels:
      app: ___________  # Must match template.metadata.labels
  template:
    metadata:
      labels:
        app: ___________  # Must match selector.matchLabels
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: ___________
          name: ___________
        volumeMounts:
        - name: ___________  # Must match volumeClaimTemplates.metadata.name
          mountPath: /usr/share/nginx/html
        command:
        - "/bin/sh"
        - "-c"
        - |
          echo "Pod: $HOSTNAME" > /usr/share/nginx/html/index.html
          echo "Timestamp: $(date)" >> /usr/share/nginx/html/index.html
          nginx -g 'daemon off;'
  volumeClaimTemplates:
  - metadata:
      name: ___________  # Choose a name for the volume claim
    spec:
      accessModes: [ "___________" ]  # What access mode for single-pod volumes?
      resources:
        requests:
          storage: ___________  # How much storage per pod?
```

**Guided questions**:

1. **serviceName**: What's the name of the Headless Service you created in 2.2?

2. **replicas**: How many pods do you want to create? (Suggestion: start with 3)

3. **selector and labels**: These must match. What label did you use in the Headless Service selector?

4. **containerPort**: What port does nginx listen on?

5. **volumeMounts.name**: This must match the name in `volumeClaimTemplates.metadata.name`. Choose a descriptive name like "data" or "storage".

6. **accessModes**: For volumes that only one pod can write to, use `ReadWriteOnce`.

7. **storage**: How much storage does each pod need? (100Mi is reasonable for this lab)

**Validation**:
```bash
kubectl apply -f statefulset.yaml
kubectl get pods -w
```

**Success criteria**:
- Pods are created sequentially (web-0, then web-1, then web-2)
- All pods reach `Running` status
- Each pod has its own PVC

---

## 2.4 Verify Your Work

### Check Pod Creation Order

**Question**: Did the pods create in sequential order or in parallel?

```bash
kubectl get pods
```

### Check PVCs

**Question**: How many PVCs were created? What are their names?

```bash
kubectl get pvc
```

**Expected pattern**: `<volumeClaimTemplate-name>-<statefulset-name>-<ordinal>`

### Check Storage Content

**Question**: Does each pod have unique content in its persistent volume?

```bash
kubectl exec web-0 -- cat /usr/share/nginx/html/index.html
kubectl exec web-1 -- cat /usr/share/nginx/html/index.html
kubectl exec web-2 -- cat /usr/share/nginx/html/index.html
```

**What should you see?** Each pod should display its own hostname.

---

## 2.5 Test DNS Resolution

Create a debug pod:

```bash
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
```

**Task**: Test DNS resolution for each pod. What command should you use?

**Hint**: The DNS pattern is `<pod-name>.<service-name>.<namespace>.svc.cluster.local`

**Questions to answer**:
1. What DNS name resolves to web-0?
2. What DNS name resolves to the headless service?
3. Does the headless service return a single IP or multiple IPs?

Type `exit` when done.

---

## 2.6 Test Identity Persistence

**Task**: Delete pod `web-1` and observe what happens.

**Questions**:
1. What command deletes a specific pod?
2. What name does the replacement pod get?
3. Does the new pod reattach to the same PVC?
4. How can you verify the storage persisted?

**Hint**: Check the timestamp in the index.html file. If it's the original timestamp (not current), storage persisted.

---

## 2.7 Test Scaling

### Scale Up

**Task**: Scale the StatefulSet to 5 replicas.

**Questions**:
1. What command scales a StatefulSet?
2. In what order are the new pods created?
3. How many new PVCs are created?

### Scale Down

**Task**: Scale back down to 2 replicas.

**Questions**:
1. In what order are pods deleted?
2. What happens to the PVCs of deleted pods?
3. Why doesn't Kubernetes automatically delete them?

### Scale Back Up

**Task**: Scale back up to 4 replicas.

**Questions**:
1. Do the recreated pods get new PVCs or reuse existing ones?
2. How can you verify this?

---

## 2.8 Cleanup Section 2

**Task**: Delete all resources you created in this section.

**Hint**: You need to delete:
1. The StatefulSet
2. The Headless Service
3. All PVCs (manually)

**Validation**: Run `kubectl get all` and `kubectl get pvc`. Both should show no resources.

---

# SECTION 3: INDEPENDENT

In this section, you'll design and implement a StatefulSet-based system from scratch with only objectives and constraints.

## 3.1 Objectives

Build a StatefulSet-based system that demonstrates:
1. Stable pod identity
2. Persistent storage per pod
3. Stable DNS names
4. Ordered pod creation and deletion
5. Identity persistence across pod recreation

## 3.2 Constraints

Your system must include:

- **Namespace**: `statefulset-lab`
- **Headless Service**: Choose your own name
- **StatefulSet**: Choose your own name
- **Replicas**: At least 3 pods
- **Container**: Use any image that can write to a file (nginx, busybox, alpine, etc.)
- **Storage**: Each pod must have its own persistent volume (at least 50Mi)
- **Identity Proof**: Each pod must write something unique to its persistent volume that proves its identity

## 3.3 Success Criteria

Your implementation must pass these tests:

### Test 1: Pod Naming
```bash
kubectl get pods
```
**Success**: Pods have predictable names with ordinals (e.g., `myapp-0`, `myapp-1`, `myapp-2`).

### Test 2: Sequential Creation
**Success**: When you create the StatefulSet, pods are created one at a time in order (0, then 1, then 2).

### Test 3: Persistent Storage
```bash
kubectl get pvc
```
**Success**: Each pod has its own PVC with a predictable name pattern.

### Test 4: Storage Content
**Success**: Each pod has unique, identifiable content in its persistent volume that proves which pod wrote it.

### Test 5: DNS Resolution
```bash
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside the pod, test DNS for each StatefulSet pod
```
**Success**: Each pod has a stable DNS name that resolves to its IP.

### Test 6: Identity Persistence
**Success**: When you delete a pod, the replacement pod:
- Gets the same name
- Reattaches to the same PVC
- The persistent volume contains the original content (not new content)

### Test 7: Ordered Scaling Up
**Success**: When you scale up, new pods are created sequentially in order.

### Test 8: Ordered Scaling Down
**Success**: When you scale down, pods are deleted in reverse order (highest ordinal first).

### Test 9: PVC Retention
**Success**: When you scale down, PVCs are NOT automatically deleted.

### Test 10: PVC Reuse
**Success**: When you scale back up, pods reattach to their original PVCs (original content is still there).

## 3.4 Design Questions

Before you start coding, answer these questions:

1. **What makes a Service "headless"?**

2. **Why does a StatefulSet need a Headless Service?**

3. **What field in the StatefulSet spec links it to the Headless Service?**

4. **How are PVC names generated for StatefulSet pods?**

5. **What happens if you delete a StatefulSet pod?**

6. **What happens if you delete the entire StatefulSet?**

7. **What happens to PVCs when you scale down?**

8. **In what order are pods created during scale-up?**

9. **In what order are pods deleted during scale-down?**

10. **How do you prove that a pod reattached to the same storage after deletion?**

## 3.5 Implementation

You're on your own. Create the necessary YAML files and apply them.

**Hints**:
- Start with the Headless Service
- Then create the StatefulSet
- Use `kubectl get pods -w` to observe behavior
- Use `kubectl describe` to debug issues

## 3.6 Validation

Run through all 10 success criteria tests above. Document your observations.

## 3.7 Cleanup

Delete all resources you created:
- StatefulSet
- Headless Service
- All PVCs

---

# CONCEPT SUMMARY

## What StatefulSets Guarantee

### 1. Stable Pod Identity
- Pods get predictable names: `<statefulset-name>-<ordinal>`
- Ordinals start at 0 and increment sequentially
- Identity persists across pod recreation

### 2. Stable Network Identity
- Each pod gets a stable DNS name via the Headless Service
- DNS pattern: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`
- DNS name persists even if pod IP changes

### 3. Stable Storage
- Each pod gets its own PersistentVolumeClaim via `volumeClaimTemplates`
- PVC naming: `<volumeClaimTemplate-name>-<statefulset-name>-<ordinal>`
- PVCs persist across pod deletion and StatefulSet scaling

### 4. Ordered Operations
- **Creation**: Pods created sequentially (0, 1, 2, ...)
- **Deletion**: Pods deleted in reverse order (..., 2, 1, 0)
- **Updates**: Pods updated in reverse order by default
- Next pod only starts after previous pod is Running and Ready

## How StatefulSets Work

### Components
1. **StatefulSet Controller**: Manages pod lifecycle
2. **Headless Service**: Provides DNS records for each pod
3. **PersistentVolumeClaims**: Provide stable storage per pod

### Key Behaviors
- StatefulSet controller watches for desired vs actual state
- Creates pods one at a time in order
- Waits for each pod to be Ready before creating the next
- Reattaches pods to their original PVCs after deletion
- Never automatically deletes PVCs (safety feature)

### DNS Implementation
- Headless Service (clusterIP: None) creates DNS records for each pod
- DNS records are updated when pods are created/deleted
- Allows direct pod-to-pod communication using stable names

---

# COMMON MISTAKES

## 1. Forgetting the Headless Service
**Mistake**: Creating a StatefulSet without a Headless Service.

**Symptom**: Pods start but don't get stable DNS names.

**Fix**: Always create a Headless Service first and reference it in `spec.serviceName`.

## 2. Mismatched Labels
**Mistake**: Service selector doesn't match StatefulSet pod labels.

**Symptom**: DNS doesn't resolve to pods.

**Fix**: Ensure `service.spec.selector` matches `statefulset.spec.template.metadata.labels`.

## 3. Wrong serviceName
**Mistake**: `spec.serviceName` doesn't match the Headless Service name.

**Symptom**: Pods don't get stable DNS names.

**Fix**: `spec.serviceName` must exactly match the Headless Service metadata.name.

## 4. Expecting Automatic PVC Deletion
**Mistake**: Assuming PVCs are deleted when scaling down or deleting the StatefulSet.

**Symptom**: PVCs accumulate and consume storage quota.

**Fix**: Manually delete PVCs when you're sure you don't need the data. This is by design to prevent data loss.

## 5. Using StatefulSets for Stateless Apps
**Mistake**: Using StatefulSets for applications that don't need stable identity or storage.

**Symptom**: Unnecessary complexity, slower deployments, wasted storage.

**Fix**: Use Deployments for stateless applications. Only use StatefulSets when you need stable identity, stable DNS, or persistent storage per pod.

## 6. Not Understanding Ordered Operations
**Mistake**: Expecting all pods to start simultaneously.

**Symptom**: Slow startup times, confusion about why pods aren't starting.

**Fix**: Understand that sequential startup is intentional. If you need parallel startup, you probably don't need a StatefulSet.

## 7. Incorrect volumeClaimTemplates
**Mistake**: Forgetting `volumeClaimTemplates` or using `volumes` instead.

**Symptom**: All pods share the same volume or have no persistent storage.

**Fix**: Use `volumeClaimTemplates` (not `volumes`) to create a separate PVC per pod.

## 8. Wrong Access Mode
**Mistake**: Using `ReadWriteMany` when `ReadWriteOnce` is sufficient.

**Symptom**: Deployment fails if storage provider doesn't support RWX.

**Fix**: Use `ReadWriteOnce` for pod-specific storage. Only use `ReadWriteMany` if multiple pods truly need to write to the same volume simultaneously.

---

# INTERVIEW-STYLE REASONING QUESTIONS

## Question 1: When to Use StatefulSets
**Scenario**: Your team is deploying a new microservice that processes messages from a queue. Each instance pulls messages, processes them, and updates a central database. Should you use a StatefulSet or Deployment?

**Answer**: Use a **Deployment**. This is a stateless workload where:
- Pods are interchangeable (any pod can process any message)
- No stable identity is needed
- No pod-specific storage is required
- Parallel startup is fine

StatefulSets would add unnecessary complexity.

## Question 2: PVC Lifecycle
**Scenario**: You have a 5-replica StatefulSet. You scale down to 2 replicas, then delete the entire StatefulSet. What happens to the PVCs?

**Answer**: All 5 PVCs still exist. StatefulSets never automatically delete PVCs because:
- Prevents accidental data loss
- Allows you to scale back up and reattach to original data
- Gives you explicit control over data lifecycle

You must manually delete PVCs when you're certain you don't need the data.

## Question 3: DNS Resolution
**Scenario**: You have a 3-replica StatefulSet named `db` with a Headless Service named `db-svc` in namespace `prod`. What DNS name would you use to connect to the second replica (db-1) from another pod in the same namespace?

**Answer**: `db-1.db-svc.prod.svc.cluster.local` (or the short form `db-1.db-svc` from within the same namespace).

The pattern is: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`

## Question 4: Update Strategy
**Scenario**: You have a 5-replica MongoDB StatefulSet where pod-0 is the primary. You update the container image. In what order are pods updated and why?

**Answer**: Pods are updated in reverse order: 4, 3, 2, 1, 0.

**Why**: This ensures the primary (pod-0) is updated last, maintaining cluster stability. If pod-0 were updated first, the cluster would lose its primary during the update, potentially causing downtime.

## Question 5: Identity Persistence
**Scenario**: Pod `web-2` in a StatefulSet crashes and is automatically restarted by Kubernetes. What guarantees does the new pod have?

**Answer**: The new pod is guaranteed to have:
1. **Same name**: `web-2` (not a random name)
2. **Same ordinal**: 2
3. **Same PVC**: Reattaches to `www-web-2` (or whatever the PVC name pattern is)
4. **Same DNS name**: `web-2.<service-name>.<namespace>.svc.cluster.local`

This is the core value of StatefulSets: identity survives pod recreation.

## Question 6: Scaling Behavior
**Scenario**: You have a 3-replica StatefulSet. You scale to 6 replicas, then immediately scale to 4 replicas before all 6 pods are Running. What happens?

**Answer**: 
1. Pods 3, 4, 5 start creating sequentially
2. When the scale-down command is issued, Kubernetes stops creating new pods
3. Any pods that are already Running are deleted in reverse order
4. Final state: 4 pods (0, 1, 2, 3)

Kubernetes always respects the most recent desired state.

## Question 7: Headless Service Purpose
**Scenario**: Why can't you use a normal (non-headless) Service with a StatefulSet?

**Answer**: You technically can, but you lose the key benefit of stable DNS names for individual pods. A normal Service:
- Provides a single virtual IP
- Load-balances traffic across all pods
- Doesn't create DNS records for individual pods

StatefulSets need individual pod DNS names so clients can connect to specific pods (e.g., connecting to the primary database node, or a specific shard in a distributed system).

## Question 8: Storage Class
**Scenario**: Your StatefulSet's `volumeClaimTemplates` doesn't specify a `storageClassName`. What happens?

**Answer**: Kubernetes uses the **default StorageClass** in the cluster. If no default StorageClass exists, PVC creation fails and pods remain in `Pending` state.

**Best practice**: Explicitly specify `storageClassName` in production to avoid surprises.

## Question 9: Pod Deletion Policy
**Scenario**: You delete a StatefulSet with `kubectl delete statefulset myapp`. What happens to the pods?

**Answer**: By default, pods are deleted in reverse order (highest ordinal first), waiting for each to fully terminate before deleting the next. This is the same as scaling to 0.

You can use `--cascade=orphan` to delete the StatefulSet without deleting pods (advanced use case).

## Question 10: Parallel Deployment
**Scenario**: Your application doesn't need ordered deployment. Can you make StatefulSet pods start in parallel?

**Answer**: Yes, set `spec.podManagementPolicy: Parallel`. This makes pods start simultaneously, but they still maintain stable identity and storage.

**When to use**: When you need stable identity/storage but don't need ordered startup (e.g., a sharded cache where shards are independent).

---

# FINAL REFLECTION

## What You Should Understand Now

1. **StatefulSets vs Deployments**: StatefulSets provide stable identity, stable DNS, and persistent storage per pod. Deployments provide interchangeable pods with random names.

2. **When to Use StatefulSets**: Databases, distributed systems, and any application requiring stable identity or pod-specific storage.

3. **When NOT to Use StatefulSets**: Stateless applications, worker queues, web servers, APIs that don't maintain local state.

4. **The Role of Headless Services**: Provide stable DNS names for individual pods, enabling direct pod-to-pod communication.

5. **PVC Lifecycle**: PVCs are never automatically deleted. This is a safety feature to prevent data loss.

6. **Ordered Operations**: Sequential creation and reverse-order deletion ensure stability for distributed systems.

7. **Identity Persistence**: Pod name, DNS name, and storage persist across pod recreation.

## Next Steps

- Explore StatefulSet update strategies (`RollingUpdate` with `partition`)
- Learn about `podManagementPolicy: Parallel` for non-ordered deployments
- Study real-world StatefulSet examples (MongoDB, Cassandra, Kafka)
- Understand StatefulSet limitations (e.g., no automatic failover, manual PVC management)

---

**Lab Complete!** You now have a deep understanding of how StatefulSets work and when to use them.
