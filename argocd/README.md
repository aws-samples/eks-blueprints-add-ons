# EKS SSP ArgoCD Add-ons

Sample App of App directory that can be used with ArgoCD. 

## Usage

To consume this repository, you must create create ArgoCD Application resource in your EKS cluster. Each individual add-on is enabled by specifying the `enabled` flag for that add-on. The code sample below demonstrate enabling every add-on. 

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: add-ons
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  destination:
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    repoURL: 'https://github.com/kcoleman731/argo-add-ons.git'
    path: chart
    targetRevision: HEAD
    helm:
      values: |
        region: {{ .Values.region }}
        account: {{ .Values.account }}
        clusterName: {{ .Values.clusterName }}
        agones:
            enable: true
        appmesh-controller:
            enable: true
        awsCalico:
            enable: true
        awsCloudWatchMetrics
            enable: true
        awsForFluentBit:
            enable: true
        awsLoadBalancerController:
            enable: true
        certManager:
            enable: true
        clusterAutoscaler:
            enable: true
        externalDns:
            enable: true
        gatekeeper:
            enable: true
        metricsServer:
            enable: true
        nginx:
            enable: true
        prometheus:
            enable: true
        traefik:
            enable: true
  syncPolicy:
    automated:
        prune: true
