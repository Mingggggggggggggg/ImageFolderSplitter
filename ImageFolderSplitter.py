import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sys

# Ermittlung der Dateigröße in MB
def get_file_size_mb(file_path):
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except OSError as e:
        print(f"Fehler beim Abrufen der Dateigröße von {file_path}: {e}")
        return 0

# Berechnung der Größe eines Verzeichnisses in MB
def get_directory_size_mb(directory):
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(directory):
            total_size += sum(os.path.getsize(os.path.join(dirpath, filename)) for filename in filenames)
    except OSError as e:
        print(f"Fehler beim Abrufen der Verzeichnisgröße von {directory}: {e}")
    return total_size / (1024 * 1024)

# Natürliche Sortierung von Strings
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

# Umbenennung und Verschiebung der Bilder
def rename_and_move_images(input_dir, batch_size_mb, rename_images, sort_into_batches, reverse_order=False):
    current_batch = 1
    current_size_mb = 0
    image_index = 1
    non_image_folder = os.path.join(input_dir, "non_images")
    found_non_images = False

    num_renamed_images = 0
    num_non_images = 0

    # Holen und Sortieren der Unterordner nach natürlicher Sortierung
    subfolders = sorted(
        [f.path for f in os.scandir(input_dir) if f.is_dir()],
        key=lambda f: natural_sort_key(os.path.basename(f)),
        reverse=reverse_order
    )

    for folder in subfolders:
        for root, _, files in os.walk(folder, topdown=False):
            # Check images with wanted suffixes
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jpe', '.gif'))]
            # Check files without the following suffixes -> marking them as other_files
            other_files = [f for f in files if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.jpe', '.gif'))]

            # Bewege nicht-Bilddateien
            for other_file in other_files:
                other_file_path = os.path.join(root, other_file)
                if not found_non_images:
                    os.makedirs(non_image_folder, exist_ok=True)
                    found_non_images = True

                # Initialer Zielpfad
                target_path = os.path.join(non_image_folder, other_file)
                file_name, ext = os.path.splitext(other_file)
                counter = 1

                # Solange der Zielpfad existiert, füge eine Nummer hinzu
                while os.path.exists(target_path):
                    target_path = os.path.join(non_image_folder, f"{counter}_{file_name}{ext}")
                    counter += 1
                        
                try:
                    shutil.move(other_file_path, target_path)
                except shutil.Error as e:
                    print(f"Fehler beim Verschieben von {other_file_path}: {e}")
                num_non_images += 1

            for image_file in sorted(image_files, key=natural_sort_key):
                original_name, ext = os.path.splitext(image_file)
                image_path = os.path.join(root, image_file)
                size_mb = get_file_size_mb(image_path)
                new_name = f"{image_index:03d}-{original_name}{ext}" if rename_images else image_file
                image_index += 1
                new_image_path = os.path.join(root, new_name)

                # Benenne das Bild um, wenn gewünscht
                if rename_images:
                    try:
                        os.rename(image_path, new_image_path)
                    except OSError as e:
                        print(f"Fehler beim Umbenennen von {image_path} nach {new_image_path}: {e}")
                    num_renamed_images += 1
                else:
                    new_image_path = image_path

                if sort_into_batches:
                    output_dir = os.path.join(input_dir, str(current_batch))
                    os.makedirs(output_dir, exist_ok=True)
                    try:
                        shutil.move(new_image_path, os.path.join(output_dir, new_name))
                    except shutil.Error as e:
                        print(f"Fehler beim Verschieben von {new_image_path} nach {os.path.join(output_dir, new_name)}: {e}")
                    current_size_mb += size_mb

                    if current_size_mb >= batch_size_mb:
                        folder_size_mb = get_directory_size_mb(output_dir)
                        new_folder_name = f"{current_batch} ({folder_size_mb:.2f} MB)"
                        new_folder_path = os.path.join(input_dir, new_folder_name)
                        try:
                            os.rename(output_dir, new_folder_path)
                        except OSError as e:
                            print(f"Fehler beim Umbenennen von {output_dir} nach {new_folder_path}: {e}")
                        current_batch += 1
                        current_size_mb = 0
                else:
                    num_renamed_images += 1  # Bild wurde umbenannt, aber nicht in Batch verschoben

        # Lösche leere Ordner
        for dirpath, dirnames, _ in os.walk(root, topdown=False):
            if not os.listdir(dirpath):
                try:
                    os.rmdir(dirpath)
                except OSError as e:
                    print(f"Fehler beim Löschen von {dirpath}: {e}")

    # Letzten Batch-Ordner umbenennen
    if current_size_mb > 0 and sort_into_batches:
        output_dir = os.path.join(input_dir, str(current_batch))
        folder_size_mb = get_directory_size_mb(output_dir)
        new_folder_name = f"{current_batch} ({folder_size_mb:.2f} MB)"
        new_folder_path = os.path.join(input_dir, new_folder_name)
        try:
            os.rename(output_dir, new_folder_path)
        except OSError as e:
            print(f"Fehler beim Umbenennen von {output_dir} nach {new_folder_path}: {e}")

    # .processed-Datei im Root-Verzeichnis erstellen
    processed_flag = os.path.join(input_dir, '.processed')
    try:
        with open(processed_flag, 'w'):
            pass
    except OSError as e:
        print(f"Fehler beim Erstellen der .processed-Datei: {e}")

    return current_batch, found_non_images, num_renamed_images, num_non_images

# Fenster zentrieren
def center_window(window):
    window.update_idletasks()
    width, height = window.winfo_width(), window.winfo_height()
    screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

# GUI für Auswahl des Eingabeverzeichnisses und Optionen
def select_input_directory_and_options():
    def select_folder():
        nonlocal input_dir
        input_dir = filedialog.askdirectory(title="Wähle den Ordner aus, der bearbeitet werden soll")
        if input_dir:
            path_label.config(text=input_dir)
            if os.path.isfile(os.path.join(input_dir, '.processed')):
                messagebox.showwarning("Bereits verarbeitet", "Der ausgewählte Ordner wurde bereits verarbeitet.")
                input_dir = ""

    def submit():
        nonlocal batch_size_mb, rename_images, sort_into_batches, reverse_order
        if input_dir:
            if os.path.isfile(os.path.join(input_dir, '.processed')):
                messagebox.showwarning("Bereits verarbeitet", "Der ausgewählte Ordner wurde bereits verarbeitet.")
                return

            try:
                batch_size_mb = int(batch_size_var.get())
            except ValueError:
                batch_size_mb = 450  # Standardgröße auf 450 MB setzen

            rename_images = rename_var.get()
            sort_into_batches = sort_var.get()
            reverse_order = reverse_var.get()

            confirmation_message = (
                f"Gewählter Ordner: {input_dir}\n"
                f"Zielgröße pro Batch: {batch_size_mb} MB\n"
                f"Bilder umbenennen: {'Ja' if rename_images else 'Nein'}\n"
                f"In Batches einordnen: {'Ja' if sort_into_batches else 'Nein'}\n"
                f"Ordner von unten nach oben bearbeiten: {'Ja' if reverse_order else 'Nein'}\n"
            )
            
            if sort_into_batches:
                confirmation_message += "Weitere Details werden angezeigt, wenn die Verarbeitung abgeschlossen ist."
            else:
                confirmation_message += "Weitere Details über die Bilder und nicht-Bilder werden angezeigt."

            confirmation = messagebox.askyesno("Bestätigung", confirmation_message)
            if confirmation:
                root.quit()

    def toggle_batch_size():
        batch_size_entry.config(state='normal' if sort_var.get() else 'disabled')

    def on_hover(event):
        event.widget.config(style='Hover.TButton')

    def on_leave(event):
        event.widget.config(style='TButton')

    input_dir = ""
    batch_size_mb = 450
    rename_images = True
    sort_into_batches = True
    reverse_order = True  # Standardmäßig aktiviert

    root = tk.Tk()
    root.title("Image Folder Splitter")

    style = ttk.Style()
    style.configure('TButton', padding=6, relief='flat', background='#DDDDDD')
    style.configure('Hover.TButton', background='#AAAAAA')

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    tk.Label(frame, text="Zielgröße für jeden Batch in MB:").grid(row=0, column=0, sticky='w')
    batch_size_var = tk.StringVar(value='450')
    batch_size_entry = tk.Entry(frame, textvariable=batch_size_var)
    batch_size_entry.grid(row=0, column=1, sticky='e')

    rename_var = tk.BooleanVar(value=True)
    tk.Checkbutton(frame, text="Bilder umbenennen", variable=rename_var).grid(row=1, column=0, columnspan=2, sticky='w')

    sort_var = tk.BooleanVar(value=True)
    tk.Checkbutton(frame, text="In Batches einordnen", variable=sort_var, command=toggle_batch_size).grid(row=2, column=0, columnspan=2, sticky='w')

    reverse_var = tk.BooleanVar(value=True)  # Standardmäßig aktiviert
    tk.Checkbutton(frame, text="Ordner von unten nach oben bearbeiten", variable=reverse_var).grid(row=3, column=0, columnspan=2, sticky='w')

    select_button = ttk.Button(frame, text="Ordner auswählen", command=select_folder)
    select_button.grid(row=4, column=0, columnspan=2, sticky='ew')
    select_button.bind("<Enter>", on_hover)
    select_button.bind("<Leave>", on_leave)

    path_label = tk.Label(frame, text="")
    path_label.grid(row=5, column=0, columnspan=2, sticky='w')

    submit_button = ttk.Button(frame, text="Weiter", command=submit)
    submit_button.grid(row=6, column=0, columnspan=2, sticky='ew')
    submit_button.bind("<Enter>", on_hover)
    submit_button.bind("<Leave>", on_leave)

    center_window(root)
    root.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()

    if not input_dir:
        sys.exit("Kein Ordner ausgewählt")

    return input_dir, batch_size_mb, rename_images, sort_into_batches, reverse_order

# MAIN
if __name__ == "__main__":
    try:
        input_dir, batch_size_mb, rename_images, sort_into_batches, reverse_order = select_input_directory_and_options()

        num_batches, found_non_images, num_renamed_images, num_non_images = rename_and_move_images(input_dir, batch_size_mb, rename_images, sort_into_batches, reverse_order)

        if num_batches == 0 and sort_into_batches:
            num_batches = 1

        if sort_into_batches:
            result_message = f"Es wurden {num_batches} Batch-Ordner erstellt und Bilder verschoben."
        else:
            result_message = (
                f"Anzahl der umbenannten Bilder: {num_renamed_images}\n"
                f"Anzahl der nicht umbenannten Bilder: {num_non_images}\n"
                f"Anzahl der Nicht-Bilddateien: {num_non_images}\n"
            )
        
        if found_non_images:
            result_message += "\nEin gesonderter Ordner für Nicht-Bilddateien wurde erstellt."
        messagebox.showinfo("Fertig", result_message)

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler aufgetreten:\n\n{e}")

    sys.exit()
