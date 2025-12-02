🚀 Code Splitter GUI Tool
Easily split large projects into ChatGPT-friendly parts

This tool helps developers split large codebases into clean, labeled, upload-ready text parts.
It is especially useful when sharing multi-file projects with ChatGPT, LM Arena, or any AI that limits message size.

The tool includes:
✔ A GUI built with Tkinter
✔ Automatic file/folder selection
✔ Multi-file merging and line-based splitting
✔ Copy-to-clipboard buttons for each part
✔ Optional automatic upload using OpenAI API (1.x)
✔ Smart part counting and instructions for ChatGPT
✔ Configurable target platforms (ChatGPT / LM Arena)

📸 Screenshot

(Add your screenshot here if you want)

✨ Features
🔹 1. Add Files or Entire Folders

Recursively scans folders and adds all files.

🔹 2. Line-based Splitting

Choose the maximum number of lines per PART:

ChatGPT default: 200 lines

LM Arena default: 800 lines

🔹 3. Clean, Well-Structured Output

Each split file includes:

[PART X of Y]
# File: relative/path/to/file
<content...>
[END PART X]

🔹 4. One-Click Copy to Clipboard

Each generated part appears as a button → click to copy.

🔹 5. Automatic Upload (Optional)

If you provide an OpenAI API key, the tool can automatically send all PARTs to a model (e.g. gpt-3.5-turbo).

🔹 6. Saves your OpenAI API key locally

Stored in api_key.json.

📦 Installation
1. Clone the repository
git clone https://github.com/rajneesh-gobin/code-splitter-gui.git
cd code-splitter-gui

2. Install dependencies
pip install -r requirements.txt


Dependencies include:

tkinter (built-in on Windows/macOS)

pyperclip

openai (v1.x)

ttk

json / os / math (built-in modules)

▶️ Usage
Run the tool
python splitter.py

1. Add Files / Add Folder

Select individual files or whole directories.

2. Choose Target Platform

This automatically sets recommended safe line limits.

3. Click "Start Split"

Parts are generated in output_parts/.

4. Use the buttons to copy each PART

Paste directly into ChatGPT or elsewhere.

5. (Optional) Upload all parts via OpenAI API

Enter your API key → press Upload All PARTs.

📁 Project Structure
code-splitter-gui/
│
├── splitter.py          # Main GUI application
├── requirements.txt     # Python dependencies
├── README.md            # This documentation
└── LICENSE              # MIT License

🔧 Configuration
Default Safe Line Limits
TARGET_LINE_DEFAULTS = {
    "ChatGPT": 200,
    "LM Arena": 800
}


You can adjust these in splitter.py.

💡 Why This Tool Exists

ChatGPT and many AI models restrict message length.
Sharing large projects requires splitting them into multiple parts — manually doing this is tedious.

This tool:

Combines all files

Splits them cleanly

Labels parts neatly

Prepares everything for AI processing

It saves time, avoids mistakes, and works with any project.

🤝 Contributing

Pull requests are welcome!
If you want to improve features or UI, feel free to fork the repo.

📜 License

This project is released under the MIT License.