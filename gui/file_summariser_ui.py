import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import sys
from pathlib import Path

# Add project directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import SUPPORTED_FILE_TYPES
from core.file_summariser import FileSummariser


class FileSummariserGUI:
    def __init__(self, root, main_menu_ref):
        self.root = root
        self.main_menu_ref = main_menu_ref
        self.file_summariser = FileSummariser()
        self.file_widgets = {}  # Track file widget references for removal
        self.setup_file_summariser_ui()

    def setup_file_summariser_ui(self):
        """Setup the file summariser interface"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="File Summariser",
            font=("Arial", 28, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(20, 40))

        # File upload area
        self.create_upload_area(main_frame)

        # File list area
        self.create_file_list_area(main_frame)

        # Summary input area
        self.create_summary_input_area(main_frame)

        # Bottom navigation area
        self.create_navigation_area(main_frame)

    def create_upload_area(self, parent):
        """Create the drag and drop / file upload area"""
        upload_frame = tk.Frame(parent, bg='#f0f0f0')
        upload_frame.pack(fill=tk.X, pady=(0, 20))

        # Upload area with dashed border effect
        self.upload_area = tk.Frame(
            upload_frame,
            bg='#ffffff',
            relief='solid',
            borderwidth=2,
            height=120
        )
        self.upload_area.pack(fill=tk.X, padx=10)
        self.upload_area.pack_propagate(False)

        # Upload text
        self.upload_label = tk.Label(
            self.upload_area,
            text="Drag and drop your file here, or\nclick to upload (.csv .docx .pdf only)",
            font=("Arial", 12),
            bg='#ffffff',
            fg='#666666',
            justify=tk.CENTER
        )
        self.upload_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Make upload area clickable
        self.upload_area.bind("<Button-1>", self.browse_file)
        self.upload_label.bind("<Button-1>", self.browse_file)

        # Add hover effects
        self.upload_area.bind("<Enter>", self.on_upload_area_enter)
        self.upload_area.bind("<Leave>", self.on_upload_area_leave)
        self.upload_label.bind("<Enter>", self.on_upload_area_enter)
        self.upload_label.bind("<Leave>", self.on_upload_area_leave)

        # Configure drag and drop functionality
        self.setup_drag_and_drop()

    def create_file_list_area(self, parent):
        """Create area to display uploaded files"""
        self.file_list_frame = tk.Frame(parent, bg='#f0f0f0')
        self.file_list_frame.pack(fill=tk.X, pady=(0, 20))

    def create_summary_input_area(self, parent):
        """Create the summary customization input area"""
        input_frame = tk.Frame(parent, bg='#f0f0f0')
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Text input area
        self.summary_text = tk.Text(
            input_frame,
            height=6,
            font=("Arial", 11),
            bg='#ffffff',
            fg='#333333',
            relief='solid',
            borderwidth=1,
            wrap=tk.WORD
        )
        self.summary_text.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Placeholder text
        placeholder_text = "Describe how you'd like your file summarised (e.g. 'Summarise in bullet points', 'Write as a short news article'..."
        self.summary_text.insert('1.0', placeholder_text)
        self.summary_text.configure(fg='#999999')

        # Bind events for placeholder behavior
        self.summary_text.bind('<FocusIn>', self.on_summary_text_focus_in)
        self.summary_text.bind('<FocusOut>', self.on_summary_text_focus_out)

        # Send button
        send_btn = tk.Button(
            input_frame,
            text="→",
            font=("Arial", 16, "bold"),
            bg='#007ACC',
            fg='#ffffff',
            relief='flat',
            borderwidth=0,
            width=3,
            height=1,
            command=self.process_summary
        )
        send_btn.pack(anchor=tk.E, padx=10)

    def create_navigation_area(self, parent):
        """Create bottom navigation with back button and help"""
        nav_frame = tk.Frame(parent, bg='#f0f0f0')
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

        # Help button (left side)
        help_btn = tk.Button(
            nav_frame,
            text="?",
            font=("Arial", 14, "bold"),
            bg='#ffffff',
            fg='#333333',
            relief='raised',
            borderwidth=2,
            width=3,
            height=2,
            command=self.show_help
        )
        help_btn.pack(side=tk.LEFT)

        # Back to main menu button (center)
        back_btn = tk.Button(
            nav_frame,
            text="BACK TO\nMAIN\nMENU",
            font=("Arial", 10, "bold"),
            bg='#ffffff',
            fg='#333333',
            relief='raised',
            borderwidth=2,
            command=self.back_to_main_menu
        )
        back_btn.pack(side=tk.LEFT, expand=True, padx=20)

        # Voice button placeholder (right side)
        voice_btn = tk.Button(
            nav_frame,
            text="🎤",
            font=("Arial", 14),
            bg='#ffffff',
            fg='#333333',
            relief='raised',
            borderwidth=2,
            width=3,
            height=2,
            command=self.toggle_voice
        )
        voice_btn.pack(side=tk.RIGHT)

    def browse_file(self, event=None):
        """Open file browser to select file"""
        filetypes = [
            ("All supported", "*.pdf *.docx *.csv *.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        try:
            filename = filedialog.askopenfilename(
                title="Select file to summarise",
                filetypes=filetypes
            )

            if filename:
                self.handle_file_upload(filename)
        except Exception as e:
            print(f"Error opening file dialog: {e}")
            messagebox.showerror("File Dialog Error", "Could not open file browser. Please try again.")

    def setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        try:
            # Enable drag and drop for the upload area
            self.upload_area.drop_target_register(DND_FILES)
            self.upload_area.dnd_bind('<<Drop>>', self.on_file_drop)

            # Also enable for the label
            self.upload_label.drop_target_register(DND_FILES)
            self.upload_label.dnd_bind('<<Drop>>', self.on_file_drop)

        except Exception as e:
            print(f"Drag and drop setup failed: {e}")
            # Fallback: show message that drag and drop isn't available
            self.upload_label.configure(text="Click to upload files\n(.csv .docx .pdf .txt only)")

    def on_file_drop(self, event):
        """Handle file drop event"""
        files = event.data.split()
        for file_path in files:
            # Remove curly braces if present (Windows specific)
            file_path = file_path.strip('{}')
            self.handle_file_upload(file_path)

    def handle_file_upload(self, file_path):
        """Handle file upload (both drag-drop and browse)"""
        success, message = self.file_summariser.add_file(file_path)

        if success:
            self.add_file_to_list(file_path)
            self.show_status_message(f"✓ {message}", "success")
        else:
            self.show_status_message(f"✗ {message}", "error")
            messagebox.showerror("File Upload Error", message)

    def add_file_to_list(self, filepath):
        """Add validated file to the file list display"""
        file_info = self.file_summariser.get_file_info(filepath)

        if not file_info.get('is_valid', False):
            return

        # Create file item widget
        file_item = tk.Frame(self.file_list_frame, bg='#ffffff', relief='solid', borderwidth=1)
        file_item.pack(fill=tk.X, padx=10, pady=5)

        # Store reference for removal
        self.file_widgets[filepath] = file_item

        # File icon and info frame
        file_info_frame = tk.Frame(file_item, bg='#ffffff')
        file_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)

        # File icon (using appropriate emoji based on file type)
        file_ext = file_info.get('extension', '')
        if file_ext == '.pdf':
            icon = "📄"
        elif file_ext == '.docx':
            icon = "📝"
        elif file_ext == '.csv':
            icon = "📊"
        elif file_ext == '.txt':
            icon = "📃"
        else:
            icon = "📄"

        icon_label = tk.Label(
            file_info_frame,
            text=icon,
            font=("Arial", 16),
            bg='#ffffff'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # File details frame
        details_frame = tk.Frame(file_info_frame, bg='#ffffff')
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # File name
        name_label = tk.Label(
            details_frame,
            text=file_info['name'],
            font=("Arial", 12, "bold"),
            bg='#ffffff',
            fg='#333333',
            anchor='w'
        )
        name_label.pack(anchor='w', fill=tk.X)

        # File size and type info
        size_info = f"{file_info['size_readable']} • {file_ext.upper()[1:]} file"
        size_label = tk.Label(
            details_frame,
            text=size_info,
            font=("Arial", 9),
            bg='#ffffff',
            fg='#666666',
            anchor='w'
        )
        size_label.pack(anchor='w', fill=tk.X)

        # Remove button
        remove_btn = tk.Button(
            file_item,
            text="Remove",
            font=("Arial", 10),
            bg='#ffffff',
            fg='#dc3545',
            relief='flat',
            borderwidth=0,
            command=lambda: self.remove_file(filepath)
        )
        remove_btn.pack(side=tk.RIGHT, padx=10, pady=8)

        # Add hover effect to remove button
        remove_btn.bind("<Enter>", lambda e: remove_btn.configure(bg='#f8f9fa'))
        remove_btn.bind("<Leave>", lambda e: remove_btn.configure(bg='#ffffff'))

    def remove_file(self, filepath):
        """Remove file from list"""
        success = self.file_summariser.remove_file(filepath)
        if success and filepath in self.file_widgets:
            self.file_widgets[filepath].destroy()
            del self.file_widgets[filepath]
            self.show_status_message(f"✓ File removed", "success")

    def on_upload_area_enter(self, event):
        """Handle mouse enter on upload area"""
        self.upload_area.configure(bg='#f8f9fa', relief='solid', borderwidth=2)

    def on_upload_area_leave(self, event):
        """Handle mouse leave on upload area"""
        self.upload_area.configure(bg='#ffffff', relief='solid', borderwidth=2)

    def show_status_message(self, message, status_type="info"):
        """Show temporary status message in the upload area"""
        original_text = self.upload_label.cget("text")
        original_color = self.upload_label.cget("fg")

        # Set color based on status type
        if status_type == "success":
            color = "#28a745"
        elif status_type == "error":
            color = "#dc3545"
        else:
            color = "#007bff"

        # Show status message
        self.upload_label.configure(text=message, fg=color)

        # Reset after 3 seconds
        self.root.after(3000, lambda: self.upload_label.configure(text=original_text, fg=original_color))

    def on_summary_text_focus_in(self, event):
        """Handle focus in on summary text area"""
        if self.summary_text.get('1.0',
                                 'end-1c') == "Describe how you'd like your file summarised (e.g. 'Summarise in bullet points', 'Write as a short news article'...":
            self.summary_text.delete('1.0', tk.END)
            self.summary_text.configure(fg='#333333')

    def on_summary_text_focus_out(self, event):
        """Handle focus out on summary text area"""
        if not self.summary_text.get('1.0', 'end-1c').strip():
            placeholder_text = "Describe how you'd like your file summarised (e.g. 'Summarise in bullet points', 'Write as a short news article'..."
            self.summary_text.insert('1.0', placeholder_text)
            self.summary_text.configure(fg='#999999')

    def process_summary(self):
        """Process the file summary request"""
        uploaded_files = self.file_summariser.get_uploaded_files()

        if not uploaded_files:
            messagebox.showwarning("No Files", "Please upload at least one file to summarise.")
            return

        summary_instruction = self.summary_text.get('1.0', 'end-1c').strip()
        if not summary_instruction or summary_instruction == "Describe how you'd like your file summarised (e.g. 'Summarise in bullet points', 'Write as a short news article'...":
            summary_instruction = "Provide a general summary"

        # TODO: Call the GPT processing logic here
        file_names = [Path(f).name for f in uploaded_files]
        messagebox.showinfo(
            "Processing",
            f"Processing {len(uploaded_files)} file(s): {', '.join(file_names)}\n\n"
            f"Summary request: {summary_instruction}\n\n"
            f"GPT integration coming next..."
        )

    def show_help(self):
        """Show help information"""
        help_text = """File Summariser Help:

1. Click the upload area or drag files to add them
2. Supported file types: PDF, DOCX, CSV
3. Describe how you want the summary formatted
4. Click the arrow button to process
5. Use the back button to return to main menu"""

        messagebox.showinfo("Help", help_text)

    def toggle_voice(self):
        """Toggle voice input (placeholder)"""
        messagebox.showinfo("Voice Input", "Voice input functionality coming soon!")

    def back_to_main_menu(self):
        """Return to main menu"""
        if hasattr(self.main_menu_ref, 'setup_main_menu'):
            self.main_menu_ref.setup_main_menu()
        else:
            messagebox.showerror("Navigation Error", "Could not return to main menu.")