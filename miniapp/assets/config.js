// SukunaRenamer — configuration partagée par toutes les pages de la Mini App
// Remplace API_BASE et ADSGRAM_BLOCK_ID avant de déployer sur Vercel.

const API_BASE = "https://legal-marilin-vianney-001f1b1c.koyeb.app"; // URL Koyeb où tourne bot.py / web_support.py
const ADSGRAM_BLOCK_ID = "37235";

// Monetag — Rewarded Interstitial (zone dashboard : https://libtl.com)
// La fonction de déclenchement est automatiquement "show_" + ce zone ID.
// Mis sur false pour le moment : seule la rewarded video AdsGram est utilisée.
// Repasser à true (et vérifier le zone ID) pour la réactiver.
const MONETAG_ENABLED = false;
const MONETAG_ZONE_ID = "10518701";
