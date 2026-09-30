import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import Counter
from pathlib import Path
import re


# -------------------------
# File setup
# -------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


# -------------------------
# Default words to exclude
# -------------------------
STOP_WORDS = {
    "the", "and", "a", "an", "to", "of", "in", "on", "for", "at", "by", "from",
    "is", "it", "this", "that", "with", "as", "be", "are", "was", "were",
    "or", "not", "but", "if", "then", "so", "than", "too", "can", "will",
    "just", "also", "about", "into", "out", "up", "down", "over", "under",
}


# -------------------------
# Analyze text file
# -------------------------
def analyze_file(filepath):
    """Read a text file and return basic statistics and top words."""

    text = None

    # Try several common encodings
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            with open(filepath, "r", encoding=encoding) as file:
                text = file.read()
            break
        except (UnicodeDecodeError, OSError):
            continue

    if text is None:
        messagebox.showerror(
            "Error",
            "Could not read the selected text file."
        )
        return None

    # Get user-entered words to exclude
    user_exclude_raw = entry_exclude.get().strip()

    user_exclude = {
        word.strip().lower()
        for word in user_exclude_raw.split(",")
        if word.strip()
    }

    # Combine default and user-defined excluded words
    all_excluded = STOP_WORDS.union(user_exclude)

    # Find words and remove excluded words
    words = [
        word
        for word in re.findall(r"\b\w+\b", text.lower())
        if word not in all_excluded
    ]

    lines = len(text.splitlines())
    characters = len(text)

    # Get 10 most common words
    common_words = Counter(words).most_common(10)

    return {
        "lines": lines,
        "words": len(words),
        "characters": characters,
        "common": common_words
    }


# -------------------------
# Display analysis
# -------------------------
def analyze_and_display(filepath):
    """Analyze the selected file and update the GUI."""

    result = analyze_file(filepath)

    if not result:
        return

    last_file["path"] = filepath
    btn_reanalyze["state"] = "normal"

    lbl_file.config(
        text=f"File: {Path(filepath).name}"
    )

    lbl_lines_val.config(text=result["lines"])
    lbl_words_val.config(text=result["words"])
    lbl_chars_val.config(text=result["characters"])

    # Clear previous results
    lst_top.delete(0, tk.END)

    # Display top words
    for word, count in result["common"]:
        lst_top.insert(tk.END, f"{word} - {count}")


# -------------------------
# Select text file
# -------------------------
def choose_file():
    """Open a file dialog to select a text file."""

    filepath = filedialog.askopenfilename(
        title="Select Text File",
        filetypes=[("Text Files", "*.txt")]
    )

    if filepath:
        analyze_and_display(filepath)


# -------------------------
# Re-analyze file
# -------------------------
def reanalyze_file():
    """Re-analyze the last selected file."""

    if last_file["path"]:
        analyze_and_display(last_file["path"])
    else:
        messagebox.showinfo(
            "Info",
            "No file selected yet."
        )


# -------------------------
# Handle word double-click
# -------------------------
def on_word_click(event):
    """Add a selected top word to the exclude list."""

    selection = lst_top.curselection()

    if not selection:
        return

    word_line = lst_top.get(selection[0])
    word = word_line.rsplit("-", 1)[0].strip()

    current_words = {
        word.strip().lower()
        for word in entry_exclude.get().split(",")
        if word.strip()
    }

    if word.lower() not in current_words:
        if entry_exclude.get().strip():
            entry_exclude.insert(tk.END, f", {word}")
        else:
            entry_exclude.insert(0, word)


# -------------------------
# GUI Setup
# -------------------------
root = tk.Tk()
root.title("Text Analyzer")
root.geometry("700x700")
root.resizable(False, False)

frm_main = ttk.Frame(root, padding=15)
frm_main.pack(fill="both", expand=True)


# File selection
ttk.Button(
    frm_main,
    text="Select Text File",
    command=choose_file
).pack(pady=10)


# Store last analyzed file
last_file = {"path": None}


# Re-analyze button
btn_reanalyze = ttk.Button(
    frm_main,
    text="Re-analyze File",
    command=reanalyze_file
)
btn_reanalyze.pack(pady=(0, 10))
btn_reanalyze["state"] = "disabled"


# Selected file
lbl_file = ttk.Label(
    frm_main,
    text="No file selected",
    font=("Segoe UI", 10, "italic")
)
lbl_file.pack(pady=5)


# -------------------------
# Statistics
# -------------------------
frm_stats = ttk.Frame(frm_main)
frm_stats.pack(pady=10, fill="x")


def add_stat_row(name):
    """Create a statistics label."""

    ttk.Label(
        frm_stats,
        text=name + ":"
    ).pack(anchor="w")

    label = ttk.Label(
        frm_stats,
        text="0",
        font=("Segoe UI", 10, "bold")
    )
    label.pack(anchor="w", padx=10)

    return label


lbl_lines_val = add_stat_row("Lines")
lbl_words_val = add_stat_row("Words")
lbl_chars_val = add_stat_row("Characters")


# -------------------------
# Exclude words
# -------------------------
frm_exclude = ttk.Frame(frm_main)
frm_exclude.pack(pady=(10, 0), fill="x")

ttk.Label(
    frm_exclude,
    text="Exclude words (comma-separated):"
).pack(anchor="w")

entry_exclude = ttk.Entry(frm_exclude)
entry_exclude.pack(fill="x", padx=5)


# -------------------------
# Top words
# -------------------------
ttk.Label(
    frm_main,
    text="Top 10 Words:",
    font=("Segoe UI", 10, "bold")
).pack(pady=(10, 0))

lst_top = tk.Listbox(
    frm_main,
    height=15,
    width=30,
    justify="left"
)
lst_top.pack(pady=5)

lst_top.bind(
    "<Double-Button-1>",
    on_word_click
)


# -------------------------
# Exit button
# -------------------------
ttk.Button(
    frm_main,
    text="Exit",
    command=root.destroy
).pack(pady=10)


root.mainloop()