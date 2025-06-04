# Importation des modules nécessaires
import os                      # Pour les opérations système et de fichiers
import platform                # Pour détecter le système d'exploitation
import tempfile                # Pour localiser le répertoire temporaire par défaut
import shutil                  # Pour supprimer récursivement des dossiers
from datetime import datetime  # Pour générer un horodatage dans le rapport

# Fonction pour déterminer les répertoires temporaires à nettoyer
def get_temp_dirs():
    system = platform.system()  # Détection du système d'exploitation (Windows, Linux, etc.)
    temp_dirs = []              # Liste qui contiendra les chemins des Répertoires à nettoyer

    if system == "Windows":
        # Sous Windows, on ajoute %TEMP% et le répertoire Temp du système
        temp_dirs.append(tempfile.gettempdir())  # Ex: C:\\Users\\User\\AppData\\Local\\Temp
        temp_dirs.append(os.path.expandvars("%SystemRoot%\\Temp"))  # Ex: C:\\Windows\\Temp
    elif system == "Linux":
        # Sous Linux, on ajoute /tmp et le répertoire temporaire par défaut
        temp_dirs.append("/tmp")
        temp_dirs.append(tempfile.gettempdir())  # Généralement aussi /tmp

    return temp_dirs  # Retourne la liste des Répertoires temporaires à nettoyer

# Fonction qui nettoie un Répertoire temporaire donné (Fichiers + Sous-Dossiers)
def clean_temp_dir(path):
    files_deleted = 0       # Initialise un compteur de Fichiers temporaires supprimés
    dirs_deleted = 0        # Initialise un compteur de Dossiers temporaires supprimés
    logs = []               # Initialise une liste pour enregistrer les messages (succès ou erreurs) dans le Rapport

    # Vérifie si le chemin spécifié existe réellement sur le système
    if not os.path.exists(path):
        logs.append(f"Chemin inexistant : {path}")  # Ajoute un message d'erreur si le chemin est invalide
        return files_deleted, dirs_deleted, logs    # Retourne les compteurs à zéro + log d'erreur

    # Parcours récursif du Répertoire, du bas vers le haut (topdown=False)
    # Cela permet de supprimer les Fichiers AVANT de tenter de supprimer les Dossiers
    for root, dirs, files in os.walk(path, topdown=False):

        # Boucle sur tous les Fichiers dans le Dossier courant
        for name in files:
            full_path = os.path.join(root, name)    # Construit le chemin complet vers le Fichier
            try:
                os.remove(full_path)                # Tente de supprimer le Fichier
                logs.append(f"[OK] Fichier supprimé : {full_path}")  # Ajoute un message de succès
                files_deleted += 1                  # Incrémente le compteur de Fichiers supprimés
            except Exception as e:
                # En cas d'erreur (ex : permission refusée), enregistre l'erreur dans les logs
                logs.append(f"[ERREUR] Suppression Fichier {full_path} : {e}")

        # Boucle sur tous les Sous-Dossiers dans le Répertoire courant
        for name in dirs:
            full_path = os.path.join(root, name)    # Construit le chemin complet vers le Sous-Dossier
            try:
                shutil.rmtree(full_path)            # Tente de supprimer récursivement le Sous-Dossier
                logs.append(f"[OK] Dossier supprimé : {full_path}")  # Message de succès
                dirs_deleted += 1                   # Incrémente le compteur de Dossiers supprimés
            except Exception as e:
                # En cas d'erreur (ex : permission refusée), enregistre l'erreur dans les logs
                logs.append(f"[ERREUR] Suppression Dossier {full_path} : {e}")

    # Retourne les résultats finaux : nombre de Fichiers et Dossiers supprimés + tous les logs (Succès ET Erreurs)
    return files_deleted, dirs_deleted, logs

# Fonction qui écrit les résultats dans un fichier log
def generate_report(log_path, report_data):
    with open(log_path, "a", encoding="utf-8") as log_file:
        # Ajoute un titre avec l’horodatage
        # log_file.write(f"\n\n--- Rapport de Maintenance ({datetime.now()}) ---\n") # "--- Rapport de Maintenance (2025-05-30 11:22:04.219161) ---"
        log_file.write(f"\n\n--- Rapport de Maintenance ({datetime.now().strftime('%d/%m/%Y %H:%M:%S')}) ---\n") # "--- Rapport de Maintenance (30/05/2025 11:25:41) ---"
        for entry in report_data:
            log_file.write(entry + "\n")  # Écrit chaque ligne du rapport

# Fonction principale exécutée lorsque le script démarre
def main():
    temp_dirs = get_temp_dirs()  # Récupère les Répertoires temporaires à nettoyer
    report = []                  # Initialise la liste des lignes du rapport qui seront ajoutées au fichier "rapport_maintenance.txt"

    for temp_dir in temp_dirs:
        report.append(f"\n[NETTOYAGE] Répertoire : {temp_dir}")
        files_deleted, dirs_deleted, errors = clean_temp_dir(temp_dir)

        # Ajout  dans le fichier "rapport_maintenance.txt" du nombre de Fichiers et Dossiers temporaires supprimés
        report.append(f"  -> Fichiers supprimés : {files_deleted}")
        report.append(f"  -> Dossiers supprimés : {dirs_deleted}")

        # En cas d'erreur (de nettoyage)
        if errors:
            report.append("  -> Erreurs :")
            # Ajout des erreurs détectées
            for err in errors:
                report.append(f"     - {err}")
        # Sinon
        else:
            report.append("  -> Aucune erreur détectée.")

    # Détermine le chemin du fichier Rapport dans le répertoire utilisateur OU dans le répertoire où se trouve le script actuellement exécuté
    # log_file = os.path.join(os.path.expanduser("~"), "rapport_maintenance.txt") # le répertoire utilisateur
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rapport_maintenance.txt") # le chemin absolu du script actuellement exécuté

    generate_report(log_file, report)  # Génère le Rapport
    
    print(f"[INFO] Rapport généré : {log_file}")  # Affiche l’emplacement du fichier "rapport_maintenance.txt"

# Point d'entrée du script
if __name__ == "__main__":
    main()
