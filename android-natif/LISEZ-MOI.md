# Module Android d'envoi e-mail

Ces trois fichiers sont recopiés dans le projet Android par la recette GitHub
(`.github/workflows/apk-android.yml`), juste après `npx cap add android`.

| Fichier | Destination dans le projet Android |
|---|---|
| `EnvoiEmailPlugin.java` | `app/src/main/java/fr/garig/crhebdo/` |
| `MainActivity.java` | `app/src/main/java/fr/garig/crhebdo/` (remplace celui généré) |
| `file_paths.xml` | `app/src/main/res/xml/` (remplace celui généré) |

## À quoi ça sert

Android offre deux mécanismes d'envoi, et chacun laisse tomber la moitié du besoin :

- la **feuille de partage** transporte des pièces jointes, mais pas le champ « À » ;
- un lien **`mailto:`** transporte les destinataires, mais pas de pièce jointe.

Ce module construit directement l'intention `ACTION_SEND` qui porte **les deux** :
destinataires, objet, texte, et les fichiers joints. L'utilisateur choisit ensuite sa
messagerie — Outlook, Gmail ou autre — dans la liste que propose le téléphone.

## Si le module est absent

L'application le détecte au démarrage et retombe sur la feuille de partage ordinaire :
les pièces jointes partent, les destinataires sont copiés dans le presse-papiers.
Rien ne casse, la fonction est seulement moins confortable.

## Si vous changez l'identifiant de l'application

`capacitor.config.json` → `appId` doit rester `fr.garig.crhebdo`, sinon corrigez la ligne
`package` en tête des deux fichiers `.java` ainsi que les chemins dans la recette.
