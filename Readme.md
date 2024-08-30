# Flask Kubernetes Deployment

This guide explains how I created a simple kubernetes deployment of a Flask application, and tested it using `kubectl`.

## Step 1: Create a Namespace

First, I created a namespace to isolate my resources:

```bash
kubectl create namespace borakostem-flask
```

## Step 2: Dockerize the Flask Application

I created a `Dockerfile` for my Flask application:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-alpine # I have used alpine for lighter image

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run main.py when the container launches
CMD ["flask", "run"]
```

Then, I built and pushed the Docker image to my Harbor registry:


## Step 3: Create a Kubernetes Secret for Harbor Credentials

I created a Kubernetes secret to store my Harbor credentials:

```bash
kubectl create secret docker-registry harbor-secret \
  --docker-username=my-harbor-username \
  --docker-password=my-harbor-password \
  --docker-server=my-harbor-url.com \
  --docker-email=my-harbor-email@kostem.net \
  --namespace=borakostem-flask
```

## Step 4: Deploy the Flask Application

I created a `deployment.yaml` file to define my Flask application deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask
  namespace: borakostem-flask
  labels:
    app: flask
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
      - name: flask
        image: my-harbor-url.com/borakostem/flask-kube:latest
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
        ports:
        - containerPort: 5000
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 3
          periodSeconds: 10
          timeoutSeconds: 5
      imagePullSecrets:
        - name: harbor-secret

```

I applied the deployment:

```bash
kubectl apply -f deployment.yaml
```

## Step 5: Expose the Application via a Service

I created a `service.yaml` file to expose my application internally in the cluster:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-service
  namespace: borakostem-flask
spec:
  selector:
    app: flask
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
  clusterIP: None

```

I applied the service configuration:

```bash
kubectl apply -f service.yaml
```


## Step 6: Set Up Horizontal Pod Autoscaler

I created a `hpa.yaml` file to define the Horizontal Pod Autoscaler for my Flask application:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flask-hpa
  namespace: borakostem-flask
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flask
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

I applied the HPA configuration:

```bash
kubectl apply -f hpa.yaml
```


This setup ensures that my Flask application automatically scales between 2 to 5 replicas based on CPU utilization.

## Step 7: Verify the Deployment

I verified that the service and pods were running correctly:

```bash
kubectl get service flask-service -n borakostem-flask
```

Output:
```
NAME            TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
flask-service   ClusterIP   None         <none>        80/TCP    8m22s
```

```bash
kubectl get pods -n borakostem-flask
```

Output:
```
NAME                    READY   STATUS    RESTARTS   AGE
flask-654c8cf97-4l7rk   1/1     Running   0          10m
flask-654c8cf97-vvjjf   1/1     Running   0          10m
```

## Step 7: Test the Application

I described the pod to ensure it was running correctly:

```bash
kubectl describe pod flask-654c8cf97-vvjjf -n borakostem-flask
```

I opened a terminal session in the pod and tested the service:

```bash
kubectl exec -it flask-654c8cf97-vvjjf -n borakostem-flask -- /bin/sh
```

Inside the pod, I ran:

```sh
curl http://flask-service:5000
```

Output:
```
An awesome Kubernetes app with Flask!
```

The application was accessible via port 5000. Inside the cluster.

## Setp 8: Accessing the Service Externally

After configuring the service to use a NodePort, I verified that the service is accessible externally. Here are the steps I followed to access the service from outside the cluster:

1. **Get Node Information**:
   I retrieved the details of the nodes in my Kubernetes cluster to find their internal IP addresses.


2. **Access the Service Externally**:
   Using the internal IP of one of the nodes and the NodePort (30001), I accessed the Flask application from my local machine:

   ```bash
   curl http://192.168.210.102:30001
   ```

   Output:
   ```plaintext
   An awesome Kubernetes app with Flask!
   ```

This confirmed that the service is correctly set up and accessible both within the Kubernetes cluster and externally via the NodePort.