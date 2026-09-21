package fr.garig.crhebdo;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        /* Doit précéder super.onCreate : c'est là que Capacitor construit le pont. */
        registerPlugin(EnvoiEmailPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
