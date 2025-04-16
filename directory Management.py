import os
import shutil
import mimetypes
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class AIDirectoryManager:
    def __init__(self, base_directory):
        self.base_directory = base_directory
        self.file_categories = defaultdict(list)
        self.text_files = []
        self.system_folders = ["$recycle.bin", "system volume information"]
        self.hidden_files = ["desktop.ini", "thumbs.db"]
        self.category_map = {
            "documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
            "videos": [".mp4", ".mkv", ".mov", ".avi", ".flv"],
            "music": [".mp3", ".wav", ".aac", ".flac"],
            "executables": [".exe", ".bat", ".sh", ".msi"],
            "archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
            "code": [".py", ".cpp", ".java", ".js", ".html", ".css", ".c"],
        }

    def categorize_files(self):
        """Categorizes files into specific folders based on extensions, skipping system files."""
        for root, _, files in os.walk(self.base_directory):
           
            if any(skip in root.lower() for skip in self.system_folders):
                continue

            for filename in files:
               
                if filename.lower() in self.hidden_files:
                    continue

                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                category = "unknown"

               
                for cat, extensions in self.category_map.items():
                    if file_ext in extensions:
                        category = cat
                        break
                
                
                if category == "documents" and file_ext in [".txt", ".pdf"]:
                    self.text_files.append(file_path)

                self.file_categories[category].append(file_path)

        self._organize_files()
        self._cluster_text_files()

    def _organize_files(self):
        """Moves categorized files into detailed subfolders in D:/Organized."""
        organized_dir = os.path.join(self.base_directory, "Organized")
        os.makedirs(organized_dir, exist_ok=True)

        for category, files in self.file_categories.items():
            category_folder = os.path.join(organized_dir, category)
            os.makedirs(category_folder, exist_ok=True)

            for file_path in files:
                try:
                    shutil.move(file_path, os.path.join(category_folder, os.path.basename(file_path)))
                except PermissionError:
                    print(f"Skipping {file_path} (Permission Denied)")
                except Exception as e:
                    print(f"Error moving {file_path}: {e}")

    def _cluster_text_files(self):
        """Uses AI (K-Means Clustering) to classify text files into subcategories."""
        if not self.text_files:
            return

        documents = []
        for file_path in self.text_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    documents.append(file.read())
            except Exception:
                documents.append("")

        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(documents)

        num_clusters = min(3, len(self.text_files))
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        for i, file_path in enumerate(self.text_files):
            cluster_folder = os.path.join(self.base_directory, "Organized", "Documents", f"Cluster_{labels[i]}")
            os.makedirs(cluster_folder, exist_ok=True)

            try:
                shutil.move(file_path, os.path.join(cluster_folder, os.path.basename(file_path)))
            except PermissionError:
                print(f"Skipping {file_path} (Permission Denied)")

    def analyze_directory(self):
        """Analyzes the directory and prints file statistics."""
        organized_dir = os.path.join(self.base_directory, "Organized")
        report = {}

        for root, _, files in os.walk(organized_dir):
            report[root] = {
                'file_count': len(files),
                'total_size_kb': sum(os.path.getsize(os.path.join(root, f)) for f in files) // 1024
            }

        return report


if __name__ == "__main__":
    base_dir = "D:\OS project"
    sdas = AIDirectoryManager(base_dir)
    sdas.categorize_files()
    report = sdas.analyze_directory()

    for folder, stats in report.items():
        print(f"{folder}: {stats['file_count']} files, {stats['total_size_kb']} KB")
