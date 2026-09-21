package fr.garig.crhebdo;

import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.util.Base64;

import androidx.core.content.FileProvider;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;

/**
 * Garig — Compte rendu Hebdo
 *
 * Ouvre l'application de messagerie choisie par l'utilisateur avec, d'un seul coup :
 * les destinataires, l'objet, le texte et les pièces jointes.
 *
 * La feuille de partage ordinaire d'Android ne transporte pas de champ « À » ; un lien
 * mailto: ne transporte pas de pièce jointe. Seul un Intent ACTION_SEND construit à la
 * main porte les deux à la fois — c'est tout ce que fait ce module.
 */
@CapacitorPlugin(name = "EnvoiEmail")
public class EnvoiEmailPlugin extends Plugin {

    @PluginMethod
    public void composer(PluginCall call) {
        try {
            JSArray destinataires = call.getArray("to", new JSArray());
            JSArray fichiers = call.getArray("fichiers", new JSArray());
            String sujet = call.getString("sujet", "");
            String texte = call.getString("texte", "");

            String[] adresses = new String[destinataires.length()];
            for (int i = 0; i < destinataires.length(); i++) {
                adresses[i] = destinataires.getString(i);
            }

            /* Les pièces jointes sont écrites dans le cache de l'application : c'est le seul
               emplacement qu'une autre application est sûre de pouvoir relire, via FileProvider. */
            File dossier = new File(getContext().getCacheDir(), "envoi");
            if (!dossier.exists()) {
                dossier.mkdirs();
            }

            ArrayList<Uri> uris = new ArrayList<>();
            String autorite = getContext().getPackageName() + ".fileprovider";

            for (int i = 0; i < fichiers.length(); i++) {
                JSONObject f = fichiers.getJSONObject(i);
                String nom = f.getString("nom");
                byte[] donnees = Base64.decode(f.getString("data"), Base64.DEFAULT);

                File cible = new File(dossier, nom);
                FileOutputStream sortie = new FileOutputStream(cible);
                try {
                    sortie.write(donnees);
                } finally {
                    sortie.close();
                }
                uris.add(FileProvider.getUriForFile(getContext(), autorite, cible));
            }

            Intent intent;
            if (uris.size() > 1) {
                intent = new Intent(Intent.ACTION_SEND_MULTIPLE);
                intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris);
            } else if (uris.size() == 1) {
                intent = new Intent(Intent.ACTION_SEND);
                intent.putExtra(Intent.EXTRA_STREAM, uris.get(0));
            } else {
                intent = new Intent(Intent.ACTION_SEND);
            }

            intent.setType("message/rfc822");
            intent.putExtra(Intent.EXTRA_EMAIL, adresses);
            intent.putExtra(Intent.EXTRA_SUBJECT, sujet);
            intent.putExtra(Intent.EXTRA_TEXT, texte);

            /* Le ClipData étend l'autorisation de lecture à toutes les pièces jointes :
               sans lui, certaines messageries affichent une pièce jointe vide. */
            ClipData clip = null;
            for (int i = 0; i < uris.size(); i++) {
                if (clip == null) {
                    clip = ClipData.newUri(getContext().getContentResolver(), "compte-rendu", uris.get(i));
                } else {
                    clip.addItem(new ClipData.Item(uris.get(i)));
                }
            }
            if (clip != null) {
                intent.setClipData(clip);
            }
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

            /* Deux façons d'ouvrir la messagerie :
               - memoriser = true  : on lance l'intention telle quelle. Android affiche son
                 dialogue « Ouvrir avec », qui propose « Une fois » et « Toujours ». Choisir
                 « Toujours » évite d'avoir à redésigner l'application chaque semaine.
               - memoriser = false : createChooser force le choix à chaque envoi. C'est
                 pratique quand plusieurs messageries servent à tour de rôle — mais un
                 sélecteur, par construction, ne propose jamais « Toujours ». */
            boolean memoriser = call.getBoolean("memoriser", Boolean.TRUE);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

            if (memoriser) {
                try {
                    getContext().startActivity(intent);
                } catch (android.content.ActivityNotFoundException introuvable) {
                    Intent choix = Intent.createChooser(intent, "Envoyer le compte-rendu");
                    choix.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    choix.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    getContext().startActivity(choix);
                }
            } else {
                Intent choix = Intent.createChooser(intent, "Envoyer le compte-rendu");
                choix.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                choix.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                getContext().startActivity(choix);
            }

            JSObject retour = new JSObject();
            retour.put("ok", true);
            retour.put("destinataires", adresses.length);
            retour.put("joints", uris.size());
            call.resolve(retour);

        } catch (Exception e) {
            call.reject(e.getMessage() == null ? "Envoi impossible" : e.getMessage());
        }
    }
}
