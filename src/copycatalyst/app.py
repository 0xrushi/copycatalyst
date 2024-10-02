import os
import pyperclip
from pathlib import Path
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, VSplit, Layout, Window, ScrollbarMargin
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import TextArea, Button, Label, Frame
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document

class FileSelectorApp:
    def __init__(self, root_dir: str, auto_select_all: bool = False):
        self.root_dir = Path(root_dir)  
        self.current_dir = self.root_dir
        self.auto_select_all = auto_select_all
        self.selected_files = set()
        self.error_message = ""
        self.cursor_position = 0
        self.directory_content = []
        self.search_query = ""
        self.file_list_buffer = Buffer()
        self.selected_files_buffer = Buffer()
        self.total_files_selected = TextArea(height=1, read_only=True)
        self.search_buffer = Buffer()
        self.search_window = Window(
            content=BufferControl(buffer=self.search_buffer, focusable=True),
            height=1,
            dont_extend_height=True
        )
        self.status_bar = TextArea(height=1, read_only=True)

        self.kb = KeyBindings()
        self.setup_keybindings()

        self.file_list_window = Window(
            content=BufferControl(buffer=self.file_list_buffer),
            right_margins=[ScrollbarMargin(display_arrows=True)]
        )
        self.selected_files_window = Window(
            content=BufferControl(buffer=self.selected_files_buffer),
            right_margins=[ScrollbarMargin(display_arrows=True)]
        )

        self.layout = self.setup_layout()
        self.update_total_files_count()

        if self.auto_select_all:
            self.select_all_files(self.root_dir)
        
        self.update_file_list()  # Add this line

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

        @self.kb.add('c-f')
        def _(event):
            """Focus search input."""
            event.app.layout.focus(self.search_window)

        @self.kb.add('enter', filter=Condition(lambda: get_app().layout.current_window == self.search_window))
        def _(event):
            """Apply search filter."""
            self.search_query = self.search_buffer.text
            self.cursor_position = 0  # Reset cursor position when applying a new search
            self.update_file_list()
            event.app.layout.focus(self.file_list_window)

        @self.kb.add('tab')
        def _(event):
            """Switch focus between file list and selected files."""
            if get_app().layout.has_focus(self.file_list_window):
                get_app().layout.focus(self.selected_files_window)
            else:
                get_app().layout.focus(self.file_list_window)

        @self.kb.add('up', filter=Condition(lambda: get_app().layout.has_focus(self.selected_files_window)))
        def _(event):
            """Scroll up in selected files window."""
            self.selected_files_buffer.cursor_up()

        @self.kb.add('down', filter=Condition(lambda: get_app().layout.has_focus(self.selected_files_window)))
        def _(event):
            """Scroll down in selected files window."""
            self.selected_files_buffer.cursor_down()

        @self.kb.add('pageup', filter=Condition(lambda: get_app().layout.has_focus(self.selected_files_window)))
        def _(event):
            """Page up in selected files window."""
            for _ in range(10):
                self.selected_files_buffer.cursor_up()

        @self.kb.add('pagedown', filter=Condition(lambda: get_app().layout.has_focus(self.selected_files_window)))
        def _(event):
            """Page down in selected files window."""
            for _ in range(10):
                self.selected_files_buffer.cursor_down()

    def setup_layout(self):
        return Layout(
            HSplit([
                Frame(self.file_list_window, title="File Explorer"),
                Frame(self.selected_files_window, title="Selected Files"),
                Window(height=1, content=FormattedTextControl("Search: ")),
                self.search_window,
                self.total_files_selected,
                VSplit([
                    Button("Submit", handler=self.submit),
                    self.status_bar
                ]),
            ])
        )

    def get_directory_content(self):
        self.directory_content = sorted(self.current_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        self.filtered_content = self.filter_content(self.directory_content)
        return "\n".join([
            f"{'> ' if i == self.cursor_position else '  '}"
            f"{'📁 ' if item.is_dir() else '📄 '}"
            f"{'[x] ' if item in self.selected_files else '[ ] '}"
            f"{item.name}"
            for i, item in enumerate(self.filtered_content)
        ])

    def filter_content(self, content):
        if self.search_query:
            return [item for item in content if self.search_query.lower() in item.name.lower()]
        return content

    def move_cursor(self, direction):
        new_position = self.cursor_position + direction
        if 0 <= new_position < len(self.filtered_content):
            self.cursor_position = new_position
            self.update_file_list()

    def change_directory(self, path):
        new_dir = (self.current_dir / path).resolve()
        if new_dir.is_dir() and new_dir.exists():
            self.current_dir = new_dir
            self.cursor_position = 0
            self.file_list_buffer.text = self.get_directory_content()

    def enter_directory(self):
        selected_item = self.directory_content[self.cursor_position]
        if selected_item.is_dir():
            self.change_directory(selected_item.name)

    def toggle_selection(self):
        if 0 <= self.cursor_position < len(self.filtered_content):
            selected_item = self.filtered_content[self.cursor_position]
            if selected_item.is_file():
                if selected_item in self.selected_files:
                    self.selected_files.remove(selected_item)
                else:
                    self.selected_files.add(selected_item)
                self.update_selected_files_display()
                self.update_file_list()
        self.update_total_files_count()

    def select_all_files(self, path):
        for root, _, files in os.walk(path):
            for file in files:
                self.selected_files.add(Path(root) / file)
        self.update_selected_files_display()
        self.update_file_list()  # Add this line
        self.update_total_files_count()

    def update_selected_files_display(self):
        self.selected_files_buffer.text = "\n".join(str(file) for file in self.selected_files)

    def update_file_list(self):
        self.file_list_buffer.text = self.get_directory_content()

    def update_total_files_count(self):
        self.total_files_selected.text = f"Total Files Selected: {len(self.selected_files)}"

    def submit(self):
        PROMPT = """Identify potential issues in the provided files 
Provide a clear explanation of the possible causes and suggested fixes.\n
Root Directory: {}
        """
        result = PROMPT.format(self.root_dir)
        result += "\n\nSelected Files:\n"
        # result = f"Identify potential issues in the provided files \nRoot Directory: {self.root_dir}\nSelected Files:\n"
        for file in self.selected_files:
            result += f"\n--- {file} ---\n"
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    result += content
                    result += "\n\n"
            except Exception as e:
                result += f"Error reading file: {str(e)}\n\n"
        result += ""
        result += f"\nError Message:\n\n"
        
        pyperclip.copy(result)  # Copy the result to clipboard
        self.show_message("Result with file contents copied to clipboard!")

    def show_message(self, message: str):
        """Show a message in the status bar."""
        self.status_bar.text = message

    def cancel(self):
        print("Action canceled.")
        self.application.exit()

    def run(self):
        self.application = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=True
        )
        self.application.run()