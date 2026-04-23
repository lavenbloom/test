import os

services = [
    {"name": "auth-service", "port": 8000, "has_db": True},
    {"name": "habit-service", "port": 8000, "has_db": True},
    {"name": "journal-service", "port": 8000, "has_db": True},
    {"name": "notification-service", "port": 8000, "has_db": True},
    {"name": "frontend", "port": 80, "has_db": False}
]

base_dir = "c:/Users/alina_2pzmzug/OneDrive/Desktop/PROJECT/helm-repo"

for srv in services:
    name = srv["name"]
    chart_dir = os.path.join(base_dir, f"{name}-chart")
    os.makedirs(os.path.join(chart_dir, "templates"), exist_ok=True)
    
    # Chart.yaml
    with open(os.path.join(chart_dir, "Chart.yaml"), "w") as f:
        f.write(f"""apiVersion: v2
name: {name}
description: Helm chart for {name}
type: application
version: 0.1.0
appVersion: "1.0.0"
""")

    # values.yaml
    with open(os.path.join(chart_dir, "values.yaml"), "w") as f:
        f.write(f"""replicaCount: 1
image:
  repository: myrepo/{name}
  pullPolicy: IfNotPresent
  tag: "latest"
service:
  type: ClusterIP
  port: {srv['port']}
""")

    # dev-values.yaml
    with open(os.path.join(chart_dir, "dev-values.yaml"), "w") as f:
        f.write(f"""replicaCount: 1
image:
  tag: "dev"
""")

    # prod-values.yaml
    with open(os.path.join(chart_dir, "prod-values.yaml"), "w") as f:
        f.write(f"""replicaCount: 3
image:
  tag: "prod"
""")

    # Deployment
    with open(os.path.join(chart_dir, "templates", "deployment.yaml"), "w") as f:
        f.write(f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{{{ .Release.Name }}}}-{name}
spec:
  replicas: {{{{ .Values.replicaCount }}}}
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
        - name: {name}
          image: "{{{{ .Values.image.repository }}}}:{{{{ .Values.image.tag }}}}"
          ports:
            - containerPort: {srv['port']}
          envFrom:
            - configMapRef:
                name: {{{{ .Release.Name }}}}-{name}-config
            - secretRef:
                name: {{{{ .Release.Name }}}}-{name}-secret
""")

    # Service
    with open(os.path.join(chart_dir, "templates", "service.yaml"), "w") as f:
        f.write(f"""apiVersion: v1
kind: Service
metadata:
  name: {name}-svc
spec:
  type: {{{{ .Values.service.type }}}}
  ports:
    - port: {srv['port']}
      targetPort: {srv['port']}
      protocol: TCP
  selector:
    app: {name}
""")

    # ConfigMap
    with open(os.path.join(chart_dir, "templates", "configmap.yaml"), "w") as f:
        if name == "frontend":
            f.write(f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {{{{ .Release.Name }}}}-{name}-config
data:
  REACT_APP_API_URL: "http://gateway.example.com"
""")
        else:
            db_name = name.split('-')[0] + "_db"
            f.write(f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {{{{ .Release.Name }}}}-{name}-config
data:
  POSTGRES_URI: "postgresql://user:password@{name}-db-0.{name}-db-svc.default.svc.cluster.local:5432/{db_name}"
""")

    # Secret
    with open(os.path.join(chart_dir, "templates", "secret.yaml"), "w") as f:
        f.write(f"""apiVersion: v1
kind: Secret
metadata:
  name: {{{{ .Release.Name }}}}-{name}-secret
type: Opaque
data:
  JWT_SECRET: c3VwZXJzZWNyZXRqd3RrZXk=
""")

    # StatefulSet & PVC for DB (if backend)
    if srv["has_db"]:
        with open(os.path.join(chart_dir, "templates", "statefulset.yaml"), "w") as f:
            f.write(f"""apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {name}-db
spec:
  serviceName: {name}-db-svc
  replicas: 1
  selector:
    matchLabels:
      app: {name}-db
  template:
    metadata:
      labels:
        app: {name}-db
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          value: "user"
        - name: POSTGRES_PASSWORD
          value: "password"
        - name: POSTGRES_DB
          value: "{name.split('-')[0]}_db"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: db-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: db-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
""")
        with open(os.path.join(chart_dir, "templates", "db-service.yaml"), "w") as f:
            f.write(f"""apiVersion: v1
kind: Service
metadata:
  name: {name}-db-svc
spec:
  clusterIP: None
  ports:
  - port: 5432
  selector:
    app: {name}-db
""")

print("Helm charts generated successfully.")
