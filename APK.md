# Fabriquer l'APK Android

Deux chemins possibles. Le premier ne demande rien à installer et prend une dizaine de
minutes ; le second automatise tout dans GitHub et redonne un APK à jour à chaque version.

La voie 1 exige que **le site soit déjà en ligne** sur GitHub Pages : elle emballe l'adresse
du site. La voie 2 n'en a pas besoin : elle embarque les fichiers dans l'APK.

---

## Avant toute chose : la clé de signature

> Si vous suivez la **voie 2**, sautez cette section : la clé se fabrique directement dans
> GitHub, sans rien installer (étape 3 de la voie 2).

Android n'installe que des applications **signées**. La clé est un petit fichier que vous
créez une fois et que vous gardez précieusement : si vous la perdez, vous ne pourrez plus
publier de mise à jour de la même application, il faudra en créer une nouvelle et les
utilisateurs devront désinstaller l'ancienne.

Sur un poste où Java est installé (ou dans un terminal Git Bash sous Windows) :

```bash
keytool -genkey -v \
  -keystore garig.keystore \
  -alias garig \
  -keyalg RSA -keysize 2048 -validity 10000
```

L'outil demande un mot de passe, puis quelques informations (nom, organisation, ville,
pays). Notez le **mot de passe du magasin**, le **mot de passe de la clé** (souvent le même)
et l'**alias** (`garig` ici).

> Si Java n'est pas installé, la voie 1 ci-dessous génère la clé pour vous : PWABuilder
> propose de créer la clé de signature et vous fait télécharger le fichier. Conservez-le.

**Ne mettez jamais `garig.keystore` dans le dépôt Git.** Le fichier `.gitignore` l'exclut déjà.

---

## Voie 1 — PWABuilder (le plus simple, rien à installer)

PWABuilder est l'outil de Microsoft qui emballe un site web en application Android.

1. Le site doit être en ligne : `https://<votre-compte>.github.io/<votre-depot>/`
2. Ouvrez **https://www.pwabuilder.com**, collez cette adresse, lancez l'analyse.
3. Le rapport doit être au vert sur le manifeste et le service worker — les deux sont déjà
   dans le dépôt (`manifest.webmanifest` et `sw.js`).
4. Cliquez **Package for stores → Android**.
   - *Package ID* : `fr.garig.crhebdo`
   - *App name* : `CR Hebdo`
   - *Signing key* : « Create new » pour en générer une, ou « Use mine » si vous avez déjà
     fait la commande `keytool` ci-dessus.
5. Téléchargez l'archive. Elle contient :
   - `app-release-signed.apk` — le fichier à installer sur les téléphones
   - `app-release-bundle.aab` — à n'utiliser que pour le Play Store
   - `signing.keystore` + `signing-key-info.txt` — **à conserver hors du dépôt**
   - `assetlinks.json` — voir l'étape suivante

### Étape indispensable : assetlinks.json

L'application Android ouvre votre site en plein écran. Pour que la barre d'adresse du
navigateur n'apparaisse pas, Android vérifie que le site et l'application appartiennent bien
à la même personne, via un fichier de vérification.

1. Ouvrez le `assetlinks.json` fourni par PWABuilder, ou reprenez celui du dépôt
   (`.well-known/assetlinks.json`) et remplacez `REMPLACER_PAR_L_EMPREINTE_SHA256_DE_VOTRE_CLE`
   par l'empreinte indiquée dans `signing-key-info.txt`.
2. Poussez le fichier dans le dépôt, à l'emplacement `.well-known/assetlinks.json`.
3. Vérifiez qu'il répond bien à
   `https://<votre-compte>.github.io/<votre-depot>/.well-known/assetlinks.json`

> Attention : GitHub Pages sert le site dans un sous-dossier (`/<votre-depot>/`), alors
> qu'Android cherche `assetlinks.json` à la **racine du domaine**
> (`https://<votre-compte>.github.io/.well-known/assetlinks.json`). Deux solutions :
> publier le fichier dans un dépôt nommé `<votre-compte>.github.io`, ou brancher un nom de
> domaine à vous sur le dépôt (Settings → Pages → Custom domain). Sans cela l'application
> fonctionne quand même, mais affiche une fine barre d'adresse en haut.
> **La voie 2 ci-dessous n'a pas ce problème** : l'application embarque les fichiers et ne
> dépend d'aucun domaine.

### Installer l'APK sur un téléphone

Envoyez le `.apk` par mail ou copiez-le sur le téléphone, puis ouvrez-le. Android demandera
d'autoriser l'installation depuis cette source (Paramètres → Applications → Accès spécial →
Installer des applications inconnues). C'est normal pour une application distribuée hors du
Play Store.

---

## Voie 2 — GitHub Actions (automatique, application autonome)

Le dépôt contient déjà tout le nécessaire. L'application est **embarquée dans l'APK** : elle
fonctionne sans connexion et ne dépend d'aucun domaine, donc pas de `assetlinks.json` à gérer.
Rien à installer sur votre poste : la clé de signature elle-même se fabrique dans GitHub.

### Étape 1 — Pousser le dépôt

Vérifiez que le dossier `.github/` est bien parti (Git ignore parfois les dossiers commençant
par un point selon la façon dont vous ajoutez les fichiers) :

```bash
git add -A
git status          # .github/workflows/apk-android.yml doit apparaître
git commit -m "Workflows APK"
git push
```

Dans l'onglet **Actions** du dépôt, deux workflows doivent maintenant être listés :
« Créer la clé de signature » et « APK Android ».

### Étape 2 — Créer les trois secrets de mot de passe

**Settings → Secrets and variables → Actions → New repository secret**, trois fois :

| Nom exact du secret | Valeur à mettre |
|---|---|
| `ANDROID_KEYSTORE_PASSWORD` | un mot de passe que vous choisissez |
| `ANDROID_KEY_PASSWORD` | **le même** que ci-dessus |
| `ANDROID_KEY_ALIAS` | `garig` |

Les deux mots de passe doivent être identiques : le format PKCS12 utilisé par la clé n'en
gère qu'un seul. Notez-le dans votre gestionnaire de mots de passe, il sera redemandé à
chaque changement de poste.

### Étape 3 — Fabriquer la clé de signature (une seule fois)

**Actions → Créer la clé de signature → Run workflow.** Renseignez le nom, l'organisation,
la ville et le pays — ces informations sont inscrites dans la clé, elles ne sont pas secrètes.

Au bout d'une minute, la page de l'exécution propose en bas un fichier
**`cle-de-signature`**. Téléchargez-le tout de suite : il est supprimé au bout de 24 heures.
Il contient trois fichiers :

- `garig.keystore` — **la clé.** Mettez-la en lieu sûr, hors du dépôt (coffre-fort de mots de
  passe, disque de sauvegarde). Sans elle, plus aucune mise à jour de l'application n'est
  possible : il faudrait repartir d'une nouvelle application et faire désinstaller l'ancienne.
- `garig.keystore.base64.txt` — la même clé en texte, pour l'étape suivante.
- `empreinte-sha256.txt` — utile seulement si vous passez un jour par la voie 1.

### Étape 4 — Créer le quatrième secret

Ouvrez `garig.keystore.base64.txt` dans un éditeur de texte, sélectionnez **tout** le
contenu (une seule longue ligne, sans retour à la ligne), puis créez le secret :

| Nom exact du secret | Valeur |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | tout le contenu du fichier `.base64.txt` |

Supprimez ensuite le fichier `.base64.txt` de votre dossier de téléchargements, et ne gardez
que `garig.keystore` à l'abri.

### Étape 5 — Fabriquer l'APK

**Actions → APK Android → Run workflow.**

La première exécution prend cinq à dix minutes (téléchargement du SDK Android) ; les
suivantes, deux à trois minutes. Quand la coche verte apparaît, ouvrez l'exécution : l'APK
est en bas de page, dans **Artifacts → `garig-cr-hebdo-apk`**. Le téléchargement arrive
sous forme de fichier ZIP contenant l'APK.

### Étape 6 — Installer sur un téléphone

Envoyez l'APK par mail, par messagerie ou par câble, puis ouvrez-le sur le téléphone.
Android demande une autorisation, c'est normal pour une application distribuée hors du
Play Store : **Paramètres → Applications → Accès spécial → Installer des applications
inconnues**, autorisez l'application qui ouvre le fichier (le navigateur ou le gestionnaire
de fichiers), puis relancez l'installation.

Un avertissement Play Protect peut apparaître : « Installer quand même ». Il s'affiche pour
toute application non passée par le Play Store.

### Étape 7 — Publier une version

Pour qu'un APK soit attaché à une release GitHub, d'où chacun peut le télécharger :

```bash
git tag v1.0.0
git push origin v1.0.0
```

Le workflow se relance seul et joint l'APK à la release `v1.0.0`.

### Mettre à jour l'application

Modifiez `index.html`, poussez, puis relancez le workflow (ou posez une étiquette `v1.1.0`).
Pour qu'Android accepte d'installer la nouvelle version par-dessus l'ancienne, il faut :

- **la même clé de signature** — c'est automatique tant que le secret reste en place ;
- un **numéro de version supérieur** : augmentez `"version"` dans `package.json`
  (`1.0.0` → `1.1.0`) avant de relancer.

Les comptes-rendus déjà saisis sur le téléphone ne sont pas effacés par une mise à jour.

---

## Personnaliser l'icône de l'application

L'icône du lanceur Android est générée depuis `assets/icon.png` (fond noir, lettrage vert,
sous-titre). Deux remarques :

- Android rogne les icônes en cercle ou en carré arrondi selon le téléphone. Le contenu de
  `assets/icon.png` est volontairement resserré au centre pour ne jamais être coupé.
- À la taille réelle du lanceur (environ 48 px), « Compte rendu Hebdo » devient une trace
  grise. Si le rendu vous paraît chargé, remplacez le fichier par la variante sans
  sous-titre déjà fournie :

  ```bash
  cp assets/icon-lettrage-seul.png assets/icon.png
  ```

L'écran de démarrage (`assets/splash.png`) affiche le logo complet, lui bien lisible.

---

## Play Store, si un jour

Le Play Store n'accepte pas les `.apk` mais les `.aab`. Remplacez `assembleRelease` par
`bundleRelease` dans le workflow ; le fichier sort dans
`android/app/build/outputs/bundle/release/`. Il faut par ailleurs un compte développeur
Google (paiement unique), une fiche avec captures d'écran, et une politique de
confidentialité — courte ici, puisque l'application n'envoie aucune donnée et ne stocke rien
en dehors de l'appareil.

---

## En cas de blocage

| Symptôme | Cause la plus fréquente |
|---|---|
| Le workflow s'arrête sur « Secret ... absent » | Un secret manque ou son nom est mal orthographié — les noms sont sensibles à la casse |
| « keystore was tampered with, or password was incorrect » | Mot de passe erroné, ou contenu du `.base64.txt` copié partiellement |
| Les workflows n'apparaissent pas dans l'onglet Actions | Le dossier `.github/` n'a pas été poussé ; refaites `git add -A` puis `git push` |
| « Resource not accessible by integration » à l'étape release | Settings → Actions → General → Workflow permissions → « Read and write permissions » |
| L'APK s'installe mais refuse de remplacer l'ancienne version | Clé de signature différente, ou `versionCode` non augmenté |
| L'application affiche une barre d'adresse en haut (voie 1) | `assetlinks.json` absent, mal placé, ou empreinte SHA-256 incorrecte |
| Page blanche à l'ouverture (voie 2) | Le dossier `www/` n'a pas été rempli avant `cap sync` — l'étape « Préparer le dossier web » du workflow s'en charge |
