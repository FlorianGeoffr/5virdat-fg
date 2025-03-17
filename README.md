# 🚀 Projet E5 - Déploiement Kubernetes de Rocket-Ecommerce  

## 📌 Introduction  

Dans le cadre du **Projet E5 5VIRDAT - ESTIAM BOURGES**, nous avons été intégrés à une équipe **SRE (Site Reliability Engineering)** au sein d’une grande entreprise française. Notre mission est de répondre aux besoins d’un futur client souhaitant tester une **architecture Kubernetes** avant une éventuelle migration complète vers cette solution.  

### 📢 **Contexte du projet**  
Le client possède une **application e-commerce critique** qui reçoit du trafic sur les ports **80 et 443**. Deux équipes travaillent sur cette application et souhaitent pouvoir tester leurs développements **sans impacter l’environnement de production**.  

Les principaux besoins sont les suivants :  
✅ **Isoler trois environnements distincts** : `dev`, `preprod` et `prod`.  
✅ **Optimiser et dockeriser l’application** pour minimiser la taille et accélérer le déploiement.  
✅ **Utiliser Stripe** pour les paiements en ligne avec des clés API adaptées à chaque environnement.  
✅ **Gérer un backend avec une base de données MySQL**.  
✅ **Automatiser le déploiement avec des manifestes Kubernetes uniquement** (pas d’interface manuelle).  

### 🎯 **Objectif du projet**  
L’objectif est de concevoir une **maquette grandeur nature** du déploiement de l’application e-commerce en **utilisant Kubernetes**. Une fois cette maquette validée, le client pourra envisager une migration complète vers cette architecture.  

Nous allons donc :  
1️⃣ **Optimiser l’application et créer une image Docker allégée**.  
2️⃣ **Pousser cette image sur Docker Hub** pour faciliter son déploiement.  
3️⃣ **Déployer l’application dans un cluster Kubernetes** avec une gestion multi-environnements.  
4️⃣ **Expliquer clairement chaque composant utilisé** et fournir une documentation détaillée.  

### 📂 **Livrables attendus**  
📌 Un dépôt Git contenant l’ensemble des fichiers du projet.   
📌 Un rapport détaillé expliquant les choix techniques et l’implémentation.  

---  


# Étape 1 : Récupération et optimisation de l’application Rocket-Ecommerce

## Récupération de l’application  

L’application a été récupérée depuis son dépôt GitLab.  

## Optimisation de l’image Docker  

L’optimisation de l’image Docker a été réalisée comme suit :  

### 1. Utilisation d'une base image plus légère  
- **Avant** : `python:3.11.5` (basé sur Debian)  
- **Après** : `python:3.11.5-alpine` (basé sur Alpine, beaucoup plus léger)  

### 2. Réduction des couches  
- Fusion des `COPY . .` pour éviter de copier plusieurs fois le projet.  
- Réduction du nombre de `RUN` en chaînant les commandes avec `&&` pour limiter le nombre de couches créées.  

### 3. Suppression de paquets inutiles  
- Plus besoin d’installer `ca-certificates`, `curl`, `gnupg`, etc.  
- Alpine gère nativement l’installation de `nodejs` et `npm` via `apk add`.  

### 4. Installation plus efficace des dépendances  
- Plus besoin d’ajouter manuellement les clés GPG et les sources pour Node.js.  
- Installation directe de `nodejs` et `npm` via `apk`.  

### 5. Réduction de la taille finale de l’image  

![image](https://github.com/user-attachments/assets/f49edfc3-c5c4-4e9b-abf7-30886c4972a7)


- **Avant** : `1.42GB`  
- **Après** : `327MB`  
- **Gain de poids** : `-77%` 🚀  
- Alpine étant minimaliste (~30MB contre ~900MB pour Debian), cela réduit considérablement le temps de build et le poids du conteneur.  

# Étape 2 : Push de l'image optimisée sur Docker Hub  

Après optimisation, l’image Docker doit être poussée sur **Docker Hub** afin d’être utilisée dans notre déploiement.  

## Commandes pour push sur Docker Hub :  

## Se connecter à Docker Hub
docker login

## Taguer l'image
docker tag rocket-ecommerce:latest floriangeoffr/rocket-ecommerce:latest

## Pousser l'image sur Docker Hub
docker push floriangeoffr/rocket-ecommerce:latest


![image](https://github.com/user-attachments/assets/2901a901-9d54-480a-94d3-ea21f4c2b595)

# Étape 3 : Déploiement Kubernetes de Rocket-Ecommerce

📌 **Introduction**  
Cette étape détaille le déploiement de **Rocket-Ecommerce** dans un cluster Kubernetes avec une gestion multi-environnements (**dev**, **preprod**, **prod**).  

Chaque environnement est :  
- Isolé dans son propre **namespace**  
- Dispose d’un **ConfigMap** pour sa configuration  
- Utilise un **Deployment** pour exécuter les pods  
- Exposé via un **Service**  

---


## Démarrage de Minikube  

Avant de déployer notre application sur **Kubernetes**, nous devons démarrer **Minikube**, qui nous permet de créer un cluster Kubernetes local.  

Utilisez la commande suivante pour **lancer Minikube** avec les paramètres optimaux :  

```sh
minikube start --listen-address=0.0.0.0 --memory=max --cpus=max --kubernetes-version=v1.32.0
```

## 🚀 1. Création des Namespaces  
Les **namespaces** permettent de séparer les environnements pour éviter les conflits et faciliter la gestion des ressources.  

Chaque namespace correspond à un environnement spécifique :  

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dev
---
apiVersion: v1
kind: Namespace
metadata:
  name: preprod
---
apiVersion: v1
kind: Namespace
metadata:
  name: prod
```

- **dev** : Environnement de développement.
- **preprod** : Environnement de pré-production pour les tests avant la mise en prod.
- **prod** : Environnement de production.


## 🛠 2. Configuration avec ConfigMaps  
Les ConfigMaps stockent les variables d’environnement spécifiques à chaque environnement.  
Ils permettent de modifier la configuration sans reconstruire l’image Docker.  

### 🔹 ConfigMap pour DEV

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rocket-ecommerce-config
  namespace: dev
data:
  DEBUG: "TRUE"
  FLASK_APP: "run.py"
  FLASK_DEBUG: "True"
  STRIPE_SECRET_KEY: "sk_test_DEV"
  STRIPE_PUBLISHABLE_KEY: "pk_test_DEV"
  SERVEUR_ADDRESS: "http://localhost:5005/"
```

(Même configuration pour PREPROD et PROD avec le namespace adapté.)

## 📦 3. Déploiement avec Deployments

Le Deployment définit comment les pods sont déployés et gérés par Kubernetes.  
Il s’assure que l’application est toujours disponible et permet de faire des mises à jour sans interruption.

### 🔹 Deployment pour DEV

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rocket-ecommerce-deployment
  namespace: dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rocket-ecommerce
  template:
    metadata:
      labels:
        app: rocket-ecommerce
    spec:
      containers:
      - name: rocket-ecommerce
        image: floriangeoffr/rocket-ecommerce:latest
        ports:
        - containerPort: 5005
        envFrom:
        - configMapRef:
            name: rocket-ecommerce-config
```

(Même configuration pour PREPROD et PROD avec le namespace adapté.)



## 🌐 4. Exposition de l’application avec Services  
Les Services exposent l’application aux utilisateurs en attribuant un port unique par environnement.  

### 🔹 Service pour DEV (Port 30081)  
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rocket-ecommerce-service
  namespace: dev
spec:
  selector:
    app: rocket-ecommerce
  type: NodePort
  ports:
    - port: 80
      targetPort: 5005
      nodePort: 30081
```
     
     

### 🔹 Service pour PREPROD (Port 30082)  
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rocket-ecommerce-service
  namespace: preprod
spec:
  selector:
    app: rocket-ecommerce
  type: NodePort
  ports:
    - port: 80
      targetPort: 5005
      nodePort: 30082
```

### 🔹 Service pour PROD (Port 30083)  
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rocket-ecommerce-service
  namespace: prod
spec:
  selector:
    app: rocket-ecommerce
  type: NodePort
  ports:
    - port: 80
      targetPort: 5005
      nodePort: 30083
```

# 🔍 VERIFICATION DU DEPLOIEMENT  

Une fois le déploiement terminé, nous devons vérifier que tous les composants fonctionnent correctement.  

## ✅ 1️⃣ Vérification des Namespaces  
Assurez-vous que les namespaces `dev`, `preprod` et `prod` sont bien créés :  

```sh
kubectl get namespaces
```
![image](https://github.com/user-attachments/assets/22a50fc2-1635-4b84-913c-d3603332b43b)

## ✅ 2️⃣ Vérification des Pods  

Chaque environnement (**dev**, **preprod**, **prod**) doit exécuter un **pod** contenant l'application **Rocket-Ecommerce**.  

Utilisez la commande suivante pour vérifier l'état des pods dans chaque namespace :  

```sh
kubectl get pods -n dev
kubectl get pods -n preprod
kubectl get pods -n prod
```
![image](https://github.com/user-attachments/assets/294e1dec-3718-431d-8ddc-af4c11eb84b3)

## ✅ 3️⃣ Vérification des Services  

Les **Services** permettent d’exposer l’application aux utilisateurs en **routant le trafic** vers les pods correspondants.  

Utilisez les commandes suivantes pour vérifier les services déployés dans chaque environnement :  

```sh
kubectl get services -n dev
kubectl get services -n preprod
kubectl get services -n prod
```
![image](https://github.com/user-attachments/assets/dfd50e6b-c586-4351-bd4c-ed04e2681090)


## ✅ 4️⃣ Vérification des Logs des Conteneurs  

Pour s’assurer que l’application fonctionne correctement et ne génère pas d’erreurs, nous pouvons **analyser les logs** du pod en cours d’exécution.



## ✅ 5️⃣ Validation de fonctionnement des pages  

Une fois les pods et services déployés, nous devons tester l'accès à l'application **Rocket-Ecommerce** pour chaque environnement (`dev`, `preprod`, `prod`).  

---

### 🛠 Accès à l’environnement **DEV**  

Forward du port pour accéder à l'application depuis le navigateur :  

```sh
kubectl port-forward --address 0.0.0.0 pod/$(kubectl get pod -l app=rocket-ecommerce -n dev -o jsonpath="{.items[0].metadata.name}") -n dev 5005:5005
```

Accès à l'application DEV via l'IP publique de la VM avec le port 5005 :

📌 Ouvrir dans un navigateur :
http://<IP-PUBLIQUE-VM>:5005

🖼 Capture d’écran de l’application DEV en fonctionnement :
![image](https://github.com/user-attachments/assets/72c5a8ab-a256-41a7-8f8f-da228bd5b273)




### 🛠 Accès à l’environnement **PREPROD**  

Forward du port pour accéder à l'application depuis le navigateur :  

```sh
kubectl port-forward --address 0.0.0.0 pod/$(kubectl get pod -l app=rocket-ecommerce -n preprod -o jsonpath="{.items[0].metadata.name}") -n preprod 5006:5005
```

Accès à l'application PREPROD via l'IP publique de la VM avec le port 5006 :

📌 Ouvrir dans un navigateur :
http://<IP-PUBLIQUE-VM>:5006

🖼 Capture d’écran de l’application PREPROD en fonctionnement :
![image](https://github.com/user-attachments/assets/df75342f-952e-4ff3-a943-36096409cecd)


### 🛠 Accès à l’environnement **PROD**  

Forward du port pour accéder à l'application depuis le navigateur :  

```sh
kubectl port-forward --address 0.0.0.0 pod/$(kubectl get pod -l app=rocket-ecommerce -n prod -o jsonpath="{.items[0].metadata.name}") -n prod 5007:5005
```

Accès à l'application PROD via l'IP publique de la VM avec le port 5007 :

📌 Ouvrir dans un navigateur :
http://<IP-PUBLIQUE-VM>:5007

🖼 Capture d’écran de l’application PREPROD en fonctionnement :
![image](https://github.com/user-attachments/assets/4875ca95-4362-4841-b7e3-e2e459a54c19)






## ✅ 5️⃣ Vérification de l'intégration avec l'API Stripe  

L’application **Rocket-Ecommerce** utilise **Stripe** comme passerelle de paiement. Nous allons vérifier que les transactions sont bien enregistrées sur le **dashboard Stripe** après un achat dans l’environnement de **production**.  



![image](https://github.com/user-attachments/assets/02d7a3d3-6132-40e7-b91a-24713aecce4a)
![image](https://github.com/user-attachments/assets/c25a3ecf-4e06-4327-b00d-7d256af3731b)

Après l'achat, les transactions doivent apparaître dans le dashboard Stripe :

![image](https://github.com/user-attachments/assets/75be3887-443b-49f6-a88f-b34830d75218)





📌 **Commande pour afficher les logs de l’application Rocket-Ecommerce** :  

```sh
kubectl logs -n dev pod/$(kubectl get pod -l app=rocket-ecommerce -n dev -o jsonpath="{.items[0].metadata.name}")
```


🎯 **Résumé du déploiement**  

📄 **Manifest complet disponible**  
Le fichier YAML complet du déploiement Kubernetes est disponible à la racine du projet sous le nom :  

**`manifest-rocket-ecommerce.yaml`**

1️⃣ **Création des Namespaces** (`dev`, `preprod`, `prod`) pour isoler les environnements.  
2️⃣ **Configuration via ConfigMaps** pour adapter l’application à chaque environnement.  
3️⃣ **Déploiement via Deployments** pour assurer la haute disponibilité des pods.  
4️⃣ **Exposition via Services** en attribuant des ports spécifiques pour chaque environnement.  

✅ **Conclusion**  
Avec cette architecture Kubernetes, l’application *Rocket-Ecommerce* est séparée en trois environnements bien distincts.  
Chaque mise à jour peut être testée en *preprod* avant d’aller en *prod*, garantissant un déploiement sécurisé et sans interruption. 🚀  


# Adminlte-pro

## Introduction

Cette deuxième application, **Django-Adminlte**, est une application Django qui fonctionne avec une base de données MySQL. Pour des raisons de temps, l'application est uniquement déployée dans le namespace `dev`.

## Étapes du Déploiement

### Téléchargement du Manifest YAML

Clone le fichier YAML contenant les configurations nécessaires avec `git clone`.

### Application du Manifest

Applique le manifest sur le namespace `dev` :
```bash
kubectl apply -f django-adminlte.yaml
```
## Utilisation des Secrets

Dans ce manifest, nous utilisons un **Secret** Kubernetes pour stocker des informations sensibles telles que des mots de passe et des clés d'API. Ces données sont encodées en base64 afin de garantir leur sécurité et de ne pas les exposer en texte clair.

## Création de la Base de Données

Après avoir appliqué le manifest, une base de données MySQL est nécessaire. Pour cela, j’ai forcé la création de la base de données en accédant au pod de l’application et en exécutant les migrations Django :

```bash
kubectl exec -it django-adminlte-deployment-67df864757-sqtvh -n dev -- /bin/bash
python manage.py migrate
```

![image](https://github.com/user-attachments/assets/8940e642-cf77-4d1b-86b0-e20d5dcb4a48)




