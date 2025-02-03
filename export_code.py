import os
import subprocess

def get_project_structure():
    """Gibt die Projektstruktur als String zurück."""
    try:
        # Verwendet tree wenn verfügbar, sonst eine einfache Alternative
        try:
            result = subprocess.run(['tree', '-I', '__pycache__|.git', '--dirsfirst'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        
        # Einfache Alternative zu tree
        structure = []
        for root, dirs, files in os.walk('.'):
            # Ignoriere __pycache__ und .git Verzeichnisse
            if '__pycache__' in root or '.git' in root:
                continue
            
            # Entferne .git aus der Liste der zu durchsuchenden Verzeichnisse
            if '.git' in dirs:
                dirs.remove('.git')
                
            level = root.count(os.sep)
            indent = '│   ' * level
            structure.append(f"{indent}{'└──' if level else ''}{os.path.basename(root)}/")
            
            for file in sorted(files):
                if file.endswith('.py') or file in ['.env', 'requirements.txt', 'README.md']:
                    structure.append(f"{indent}│   └──{file}")
        
        return '\n'.join(structure)
    
    except Exception as e:
        return f"Error getting project structure: {str(e)}"

def read_file(file_path):
    """Liest den Inhalt einer Datei und gibt ihn zurück."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}\n"

def export_code(output_file='project_code.txt'):
    """Exportiert den Code des Projekts in eine Textdatei."""
    # Relevante Python-Dateien und ihre Pfade
    files = [
        'main.py',
        'src/handlers/game_handlers.py',
        'src/handlers/admin_handlers.py',
        'src/handlers/help_handlers.py',
        'src/models/leverage_game.py',
        'src/models/leaderboard.py'
    ]
    
    with open(output_file, 'w', encoding='utf-8') as out:
        # Zuerst die Projektstruktur
        out.write("Projektstruktur:\n")
        out.write("===============\n\n")
        out.write(get_project_structure())
        out.write("\n\n")
        
        # Dann der Code
        for file_path in files:
            if os.path.exists(file_path):
                out.write(f"\n{'='*80}\n")
                out.write(f"File: {file_path}\n")
                out.write(f"{'='*80}\n\n")
                out.write(read_file(file_path))
                out.write("\n")

if __name__ == '__main__':
    export_code()
    print("Code wurde in 'project_code.txt' exportiert!")
