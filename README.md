<img src="images/logo.jpeg" alt="Logo" style="max-width: auto; height: 200px;">


**CopyCatalyst** is a tool designed to make copying code and files easier for interacting with Large Language Models (LLMs). It lets you quickly select multiple files and automatically format their contents with filenames, all copied to your clipboard.

![Screen Recording Oct 01](https://github.com/user-attachments/assets/6f737928-360d-418f-800b-4aca37f17eee)

## Installation

```
git clone https://github.com/0xrushi/copycatalyst.git
cd copycatalyst
pip install -e .
```


### Usage

**To run copycatalyst in current dir**
```
copycatalyst .
```

**To select all files in current dir**
```
copycatalyst -A .
```

**Navigation:**

* Use the arrow keys (`↑`, `↓`, `←`, `→`) to navigate the file list.
* Press `Space` to add file to selection.
* Press `Ctrl+F` to search for a file by name.
* Press `Enter` to:
  * Search for a specific file (when in search mode).
  * Submit the selected files and copy the formatted content to the clipboard.
* Press `Ctrl+C` to exit CopyCatalyst.
