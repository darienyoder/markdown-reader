import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

page_width = 800

# Fixes page placement whenever the window resizes
def on_window_resize(event):
    global page_width
    page_width = min(800, event.width - 20)
    
    page_border.place(x =event.width/2 - page_width/2, y=0, width=page_width, height=event.height - 20)
    text_margin.place(x=1, y=1, width=page_width-2, height=event.height-21)
    text.place(x=100, y=50, width=page_width-200, height=event.height - 70)
    
# Prints as many underscores as will fit on a line to emulate a line break
def add_line_break():
    global page_width
    line = "_" * int((page_width - 200) / 6 - 1) + "\n"
    text.insert("end", line, "hr")
    text.insert("end", "\n")
    global line_number
    line_number += 2

# Adds a tag to the text in the given range
def set_tag(tag, line, start, end):
    text.tag_add(tag, str(line) + '.0 + ' + str(start) + " chars", str(line) + '.0 + ' + str(end) + " chars")

# Formats and prints a markdown file onto the page
def load_file(file):

    text.configure(state="normal")

    text.delete('1.0', "end")
    
    lines = file.readlines()
    global line_number
    line_number = 0
    is_paragraph = False
    paragraph_start = 0

    for read_line_number in range(len(lines)):

        line = lines[read_line_number]

        # Only print empty lines if the line before it was also empty
        if line == "\n":
            if not (read_line_number != len(lines) - 1 and lines[read_line_number + 1] == "\n"):
                line = ""
                
        tag = ""

        # Headers
        if line.startswith("# "):
            tag = "h1"
            line = line.replace("# ", "", 1)
        elif line.startswith("## "):
            tag = "h2"
            line = line.replace("## ", "", 1)
        elif line.startswith("### "):
            tag = "h3"
            line = line.replace("### ", "", 1)
        elif line.startswith("#### "):
            tag = "h4"
            line = line.replace("#### ", "", 1)
        elif line.startswith("##### "):
            tag = "h5"
            line = line.replace("##### ", "", 1)
        elif line.startswith("###### "):
            tag = "h6"
            line = line.replace("###### ", "", 1)

        # Line break
        elif line.startswith("---") or line.startswith("___") or line.startswith("***"):
            only_lines = True
            for char in range(len(line) - 2):
                if line[char] != line[0]:
                    only_lines = False
                    break
            if only_lines:
                add_line_break()
                line = ""

        # Unordered lists
        elif line.startswith("* ") or line.startswith("- "):
            tag = "list"
            line = "".join(("\t•  ", line[2:]))

        # Ordered lists
        is_ordered_list = False
        for char in range(len(line)):
            if line[char].isnumeric():
                continue
            elif line[char] == '.':
                if line[char + 1] != " ":
                    line = " ".join((line[0:char + 1], line[char + 1:]))
                line = "".join(("\t", line))
                tag = "list"
                break
            else:
                break

        # Paragraph tags can span multiple lines,
        # so the code records when the paragraph begins
        # and waits until it reaches the end to declare the tag
        if tag == "":
            if not is_paragraph:
                paragraph_start = line_number
                is_paragraph = True
        elif is_paragraph:
            text.tag_add("p", str(paragraph_start) + '.0', str(line_number + 1) + '.0')
            is_paragraph = False

        # Do not print if line is marked as empty
        if line != "":
            line.expandtabs(4)
            text.insert("end", line, tag)
            line_number += 1

        # Delete all formatting characters
        chars_to_delete = []
        tags = [""]
        open_index = [0]
        for char in range(len(line)):
            if line[char] in ['*', '_']:
                chars_to_delete.append(char)
                if tags[-1] == line[char]:
                    if char == open_index[-1] + 1:
                        if tags[-2] == "**":
                            set_tag('b', line_number, open_index[-2] + 1, char + 2)
                            open_index.pop(-2)
                            tags.pop(-2)
                        else:
                            tags.insert(-1, "**")
                            open_index.insert(-1, open_index[-1])
                    else:
                        set_tag('i', line_number, open_index[-1] + 1, char + 2)   
                    tags.pop()
                    open_index.pop()
                else:
                    tags.append(line[char])
                    open_index.append(char)
        chars_to_delete.reverse()
        for i in chars_to_delete:
            text.delete(str(line_number) + '.' + str(i))

        # Big headers get a line break for emphasis
        if tag in ["h1", "h2"]:
            add_line_break()

    text.configure(state="disabled")
            
# Prompt user to select a markdown document, and load if one is selected
def attempt_load():
    file = filedialog.askopenfile(mode='r', filetypes=(('Markdown Files', '*.md'), ('All Files', '*.*')))
    if file is not None:
        load_file(file)


# Initialize window
root = tk.Tk()
root.title("Markdown Reader")
root.geometry("1024x600")
root.configure(bg="#eeeeee")

# Button to load documents
load_button = ttk.Button(root, text="Load Document", command=attempt_load)
load_button.pack(pady=10)

# Container for page and scrollbar
text_frame = tk.Frame(root, background="blue")
text_frame.pack(fill = "both", expand = True)

# Fills all space not taken by the scrollbar
empty_margin = tk.Frame(text_frame, background="#eeeeee")
empty_margin.pack(fill = "both", side = "left", expand = True)
empty_margin.update()

# Border around page
page_border = tk.Frame(empty_margin, background="#909090")
page_border.place(x=0, y=0, width=800, height=0)

# White page including margins
text_margin = tk.Frame(page_border, background="white")
text_margin.pack(padx=1, pady=1)

# Area where text is printed
text = tk.Text(text_margin, font="Helvetica 12", tabs=48, border=0, wrap="word")
text.configure(state="disabled")
text.pack(fill="both", expand=True, padx=100, pady=50)

# Scrollbar next to page
scrollbar = ttk.Scrollbar(text_frame, orient='vertical')
text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text.yview)
scrollbar.pack(fill = "y", side = "right")

# Tag formatting
text.tag_configure('hr', font='Helvetica 8', foreground="gray")
text.tag_configure('h1', font="Helvetica 32", spacing3=0)
text.tag_configure('h2', font="Helvetica 24", spacing3=0)
text.tag_configure('h3', font='Helvetica 16', spacing3=8)
text.tag_configure('h4', font='Helvetica 14', spacing3=8)
text.tag_configure('h5', font='Helvetica 12', spacing3=8)
text.tag_configure('h6', font='Helvetica 8', spacing3=8)
text.tag_configure('i', font='Helvetica 12 italic')
text.tag_configure('b', font='Helvetica 12 bold')
text.tag_configure('list', font='Helvetica 12')
text.tag_configure('p', spacing3=8)

empty_margin.bind("<Configure>", on_window_resize)
root.mainloop()

