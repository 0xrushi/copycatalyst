import os
import argparse
from pathlib import Path
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.widgets import TextArea, Frame, Button, Label
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
import pyperclip  # Add this import at the top of your file

class FileSelectorApp:
    def __init__(self, root_dir: str, auto_select_all: bool = False):
        self.root_dir = Path(root_dir)
        self.current_dir = self.root_dir
        self.selected_files = set()
        self.auto_select_all = auto_select_all
        self.error_message = ""
        self.cursor_position = 0
        self.directory_content = []

        self.kb = KeyBindings()
        self.setup_keybindings()

        self.file_list = TextArea(text=self.get_directory_content(), read_only=True)
        self.selected_files_area = TextArea(text="", read_only=True)
        self.error_input = TextArea(height=1, prompt="Error message: ")
        self.status_bar = TextArea(height=1, read_only=True)

        self.layout = self.setup_layout()

        if self.auto_select_all:
            self.select_all_files(self.root_dir)

    def setup_keybindings(self):
        @self.kb.add('up')
        def _(event):
            self.move_cursor(-1)

        @self.kb.add('down')
        def _(event):
            self.move_cursor(1)

        @self.kb.add('left')
        def _(event):
            self.change_directory('..')

        @self.kb.add('right')
        def _(event):
            self.enter_directory()

        @self.kb.add('space')
        def _(event):
            self.toggle_selection()

        @self.kb.add('enter')
        def _(event):
            self.submit()

        @self.kb.add('c-c')
        def _(event):
            """Pressing Ctrl-C will exit the user interface."""
            event.app.exit()

    def setup_layout(self):
        return Layout(
            HSplit([
                Frame(self.file_list, title="File Explorer"),
                Frame(self.selected_files_area, title="Selected Files"),
                self.error_input,
                VSplit([
                    Button("Submit"),
                    self.status_bar
                ]),
            ])
        )

    def get_directory_content(self):
        self.directory_content = sorted(self.current_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        return "\n".join([f"{'> ' if i == self.cursor_position else '  '}{('📁 ' if item.is_dir() else '📄 ') + item.name}" for i, item in enumerate(self.directory_content)])

    def move_cursor(self, direction):
        new_position = self.cursor_position + direction
        if 0 <= new_position < len(self.directory_content):
            self.cursor_position = new_position
            self.file_list.text = self.get_directory_content()

    def change_directory(self, path):
        new_dir = (self.current_dir / path).resolve()
        if new_dir.is_dir() and new_dir.exists():
            self.current_dir = new_dir
            self.cursor_position = 0
            self.file_list.text = self.get_directory_content()

    def enter_directory(self):
        selected_item = self.directory_content[self.cursor_position]
        if selected_item.is_dir():
            self.change_directory(selected_item.name)

    def toggle_selection(self):
        selected_item = self.directory_content[self.cursor_position]
        if selected_item.is_file():
            if selected_item in self.selected_files:
                self.selected_files.remove(selected_item)
            else:
                self.selected_files.add(selected_item)
            self.update_selected_files_display()

    def select_all_files(self, path: Path):
        for root, _, files in os.walk(path):
            for file in files:
                self.selected_files.add(Path(root) / file)
        self.update_selected_files_display()

    def update_selected_files_display(self):
        self.selected_files_area.text = "\n".join(str(file) for file in self.selected_files)

    def submit(self):
        result = f"\nRoot Directory: {self.root_dir}\nSelected Files:\n"
        for file in self.selected_files:
            result += f"\n--- {file} ---\n"
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    result += content
                    result += "\n\n"
            except Exception as e:
                result += f"Error reading file: {str(e)}\n\n"
        
        result += f"\nError Message:\n{self.error_message}\n"
        
        pyperclip.copy(result)  # Copy the result to clipboard
        self.show_message("Result with file contents copied to clipboard!")

    def show_message(self, message: str):
        """Show a message in the status bar."""
        self.status_bar.text = message

    def cancel(self):
        print("Action canceled.")
        self.application.exit()

    def run(self):
        self.application = Application(layout=self.layout, key_bindings=self.kb, full_screen=True)
        self.application.run()

def main():
    parser = argparse.ArgumentParser(description="File selection and error message generation.")
    parser.add_argument("path", help="The root directory to start selection from")
    parser.add_argument("-A", "--all", action="store_true", help="Automatically select all files")
    args = parser.parse_args()

    try:
        app = FileSelectorApp(args.path, auto_select_all=args.all)
        app.run()
    except FileNotFoundError:
        print(f"Error: The specified directory '{args.path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied to access the directory '{args.path}'.")

if __name__ == "__main__":
    main()
