import os
import json
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from config import load_config
from utils.helpers import load_json, get_employee_document_folder

config = load_config()
EMPLOYEE_FILE = os.path.join(config["data_directory"],"employees",  "employees.json")

def load_employees():
    if not os.path.exists(EMPLOYEE_FILE):
        return {}
    with open(EMPLOYEE_FILE, "r") as f:
        return json.load(f)

def open_file_folder(path):
    os.startfile(os.path.abspath(path))

def delete_document(path, refresh_func):
    if messagebox.askyesno("Confirm Delete", f"Delete file: {os.path.basename(path)}?"):
        try:
            os.remove(path)
            messagebox.showinfo("Deleted", f"{os.path.basename(path)} deleted.")
            refresh_func()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

def upload_document(emp_id, refresh_func):
    folder = get_employee_document_folder(emp_id)
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(folder, filename)
            with open(file_path, "rb") as fsrc, open(dest_path, "wb") as fdest:
                fdest.write(fsrc.read())
            messagebox.showinfo("Success", f"Document uploaded for {emp_id}")
            refresh_func()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def show_employee_documents(emp_id, container, refresh_func):
    for widget in container.winfo_children():
        widget.destroy()

    doc_folder = get_employee_document_folder(emp_id)
    files = os.listdir(doc_folder)

    if not files:
        Label(container, text="No documents uploaded yet.", bg="white", font=("Segoe UI", 11)).pack()
        return

    for file in files:
        file_path = os.path.join(doc_folder, file)
        frame = Frame(container, bg="#f0f0f0", pady=5, padx=5)
        frame.pack(fill=X, pady=4, padx=8)

        Label(frame, text=file, anchor="w", bg="#f0f0f0", font=("Segoe UI", 10)).pack(side=LEFT, fill=X, expand=True)
        Button(frame, text="Open", command=lambda p=file_path: os.startfile(p),
               bg="#007bff", fg="white", font=("Segoe UI", 9), width=8).pack(side=LEFT, padx=5)
        Button(frame, text="🗑 Delete", command=lambda p=file_path: delete_document(p, refresh_func),
               bg="#dc3545", fg="white", font=("Segoe UI", 9), width=8).pack(side=LEFT, padx=5)

def open_document_gui():
    win = Tk()
    win.title("📁 Employee Documents")
    win.geometry("650x550")
    win.configure(bg="white")

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 10))

    employees = load_employees()
    emp_ids = list(employees.keys())

    top_frame = Frame(win, bg="white", pady=10)
    top_frame.pack(fill=X)

    Label(top_frame, text="Select Employee:", bg="white", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=10)
    emp_var = StringVar()
    emp_dropdown = ttk.Combobox(top_frame, textvariable=emp_var, values=emp_ids, state="readonly", width=25)
    emp_dropdown.grid(row=0, column=1, padx=10)

    def refresh_docs():
        emp_id = emp_var.get()
        if emp_id:
            show_employee_documents(emp_id, doc_container, refresh_docs)

    Button(top_frame, text="📤 Upload", command=lambda: upload_document(emp_var.get(), refresh_docs),
           bg="#28a745", fg="white", font=("Segoe UI", 10), padx=10).grid(row=0, column=2, padx=10)
    Button(top_frame, text="📂 View", command=refresh_docs,
           bg="#007acc", fg="white", font=("Segoe UI", 10), padx=10).grid(row=0, column=3, padx=10)

    # Scrollable Frame for Documents
    canvas = Canvas(win, bg="white", highlightthickness=0)
    scrollbar = Scrollbar(win, orient=VERTICAL, command=canvas.yview)
    doc_container = Frame(canvas, bg="white")

    doc_container.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=doc_container, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
    scrollbar.pack(side=RIGHT, fill=Y)

    win.mainloop()

if __name__ == "__main__":
    open_document_gui()
