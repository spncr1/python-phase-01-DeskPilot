import tkinter as tk
from tkinter import filedialog, messagebox
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Define supported file types for the file summarizer
SUPPORTED_FILE_TYPES = ['.txt', '.pdf', '.docx', '.csv']

class DummyFileSummariser:
    """Dummy file summarizer for testing"""
    @staticmethod
    def summarize_file(file_path, instructions):
        return "This is a test summary. The actual summarization functionality is not available in this test version."

class FileSummariserGUI:
    """GUI for the File Summarizer module"""

    def __init__(self, root, main_menu):
        self.root = root
        self.main_menu = main_menu
        self.summariser = DummyFileSummariser()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for the file summarizer"""
        self.root.title("File Summarizer (Test Mode)")
        self.root.geometry("800x600")

        # Main container
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # File selection
        file_frame = tk.Frame(container)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(file_frame, text="File Path:").pack(side=tk.LEFT)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        browse_btn = tk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT)

        # Instructions
        tk.Label(container, text="Instructions:").pack(anchor=tk.W, pady=(10, 0))
        self.instructions_text = tk.Text(container, height=5, wrap=tk.WORD)
        self.instructions_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=10)
        
        summarize_btn = tk.Button(btn_frame, text="Summarize", command=self.summarize_file)
        summarize_btn.pack(side=tk.LEFT, padx=5)
        
        if self.main_menu:
            back_btn = tk.Button(btn_frame, text="Back to Main Menu", 
                               command=self.main_menu.setup_main_menu)
            back_btn.pack(side=tk.RIGHT, padx=5)

        # Status
        self.status_var = tk.StringVar()
        status_label = tk.Label(container, textvariable=self.status_var, fg="blue")
        status_label.pack(pady=5)

        # Summary
        tk.Label(container, text="Summary:").pack(anchor=tk.W)
        self.summary_text = tk.Text(container, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    def browse_file(self):
        """Open a file dialog to select a file"""
        file_types = [
            ("Supported Files", "*.txt *.pdf *.docx *.csv"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(title="Select File", filetypes=file_types)
        if file_path:
            self.file_path_var.set(file_path)

    def summarize_file(self):
        """Handle file summarization"""
        file_path = self.file_path_var.get().strip()
        instructions = self.instructions_text.get("1.0", tk.END).strip()

        if not file_path:
            messagebox.showerror("Error", "Please select a file first")
            return

        try:
            self.status_var.set("Summarizing...")
            self.root.update()
            
            # Call the dummy summarizer
            summary = self.summariser.summarize_file(file_path, instructions)
            
            # Show the summary
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert(tk.END, summary)
            self.summary_text.config(state=tk.DISABLED)
            
            self.status_var.set("Summary complete! (Test Mode)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to summarize file: {str(e)}")
            self.status_var.set("Error occurred")

if __name__ == "__main__":
    root = tk.Tk()
    gui = FileSummariserGUI(root, None)
    root.mainloop()