import os
import shutil

from dotenv import load_dotenv

load_dotenv()
SOURCE_FOLDER = os.getenv("PASTA")

CATEGORIES = {
    "Images": ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'),
    "Documents": ('.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt', '.rtf', '.csv'),
    "Videos": ('.mp4', '.mov', '.avi', '.mkv', '.wmv'),
    "Music": ('.mp3', '.wav'),
    "Archives": ('.zip', '.rar', '.7z', '.tar', '.gz'),
    "Executables": ('.exe', '.msi', '.bat', '.sh'),
    "Torrents": ('.torrent',),
    "Documents": {
        "PDFs": ('.pdf',),
        "Text": ('.docx', '.doc', '.txt', '.rtf'),
        "Spreadsheets": ('.xlsx', '.xls', '.csv'),
        "Presentations": ('.pptx', '.ppt',)
    }
}

MOVIE_FOLDER_DEST = "Movies"
VIDEO_EXTENSIONS = CATEGORIES["Videos"] 
MIN_VIDEO_SIZE_MB = 100
MIN_VIDEO_SIZE_BYTES = MIN_VIDEO_SIZE_MB * 1024 * 1024

def is_movie_folder(folder_path, video_extensions, min_size_bytes):
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            if os.path.isfile(item_path):
                _ , extension = os.path.splitext(item)
                
                if extension.lower() in video_extensions:
                    file_size = os.path.getsize(item_path)
                    if file_size >= min_size_bytes:
                        return True
    except Exception as e:
        print(f"Warning: Could not scan folder {folder_path}: {e}")
        return False
    
    return False

def organize_files(source_folder, categories):
    print(f"Starting organization of folder: {source_folder}\n")
    
    try:
        items_in_folder = os.listdir(source_folder)
    except FileNotFoundError:
        print(f"Error: The source folder '{source_folder}' was not found.")
        print("Please check the 'SOURCE_FOLDER' variable in the script.")
        return
    except Exception as e:
        print(f"Error accessing the source folder: {e}")
        return

    files_moved = 0
    files_skipped = 0
    folders_moved = 0
    folders_skipped = 0
    
    category_folders = list(categories.keys()) + ["Other", MOVIE_FOLDER_DEST]

    for filename in items_in_folder:
        item_path = os.path.join(source_folder, filename)
        
        # --- 1. Lógica para ARQUIVOS (Modificada) ---
        if os.path.isfile(item_path):
            extension = os.path.splitext(filename)[1].lower()

            if not extension:
                found_category_path = ["Other"]
            else:
                # Usa uma lista para construir o caminho (ex: ["Documents", "PDFs"])
                found_category_path = None 
                
                for category, extensions_or_subdict in categories.items():
                    
                    # Se for uma categoria simples (ex: "Images": ('.jpg', ...))
                    if isinstance(extensions_or_subdict, tuple):
                        if extension in extensions_or_subdict:
                            found_category_path = [category]
                            break
                    
                    # Se for uma categoria aninhada (ex: "Documents": { ... })
                    elif isinstance(extensions_or_subdict, dict):
                        for sub_category, sub_extensions in extensions_or_subdict.items():
                            if extension in sub_extensions:
                                found_category_path = [category, sub_category]
                                break
                        
                        if found_category_path:
                            break 
                
                # Se não encontrou em nenhuma categoria, usa "Other"
                if not found_category_path:
                    found_category_path = ["Other"]
            
            # Usa '*' para desempacotar a lista e construir o caminho
            # ex: os.path.join(source_folder, "Documents", "PDFs")
            destination_folder = os.path.join(source_folder, *found_category_path)
            
            if not os.path.exists(destination_folder):
                try:
                    os.makedirs(destination_folder)
                    print(f"Folder created: {destination_folder}")
                except OSError as e:
                    print(f"Error creating folder {destination_folder}: {e}")
                    files_skipped += 1
                    continue 

            destination_file_path = os.path.join(destination_folder, filename)

            try:
                shutil.move(item_path, destination_file_path)
                display_path = "/".join(found_category_path)
                print(f"Moved File: '{filename}' -> {display_path}")
                files_moved += 1
            except Exception as e:
                print(f"Error moving file '{filename}': {e}")
                files_skipped += 1
        
        # --- 2. Lógica para PASTAS (Inalterada) ---
        elif os.path.isdir(item_path):
            if filename in category_folders:
                continue
            
            if is_movie_folder(item_path, VIDEO_EXTENSIONS, MIN_VIDEO_SIZE_BYTES):
                destination_folder = os.path.join(source_folder, MOVIE_FOLDER_DEST)
                
                if not os.path.exists(destination_folder):
                    try:
                        os.makedirs(destination_folder)
                        print(f"Folder created: {destination_folder}")
                    except OSError as e:
                        print(f"Error creating folder {destination_folder}: {e}")
                        folders_skipped += 1
                        continue
                
                try:
                    shutil.move(item_path, destination_folder)
                    print(f"Moved Folder: '{filename}' -> {MOVIE_FOLDER_DEST}")
                    folders_moved += 1
                except Exception as e:
                    print(f"Error moving folder '{filename}': {e}")
                    folders_skipped += 1
            else:
                folders_skipped += 1

    print(f"\n--- Organization Complete ---")
    print(f"Files moved: {files_moved}")
    print(f"Folders moved: {folders_moved}")
    print(f"Items skipped/errors: {files_skipped + folders_skipped}")

if __name__ == "__main__":
    organize_files(SOURCE_FOLDER, CATEGORIES)