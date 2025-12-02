import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pyperclip
import json
import openai  # Ensure openai>=1.0.0

# ---------- Global Variables ----------
file_list = []
all_parts_global = []
current_copy_index = 0
TARGET_LINE_DEFAULTS = {"ChatGPT": 200, "LM Arena": 800}
API_KEY_FILE = "api_key.json"

# ---------- Splitter Functions ----------

def add_files():
    files = filedialog.askopenfilenames(title="Select Files to Add")
    if files:
        for f in files:
            if f not in file_list:
                file_list.append(f)
        update_file_display()
        auto_set_safe_lines()

def add_folder():
    folder = filedialog.askdirectory(title="Select Folder to Add")
    if folder:
        for root_dir, _, files in os.walk(folder):
            for f in files:
                file_path = os.path.join(root_dir, f)
                if file_path not in file_list:
                    file_list.append(file_path)
        update_file_display()
        auto_set_safe_lines()

def clear_files():
    global file_list, all_parts_global, current_copy_index
    file_list.clear()
    update_file_display()
    txt_max_lines.delete(0, tk.END)
    lbl_estimate.config(text="")
    all_parts_global = []
    current_copy_index = 0
    clear_output_folder(os.path.join(os.getcwd(), "output_parts"))
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

def update_file_display():
    listbox_files.delete(0, tk.END)
    for f in file_list:
        listbox_files.insert(tk.END, os.path.relpath(f, os.getcwd()))
    if not file_list:
        listbox_files.insert(tk.END, "No files selected")

def auto_set_safe_lines(event=None):
    target = cmb_target.get()
    safe_lines = TARGET_LINE_DEFAULTS.get(target, 200)
    txt_max_lines.delete(0, tk.END)
    txt_max_lines.insert(0, str(safe_lines))
    total_lines = sum(len(open(f, "r", encoding="utf-8", errors="ignore").readlines()) for f in file_list)
    estimated_parts = math.ceil(total_lines / safe_lines) if safe_lines else 0
    lbl_estimate.config(text=f"Estimated total PARTs: {estimated_parts}")

def clear_output_folder(output_folder):
    if os.path.exists(output_folder):
        for f in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, f))
    else:
        os.makedirs(output_folder)

def copy_to_clipboard(file_path, part_label):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            pyperclip.copy(f.read())
        lbl_copy_feedback.config(text=f"Copied {part_label}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy: {e}")

def split_files():
    global all_parts_global, current_copy_index
    if not file_list:
        messagebox.showerror("Error", "No files selected!")
        return

    try:
        max_lines = int(txt_max_lines.get())
        if max_lines <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Invalid max lines value!")
        return

    output_folder = os.path.join(os.getcwd(), "output_parts")
    clear_output_folder(output_folder)

    part_counter = 1
    current_part_lines = 0
    current_part_content = ""
    all_parts = []

    # Clear previous scrollable buttons
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Instruction text only at the top of the first part
    ai_instruction = """I need to share a large codebase, so I'll send it in multiple parts.

Please:
- Just say "OK, waiting for all parts" after this message.
- Do NOT start analyzing until I say: DONE WITH ALL PARTS.
- I will label them like this: ...

"""
    first_part = True

    # Calculate total lines for estimating parts
    total_lines_all_files = sum(len(open(f, "r", encoding="utf-8", errors="ignore").readlines()) for f in file_list)
    total_parts_estimate = max(1, math.ceil(total_lines_all_files / max_lines))

    for file_index, file_path in enumerate(file_list, start=1):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        rel_path = os.path.relpath(file_path, os.getcwd())
        line_index = 0
        total_lines = len(lines)

        while line_index < total_lines:
            remaining_lines = total_lines - line_index
            available_space = max_lines - current_part_lines
            if remaining_lines <= available_space:
                chunk = "".join(lines[line_index:])
                line_index = total_lines
            else:
                chunk = "".join(lines[line_index:line_index + available_space])
                line_index += available_space

            if first_part:
                current_part_content += ai_instruction
                first_part = False

            current_part_content += f"# File: {rel_path}\n{chunk}\n"
            current_part_lines += len(chunk.splitlines())

            if current_part_lines >= max_lines:
                part_label = f"PART {part_counter} of {total_parts_estimate}"
                output_file = os.path.join(output_folder, f"{part_label.replace(' ', '_')}.txt")
                formatted = f"[{part_label}]\n{current_part_content}[END {part_label}]\n"
                with open(output_file, "w", encoding="utf-8") as out:
                    out.write(formatted)
                all_parts.append((output_file, part_label))
                part_counter += 1
                current_part_lines = 0
                current_part_content = ""

    if current_part_content.strip() != "":
        part_label = f"PART {part_counter} of {total_parts_estimate}"
        output_file = os.path.join(output_folder, f"{part_label.replace(' ', '_')}.txt")
        formatted = f"[{part_label}]\n{current_part_content}[END {part_label}]\n"
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(formatted)
        all_parts.append((output_file, part_label))

    all_parts_global = all_parts
    current_copy_index = 0

    for f_path, part_label in all_parts:
        btn = tk.Button(scrollable_frame, text=part_label,
                        command=lambda fp=f_path, pl=part_label: copy_to_clipboard(fp, pl),
                        bg="#f0f0f0")
        btn.pack(fill="x", padx=5, pady=2)

    messagebox.showinfo("Done", f"All files split successfully!\nSaved in {output_folder}")

def copy_next_part():
    global current_copy_index
    if not all_parts_global:
        messagebox.showerror("Error", "No parts generated yet!")
        return
    if current_copy_index >= len(all_parts_global):
        messagebox.showinfo("Info", "All parts have been copied. Starting over.")
        current_copy_index = 0
    file_path, part_label = all_parts_global[current_copy_index]
    copy_to_clipboard(file_path, part_label)
    current_copy_index += 1

# ---------- API Functions for OpenAI 1.x ----------

def load_api_key():
    if os.path.exists(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, "r") as f:
                data = json.load(f)
                api_key = data.get("api_key", "")
                txt_api_key.delete(0, tk.END)
                txt_api_key.insert(0, api_key)
                if api_key:
                    btn_upload_api.config(state="normal")
        except:
            pass

def save_api_key():
    key = txt_api_key.get().strip()
    with open(API_KEY_FILE, "w") as f:
        json.dump({"api_key": key}, f)
    if key:
        btn_upload_api.config(state="normal")
    else:
        btn_upload_api.config(state="disabled")
    messagebox.showinfo("API Key Saved", "API Key saved locally successfully!")

def upload_all_parts():
    api_key = txt_api_key.get().strip()
    if not api_key:
        messagebox.showerror("Error", "No API key entered!")
        return
    if not all_parts_global:
        messagebox.showerror("Error", "No parts to upload!")
        return

    openai.api_key = api_key
    for idx, (file_path, part_label) in enumerate(all_parts_global, start=1):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # safer choice
            messages=[{"role": "user", "content": content}]
            )
            lbl_api_status.config(text=f"Uploaded {part_label} ({idx}/{len(all_parts_global)})")
            root.update()
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload {part_label}: {e}")
            return
    messagebox.showinfo("Upload Complete", "All PARTs uploaded successfully!")

# ---------- GUI ----------

root = tk.Tk()
root.title("Project Code Splitter – ChatGPT/LM Arena Ready")
root.geometry("720x980")
root.configure(bg="#e8f0f8")

# Settings Frame
frame_top = tk.LabelFrame(root, text="Settings", padx=10, pady=10, bg="#e8f0f8")
frame_top.place(x=10, y=10, width=700, height=220)
tk.Label(frame_top, text="Target Platform:", bg="#e8f0f8").grid(row=0, column=0, sticky="w")
cmb_target = ttk.Combobox(frame_top, values=list(TARGET_LINE_DEFAULTS.keys()), state="readonly")
cmb_target.current(0)
cmb_target.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Max lines per PART:", bg="#e8f0f8").grid(row=1, column=0, sticky="w")
txt_max_lines = tk.Entry(frame_top)
txt_max_lines.grid(row=1, column=1, padx=5)

lbl_estimate = tk.Label(frame_top, text="", fg="blue", bg="#e8f0f8")
lbl_estimate.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

# API Key Frame
frame_api = tk.LabelFrame(frame_top, text="API Key (Optional for Auto Upload)", padx=5, pady=5, bg="#e8f0f8")
frame_api.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
txt_api_key = tk.Entry(frame_api, width=50, show="*")
txt_api_key.grid(row=0, column=0, padx=5)
btn_save_api = tk.Button(frame_api, text="Save API Key", command=save_api_key, bg="#d1e7dd")
btn_save_api.grid(row=0, column=1, padx=5)
btn_upload_api = tk.Button(frame_api, text="Upload All PARTs via API", command=upload_all_parts, bg="#cff4fc")
btn_upload_api.grid(row=1, column=0, columnspan=2, pady=5, sticky="we")
btn_upload_api.config(state="disabled")

lbl_api_status = tk.Label(frame_api, text="", fg="green", bg="#e8f0f8")
lbl_api_status.grid(row=2, column=0, columnspan=2, sticky="w")

# Load saved API key
load_api_key()

# File List Frame
frame_files = tk.LabelFrame(root, text="Selected Files", padx=5, pady=5, bg="#e8f0f8")
frame_files.place(x=10, y=240, width=700, height=180)
listbox_files = tk.Listbox(frame_files, bg="white")
listbox_files.pack(side="left", fill="both", expand=True)
scroll_files = ttk.Scrollbar(frame_files, orient="vertical", command=listbox_files.yview)
scroll_files.pack(side="right", fill="y")
listbox_files.config(yscrollcommand=scroll_files.set)

# Buttons Frame
frame_buttons = tk.LabelFrame(root, text="Actions", padx=5, pady=5, bg="#e8f0f8")
frame_buttons.place(x=10, y=430, width=700, height=100)
btn_add = tk.Button(frame_buttons, text="Add Files", command=add_files, bg="#d1e7dd")
btn_add.grid(row=0, column=0, padx=5, pady=5)
btn_add_folder = tk.Button(frame_buttons, text="Add Folder", command=add_folder, bg="#d1e7dd")
btn_add_folder.grid(row=0, column=1, padx=5, pady=5)
btn_clear = tk.Button(frame_buttons, text="Clear List", command=clear_files, bg="#f8d7da")
btn_clear.grid(row=0, column=2, padx=5, pady=5)
btn_start = tk.Button(frame_buttons, text="Start Split", command=split_files, bg="#cff4fc")
btn_start.grid(row=0, column=3, padx=5, pady=5)

# Copy feedback
lbl_copy_feedback = tk.Label(root, text="", fg="green", bg="#e8f0f8", anchor="w")
lbl_copy_feedback.place(x=10, y=540, width=700, height=20)

# Scrollable frame for PART buttons
frame_parts = tk.LabelFrame(root, text="Generated PARTs", padx=5, pady=5, bg="#e8f0f8")
frame_parts.place(x=10, y=570, width=700, height=220)
canvas = tk.Canvas(frame_parts, bg="white")
scrollbar = ttk.Scrollbar(frame_parts, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#ffffff")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Copy Next PART button at the bottom
btn_copy_next = tk.Button(root, text="Copy Next PART", command=copy_next_part, bg="#fff3cd")
btn_copy_next.place(x=10, y=800, width=700, height=50)

# Initialize default lines
cmb_target.bind("<<ComboboxSelected>>", lambda e: auto_set_safe_lines())
auto_set_safe_lines()

root.mainloop()
