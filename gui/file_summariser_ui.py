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
# Voice + GPT
try:
    from voice.speaker import speak, speak_and_wait
    from voice.listener import listen_command
except Exception:
    speak = None
    speak_and_wait = None
    listen_command = None

try:
    from gpt import GPTHandler
except Exception:
    GPTHandler = None


class FileSummariserGUI:
    def __init__(self, root, main_menu_ref):
        self.root = root
        self.main_menu_ref = main_menu_ref
        self.file_summariser = FileSummariser()
        self.file_widgets = {}  # Track file widget references for removal
        self.gpt_handler = GPTHandler() if GPTHandler else None
        self.summary_result_frame = None
        self.summary_output_text = None
        # Modal summary window state
        self.summary_window = None
        self._summary_saved = True
        self._last_summary_filename = None
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
        """Process the file summary request using core + GPT and display results"""
        # Enforce single summary window at a time
        try:
            if self.summary_window and self.summary_window.winfo_exists():
                messagebox.showwarning("Summary Window Open", "Please close the current summary window before generating a new one.")
                return
        except Exception:
            pass
        uploaded_files = self.file_summariser.get_uploaded_files()

        if not uploaded_files:
            messagebox.showwarning("No Files", "Please upload at least one file to summarise.")
            if speak_and_wait:
                speak_and_wait("Please upload a file for me to summarise, sir.")
            return

        instruction = self.summary_text.get('1.0', 'end-1c').strip()
        if not instruction or instruction == "Describe how you'd like your file summarised (e.g. 'Summarise in bullet points', 'Write as a short news article'...":
            instruction = "Provide a general summary"

        target_file = uploaded_files[0]  # Start with first for now
        result = self.file_summariser.summarise(target_file, instruction)

        if not result.get('success'):
            msg = result.get('message', 'An error occurred during summarisation.')
            self.show_status_message(f"✗ {msg}", "error")
            messagebox.showerror("Summary Error", msg)
            if speak_and_wait:
                speak_and_wait(f"Sorry sir, {msg}")
            return

        # Success: display in modal
        summary_text = result.get('summary', '')
        self.show_summary_result(Path(target_file).name, summary_text, result.get('kind', 'general'))
        # Speak confirmation (not reading the whole summary by default)
        if speak_and_wait:
            speak_and_wait("Summary completed successfully, sir.")

    def show_help(self):
        """Show help information"""
        help_text = """File Summariser Help:

1. Click the upload area or drag files to add them
2. Supported file types: PDF, DOCX, CSV, TXT
3. Describe how you want the summary formatted (e.g., timeline, highlights, code summary)
4. Click the arrow button or use the 🎤 button to speak your request
5. After a summary completes, you can copy it, read it aloud, or summarise another file
6. Use the back button to return to main menu"""

        messagebox.showinfo("Help", help_text)

    def toggle_voice(self):
        """Voice input: dynamic greeting, listen, and process summary/identity/name."""
        # Ensure there is a file
        uploaded_files = self.file_summariser.get_uploaded_files()
        if not uploaded_files:
            if speak_and_wait:
                speak_and_wait("Please upload a file first, sir.")
            else:
                messagebox.showinfo("Voice", "Please upload a file first.")
            return

        # Dynamic greeting tailored to File Summariser
        greet = None
        if self.gpt_handler:
            try:
                # Use specialised summariser prompt if available
                if hasattr(self.gpt_handler, 'get_summariser_prompt'):
                    greet = self.gpt_handler.get_summariser_prompt()
                else:
                    greet = self.gpt_handler.get_dynamic_prompt()
            except Exception:
                greet = None
        if not greet:
            greet = "Good day sir, what would you like me to summarise?"

        if speak_and_wait:
            speak_and_wait(greet)
        
        # Listen
        cmd = ""
        if listen_command:
            try:
                cmd = listen_command(timeout=10, phrase_time_limit=15) or ""
            except Exception as e:
                print(f"Voice listen error: {e}")
                cmd = ""
        if not cmd.strip():
            if speak_and_wait:
                speak_and_wait("I didn't catch that, sir. Please try again.")
            return

        # Identity/name handling for this page
        lower = cmd.lower().strip()
        if ("your name" in lower) or ("what's your name" in lower) or ("what is your name" in lower) or (lower.startswith("name") and "your" in lower):
            if self.gpt_handler:
                try:
                    reply = self.gpt_handler.get_name_response()
                except Exception:
                    reply = "My name is DeskPilot, sir."
            else:
                reply = "My name is DeskPilot, sir."
            if speak_and_wait:
                speak_and_wait(reply)
            return

        if any(p in lower for p in ["who are you", "what can you do", "your capabilities", "capabilities", "functions", "introduce yourself", "what are you"]):
            # Tailor for file summariser page
            if self.gpt_handler:
                try:
                    intro = "I am DeskPilot sir, your file summarisation assistant here to help on your desktop."
                except Exception:
                    pass
            else:
                intro = "I am DeskPilot sir, your file summarisation assistant here to help on your desktop."
            extra = "I can summarise files, create timelines, extract highlights, and explain code contents."
            if speak_and_wait:
                speak_and_wait(f"{intro} {extra}")
            return

        # Otherwise treat as a summary request
        target = uploaded_files[0]
        instruction = cmd
        res = self.file_summariser.summarise(target, instruction)
        if not res.get('success'):
            msg = res.get('message', 'I could not complete that request.')
            if speak_and_wait:
                speak_and_wait(f"Sorry sir, {msg}")
            messagebox.showerror("Summary Error", msg)
            return

        self.show_summary_result(Path(target).name, res.get('summary',''), res.get('kind','general'))
        if speak_and_wait:
            speak_and_wait("Summary completed successfully, sir.")

    def show_summary_result(self, filename: str, summary_text: str, kind: str):
        """Open a modal window (popup) to display the summary with Copy/Save controls."""
        # Close any stale window object
        try:
            if self.summary_window and not self.summary_window.winfo_exists():
                self.summary_window = None
        except Exception:
            self.summary_window = None

        # Create modal only if no other exists
        if self.summary_window and self.summary_window.winfo_exists():
            try:
                self.summary_window.lift()
            except Exception:
                pass
            messagebox.showwarning("Summary Window Open", "Please close the current summary window before generating a new one.")
            return

        self._summary_saved = False
        self._last_summary_filename = filename

        self.summary_window = tk.Toplevel(self.root)
        self.summary_window.title(f"Summary of {filename} — {kind}")
        # Place to the left side for better focus; allow resizing/moving
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            self.summary_window.geometry(f"720x560+{max(20, rx - 10)}+{max(40, ry + 20)}")
        except Exception:
            self.summary_window.geometry("720x560+50+80")
        self.summary_window.configure(bg="#ffffff")
        self.summary_window.transient(self.root)
        self.summary_window.grab_set()  # make modal-like

        # Header with centered title and right-aligned buttons
        header = tk.Frame(self.summary_window, bg="#ffffff")
        header.pack(fill=tk.X, padx=12, pady=(10, 6))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        title_lbl = tk.Label(
            header,
            text=f"Summary of {filename} ({kind})",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#333333",
            anchor="center"
        )
        title_lbl.grid(row=0, column=0, sticky="n")

        btns_frame = tk.Frame(header, bg="#ffffff")
        btns_frame.grid(row=0, column=1, sticky="ne")

        # Text area with scrollbar
        text_frame = tk.Frame(self.summary_window, bg="#ffffff")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.summary_output_text = tk.Text(
            text_frame,
            font=("Arial", 12),
            bg="#ffffff",
            fg="#222222",
            relief='solid',
            borderwidth=1,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.summary_output_text.pack(fill=tk.BOTH, expand=True)
        self.summary_output_text.insert('1.0', summary_text)
        scrollbar.config(command=self.summary_output_text.yview)

        # Button callbacks
        def copy_to_clipboard():
            try:
                self.summary_window.clipboard_clear()
                self.summary_window.clipboard_append(self.summary_output_text.get('1.0', 'end-1c'))
                messagebox.showinfo("Copied", "Summary copied to clipboard.")
            except Exception as e:
                messagebox.showerror("Copy Error", f"Failed to copy: {e}")

        def save_summary_as():
            try:
                init_name = (Path(filename).stem or "summary") + ".txt"
            except Exception:
                init_name = "summary.txt"
            fpath = filedialog.asksaveasfilename(
                parent=self.summary_window,
                title="Save Summary As",
                defaultextension=".txt",
                initialfile=init_name,
                filetypes=[
                    ("Text file", "*.txt"),
                    ("Markdown", "*.md"),
                    ("All files", "*.*")
                ]
            )
            if not fpath:
                return
            try:
                content = self.summary_output_text.get('1.0', 'end-1c')
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._summary_saved = True
                messagebox.showinfo("Saved", f"Summary saved to:\n{fpath}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save: {e}")

        # Buttons: Copy and Save (top-right)
        copy_btn = tk.Button(btns_frame, text="Copy", command=copy_to_clipboard, bg="#f5f5f5")
        save_btn = tk.Button(btns_frame, text="Save", command=save_summary_as, bg="#e8f0fe")
        copy_btn.pack(side=tk.LEFT, padx=(0, 6))
        save_btn.pack(side=tk.LEFT)

        # Close handling with save prompt
        def on_close():
            try:
                if not self._summary_saved:
                    resp = messagebox.askyesno(
                        "Unsaved Summary",
                        "Would you like to save your summary before closing?"
                    )
                    if resp:
                        # Attempt save; if user cancels Save As, keep window open
                        before = self._summary_saved
                        save_summary_as()
                        if not self._summary_saved and before == self._summary_saved:
                            return
                self.summary_window.destroy()
                self.summary_window = None
                self._summary_saved = True
            except Exception:
                try:
                    self.summary_window.destroy()
                finally:
                    self.summary_window = None
                    self._summary_saved = True

        self.summary_window.protocol("WM_DELETE_WINDOW", on_close)

    def back_to_main_menu(self):
        """Return to main menu"""
        if hasattr(self.main_menu_ref, 'setup_main_menu'):
            self.main_menu_ref.setup_main_menu()
        else:
            messagebox.showerror("Navigation Error", "Could not return to main menu.")