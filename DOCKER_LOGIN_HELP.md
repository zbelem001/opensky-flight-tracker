# 🐳 Configuration Docker Hub - Instructions

## ⚠️ Problème détecté

Vous devez d'abord créer un compte Docker Hub ou utiliser vos identifiants corrects.

---

## Option 1 : Créer un nouveau compte Docker Hub (Recommandé)

### 1. Allez sur Docker Hub
🔗 **https://hub.docker.com/signup**

### 2. Créez votre compte
- **Username** : `zbelem001` (ou un autre de votre choix)
- **Email** : Votre email étudiant
- **Password** : Choisissez un mot de passe fort

### 3. Confirmez votre email
- Allez dans votre boîte mail
- Cliquez sur le lien de confirmation

### 4. Connectez-vous depuis le terminal
```bash
sudo docker login -u zbelem001
# Entrez votre mot de passe quand demandé
```

---

## Option 2 : Si vous avez déjà un compte

### 1. Vérifiez votre username Docker Hub
- Allez sur https://hub.docker.com
- Connectez-vous
- Vérifiez votre username exact (en haut à droite)

### 2. Utilisez ce username pour vous connecter
```bash
sudo docker login -u VOTRE_USERNAME_EXACT
# Entrez votre mot de passe
```

---

## Option 3 : Utiliser un Personal Access Token (Plus sécurisé)

### 1. Créez un PAT (Personal Access Token)
1. Connectez-vous sur https://hub.docker.com
2. Allez dans **Account Settings** → **Security**
3. Cliquez sur **New Access Token**
4. Nom : `opensky-project`
5. Permissions : **Read, Write, Delete**
6. Cliquez **Generate**
7. **COPIEZ LE TOKEN** (vous ne le verrez qu'une fois !)

### 2. Connectez-vous avec le token
```bash
sudo docker login -u zbelem001
# Password: COLLEZ_VOTRE_TOKEN (pas votre mot de passe normal)
```

---

## ✅ Après connexion réussie

Une fois connecté, vous verrez :
```
Login Succeeded
```

Ensuite, modifiez le script `publish-docker-images.sh` :

### Ligne à modifier

Ouvrez `publish-docker-images.sh` et changez :
```bash
DOCKER_USERNAME="zbelem001"
```

Par votre username Docker Hub réel si différent.

### Puis exécutez
```bash
./publish-docker-images.sh
```

---

## 🔧 Alternative : Sans Docker Hub

Si vous ne voulez pas créer de compte Docker Hub, vous pouvez :

### Option A : Utiliser GitHub Container Registry (ghcr.io)
- Gratuit avec votre compte GitHub
- Plus moderne
- Commandes similaires mais avec `ghcr.io/zbelem001/...`

### Option B : Juste GitHub + docker-compose build
- Votre prof clone le repo
- Lance `docker-compose build && docker-compose up -d`
- Un peu plus long mais fonctionne aussi

---

## 📝 Quelle option choisir ?

| Option | Avantages | Inconvénients |
|--------|-----------|---------------|
| **Docker Hub** | Le plus populaire, facile | Créer un compte |
| **GitHub Container Registry** | Intégré GitHub, moderne | Un peu plus technique |
| **Sans registry** | Rien à configurer | Build de 5-10 min pour votre prof |

**Ma recommandation** : Créez un compte Docker Hub (5 minutes), c'est le plus simple et le plus standard.

---

## 🆘 Besoin d'aide ?

### Je ne me souviens pas de mon mot de passe Docker Hub
→ Cliquez sur "Forgot password" sur https://hub.docker.com

### Je veux utiliser un autre username
→ Changez `DOCKER_USERNAME` dans `publish-docker-images.sh`

### L'email de confirmation ne arrive pas
→ Vérifiez vos spams

---

## 🎯 Prochaines étapes

Une fois connecté avec `sudo docker login` :

1. ✅ `sudo docker login -u zbelem001` → Login Succeeded
2. ✅ `./publish-docker-images.sh` → Publie les images
3. ✅ Vérifier sur https://hub.docker.com/u/zbelem001
4. ✅ Tester : `sudo docker-compose -f docker-compose.hub.yml up -d`
5. ✅ Push sur GitHub
6. ✅ Envoyer email à votre prof

**Dites-moi quelle option vous choisissez et je vous aide !** 😊
