import os
from PIL import Image
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import sys

#  Ermitteln der Dateigröße in MB
def get_file_size_mb(file_path):
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return size_mb

# Rekursive Addition enumerierter Bilder
def get_directory_size_mb(directory):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # Größe in MB

# Bilder umbenennen und verschieben
def rename_and_move_images(input_dir, batch_size_mb):
    # Liste für alle Bilder im Eingabeverzeichnis
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_count = len(image_files)
    current_batch = 1
    current_size_mb = 0

    for idx, image_file in enumerate(image_files):
        original_name, ext = os.path.splitext(image_file)
        image_path = os.path.join(input_dir, image_file)

        # Bildgröße in MB ermitteln
        size_mb = get_file_size_mb(image_path)

        # Neuer Dateiname im Format [xxx-originalname]
        new_name = f"{idx + 1:03d}-{original_name}{ext}"
        new_image_path = os.path.join(input_dir, new_name)

        os.rename(image_path, new_image_path)

        # Ordner für Batch erstellen, falls noch nicht vorhanden
        output_dir = os.path.join(input_dir, str(current_batch))
        os.makedirs(output_dir, exist_ok=True)

        # Bild in entsprechende Batch-Ordner verschieben
        shutil.move(new_image_path, os.path.join(output_dir, new_name))

        current_size_mb += size_mb

        # Wenn Batch-Größe erreicht oder alle Bilder durchlaufen
        if current_size_mb >= batch_size_mb or idx == image_count - 1:
            # Berechne die Größe des Batch-Ordners und benenne ihn entsprechend um
            folder_size_mb = get_directory_size_mb(output_dir)
            new_folder_name = f"{current_batch} ({folder_size_mb:.2f} MB)"
            new_folder_path = os.path.join(input_dir, new_folder_name)
            os.rename(output_dir, new_folder_path)

            current_batch += 1
            current_size_mb = 0

    return current_batch - 1

# Auswahl Eingabeverzeichnisses
def select_input_directory():
    root = tk.Tk()
    root.withdraw()  # Verstecke das Tkinter-Fenster

    input_dir = filedialog.askdirectory(title="Wähle bitte den Ordner aus, der bearbeitet werden soll")

    if input_dir:
        return input_dir
    else:
        raise ValueError("Kein Ordner ausgewählt")

# Eingabe Batchgröße
def get_batch_size():
    root = tk.Tk()
    root.withdraw()  # Verstecke das Tkinter-Fenster

    batch_size_mb = simpledialog.askinteger("Benutzerdefinierte Zielgröße", "Bitte geben Sie die Zielgröße für jeden Batch in MB ein:\n(Standardmäßig 450MB)", initialvalue=450)
    
    if batch_size_mb is None or batch_size_mb <= 0:
        # Standardgröße 450MB
        batch_size_mb = 450
    
    return batch_size_mb

# MAIN
if __name__ == "__main__":
    try:
        input_dir = select_input_directory()
        batch_size_mb = get_batch_size()

        # Dialog zur Bestätigung der Eingaben
        confirmation = messagebox.askyesno(
            "Bestätigung",
            f"Gewählter Ordner: {input_dir}\nZielgröße pro Batch: {batch_size_mb} MB\n\nSind diese Einstellungen korrekt?"
        )
        if not confirmation:
            raise ValueError("Benutzer hat die Eingaben nicht bestätigt")

        num_batches = rename_and_move_images(input_dir, batch_size_mb)
        messagebox.showinfo("Fertig", f"Es wurden {num_batches} Batch-Ordner erstellt und Bilder verschoben.")
    
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler aufgetreten:\n\n{e}")

    # Programm beenden
    sys.exit()
