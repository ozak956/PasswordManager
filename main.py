import os
import re
import tkinter as tk
from tkinter import messagebox
import cryptation
import sys
import ctypes

attemptsFailed = 0
with open("data/attempts.tsw", "r", encoding="utf-8") as file:
        loadAttempts = file.readline()

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "ozak956.passwordmanager"
    )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD_DIR = os.path.join(BASE_DIR, "passwords", "pass")
KEY_DIR = os.path.join(BASE_DIR, "passwords", "keys")

os.makedirs(PASSWORD_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

window = tk.Tk()
window.title("Password Manager")
window.geometry("420x500")
icon = tk.PhotoImage(file="data/icon.png")
window.iconphoto(True, icon)


def account_stem(filename):
    """discord12.tsw -> discord12"""
    return os.path.splitext(filename)[0]


def app_from_stem(stem):
    """discord12 -> discord"""
    return re.sub(r"\d+$", "", stem)


def matching_accounts(app):
    """Return stems for app that have both .tsw and .key files."""
    result = []
    pattern = re.compile(rf"^{re.escape(app)}(\d+)$", re.IGNORECASE)

    for filename in os.listdir(PASSWORD_DIR):
        if not filename.endswith(".tsw"):
            continue

        stem = account_stem(filename)
        match = pattern.match(stem)
        if not match:
            continue

        key_path = os.path.join(KEY_DIR, stem + ".key")
        if os.path.exists(key_path):
            result.append((int(match.group(1)), stem))

    result.sort(key=lambda item: item[0])
    return [stem for _, stem in result]


def save_password(app, username, password):
    app = app.strip()
    username = username.strip()

    if not app or not username or not password:
        messagebox.showwarning("Missing data", "Fill in application, username and password.")
        return

    # Avoid path separators inside a filename.
    if any(char in app for char in '/\\'):
        messagebox.showerror("Invalid name", "Application name cannot contain / or \\.")
        return

    i = 1
    while True:
        stem = app + str(i)
        encrypted_path = os.path.join(PASSWORD_DIR, stem + ".tsw")
        key_path = os.path.join(KEY_DIR, stem + ".key")

        if not os.path.exists(encrypted_path) and not os.path.exists(key_path):
            break
        i += 1

    base_path = os.path.join(PASSWORD_DIR, stem)

    with open(base_path + ".txt", "x", encoding="utf-8") as file:
        file.write(username + "\n")
        file.write(password)

    try:
        cryptation.LoadFile(base_path)
        cryptation.EncryptFile(KEY_DIR)
        messagebox.showinfo("Saved", f"Password saved as {stem}.")
    except Exception as error:
        # Remove temporary plaintext if encryption failed.
        plain_path = base_path + ".txt"
        if os.path.exists(plain_path):
            os.remove(plain_path)
        messagebox.showerror("Error", str(error))


def edit_saved_password(stem, username, password):
    username = username.strip()

    if not stem:
        messagebox.showwarning("Select account", "Select an account to edit.")
        return False

    if not username or not password:
        messagebox.showwarning("Missing data", "Username and password cannot be empty.")
        return False

    base_path = os.path.join(PASSWORD_DIR, stem)
    plain_path = base_path + ".txt"

    try:
        # Create plaintext only for the short moment needed by the encryption function.
        with open(plain_path, "w", encoding="utf-8") as file:
            file.write(username + "\n")
            file.write(password)

        # EncryptFile writes over the existing .tsw and .key files,
        # so the account keeps exactly the same name/number.
        cryptation.LoadFile(base_path)
        cryptation.EncryptFile(KEY_DIR)

        messagebox.showinfo("Edited", f"Account {stem} was updated.")
        return True

    except Exception as error:
        if os.path.exists(plain_path):
            os.remove(plain_path)
        messagebox.showerror("Error", str(error))
        return False


def delete_saved_password(stem):
    if not stem:
        messagebox.showwarning("Select account", "Select an account to delete.")
        return False

    encrypted_path = os.path.join(PASSWORD_DIR, stem + ".tsw")
    key_path = os.path.join(KEY_DIR, stem + ".key")

    answer = messagebox.askyesno(
        "Delete account",
        f"Are you sure you want to delete {stem}?\nThis cannot be undone.",
    )

    if not answer:
        return False

    try:
        if os.path.exists(encrypted_path):
            os.remove(encrypted_path)

        if os.path.exists(key_path):
            os.remove(key_path)

        messagebox.showinfo("Deleted", f"Account {stem} was deleted.")
        return True

    except Exception as error:
        messagebox.showerror("Error", str(error))
        return False


def clear_window():
    for widget in window.winfo_children():
        widget.destroy()


def authors():
    clear_window()

    tk.Label(window, text="Authors", font=("Arial", 24)).pack(pady=30)
    tk.Label(window, text="Password Manager\nCreated by ozak956", font=("Arial", 12)).pack(pady=20)
    tk.Button(window, text="Back", command=about).pack(pady=20)


def main_menu():
    clear_window()

    tk.Label(window, text="Password Manager", font=("Arial", 25)).pack(pady=30)
    tk.Button(window, text="Add password", width=15, command=add_password).pack(pady=8)
    tk.Button(window, text="Show password", width=15, command=show_password).pack(pady=8)
    tk.Button(window, text="Delete password", width=15, command=delete_password).pack(pady=8)
    tk.Button(window, text="Edit password", width=15, command=edit_password).pack(pady=8)
    tk.Button(window, text="About", width=15, command=about).pack(pady=8)
    tk.Button(window, text="Logout", width=15, command=login).pack(pady=8)
    tk.Button(window, text="Exit", width=15, command=exit_app).pack(pady=40)


def add_password():
    clear_window()

    tk.Label(window, text="Add Password", font=("Arial", 24)).pack(pady=30)

    tk.Label(window, text="Application:").pack()
    app_entry = tk.Entry(window, width=30)
    app_entry.pack(pady=5)

    tk.Label(window, text="Username:").pack()
    username_entry = tk.Entry(window, width=30)
    username_entry.pack(pady=5)

    tk.Label(window, text="Password:").pack()
    password_entry = tk.Entry(window, width=30, show="*")
    password_entry.pack(pady=5)

    tk.Button(
        window,
        text="Save",
        command=lambda: save_password(app_entry.get(), username_entry.get(), password_entry.get()),
    ).pack(pady=15)

    tk.Button(window, text="Back", command=main_menu).pack()


def show_password():
    clear_window()

    tk.Label(window, text="Saved Passwords", font=("Arial", 24)).pack(pady=20)

    listbox = tk.Listbox(window, width=35, height=9)
    listbox.pack(pady=10)

    info_label = tk.Label(
        window,
        text="Select application",
        font=("Arial", 11),
        justify="left",
        anchor="w",
    )
    info_label.pack(pady=10)

    apps = set()

    for filename in os.listdir(PASSWORD_DIR):
        if not filename.endswith(".tsw"):
            continue

        stem = account_stem(filename)
        app_name = app_from_stem(stem)

        if not app_name:
            continue

        # Only show applications that have at least one matching key.
        if matching_accounts(app_name):
            apps.add(app_name)

    for app in sorted(apps, key=str.lower):
        listbox.insert(tk.END, app)

    def show_details(event=None):
        selected = listbox.curselection()
        if not selected:
            return

        app = listbox.get(selected[0])
        text = "Application: " + app + "\n\n"

        accounts = matching_accounts(app)
        if not accounts:
            info_label.config(text="No readable accounts found.")
            return

        for number, stem in enumerate(accounts, start=1):
            base_path = os.path.join(PASSWORD_DIR, stem)

            try:
                decrypted = cryptation.Decryption(base_path, KEY_DIR)
                lines = decrypted.splitlines()

                username = lines[0] if len(lines) >= 1 else ""
                password = lines[1] if len(lines) >= 2 else ""

                text += f"Account {number}\n"
                text += "Username: " + username + "\n"
                text += "Password: " + password + "\n\n"
            except Exception as error:
                text += f"{stem}: cannot decrypt ({error})\n\n"

        info_label.config(text=text)

    listbox.bind("<<ListboxSelect>>", show_details)

    tk.Button(window, text="Back", command=main_menu).pack(pady=20)


def edit_password():
    clear_window()

    tk.Label(window, text="Edit Password", font=("Arial", 24)).pack(pady=18)

    tk.Label(window, text="Select account:").pack()
    listbox = tk.Listbox(window, width=35, height=7)
    listbox.pack(pady=8)

    account_stems = []

    # Put every readable account on the list, e.g. Steam1, Steam2.
    for filename in os.listdir(PASSWORD_DIR):
        if not filename.endswith(".tsw"):
            continue

        stem = account_stem(filename)
        key_path = os.path.join(KEY_DIR, stem + ".key")
        if not os.path.exists(key_path):
            continue

        try:
            decrypted = cryptation.Decryption(os.path.join(PASSWORD_DIR, stem), KEY_DIR)
            lines = decrypted.splitlines()
            username = lines[0] if lines else ""
        except Exception:
            username = "cannot decrypt"

        account_stems.append(stem)
        listbox.insert(tk.END, f"{stem}   ({username})")

    tk.Label(window, text="Username:").pack()
    username_entry = tk.Entry(window, width=30)
    username_entry.pack(pady=4)

    tk.Label(window, text="Password:").pack()
    password_entry = tk.Entry(window, width=30, show="*")
    password_entry.pack(pady=4)

    selected_stem = {"value": None}

    def load_selected_account(event=None):
        selected = listbox.curselection()
        if not selected:
            return

        index = selected[0]
        stem = account_stems[index]
        selected_stem["value"] = stem

        try:
            decrypted = cryptation.Decryption(
                os.path.join(PASSWORD_DIR, stem),
                KEY_DIR,
            )
            lines = decrypted.splitlines()
            username = lines[0] if len(lines) >= 1 else ""
            password = lines[1] if len(lines) >= 2 else ""

            username_entry.delete(0, tk.END)
            username_entry.insert(0, username)

            password_entry.delete(0, tk.END)
            password_entry.insert(0, password)

        except Exception as error:
            messagebox.showerror("Error", f"Cannot decrypt {stem}:\n{error}")

    def save_changes():
        if edit_saved_password(
            selected_stem["value"],
            username_entry.get(),
            password_entry.get(),
        ):
            edit_password()

    listbox.bind("<<ListboxSelect>>", load_selected_account)

    tk.Button(window, text="Save changes", command=save_changes).pack(pady=10)
    tk.Button(window, text="Back", command=main_menu).pack(pady=4)

def delete_password():
    clear_window()

    tk.Label(window, text="Delete Password", font=("Arial", 24)).pack(pady=20)
    tk.Label(window, text="Select account to delete:").pack()

    listbox = tk.Listbox(window, width=35, height=9)
    listbox.pack(pady=10)

    account_stems = []

    for filename in sorted(os.listdir(PASSWORD_DIR), key=str.lower):
        if not filename.endswith(".tsw"):
            continue

        stem = account_stem(filename)
        key_path = os.path.join(KEY_DIR, stem + ".key")

        if not os.path.exists(key_path):
            continue

        try:
            decrypted = cryptation.Decryption(
                os.path.join(PASSWORD_DIR, stem),
                KEY_DIR,
            )
            lines = decrypted.splitlines()
            username = lines[0] if lines else ""
        except Exception:
            username = "cannot decrypt"

        account_stems.append(stem)
        listbox.insert(tk.END, f"{stem}   ({username})")

    selected_label = tk.Label(window, text="No account selected")
    selected_label.pack(pady=5)

    selected_stem = {"value": None}

    def select_account(event=None):
        selected = listbox.curselection()
        if not selected:
            return

        stem = account_stems[selected[0]]
        selected_stem["value"] = stem
        selected_label.config(text="Selected: " + stem)

    def delete_selected():
        if delete_saved_password(selected_stem["value"]):
            delete_password()

    listbox.bind("<<ListboxSelect>>", select_account)

    tk.Button(window, text="Delete selected", command=delete_selected).pack(pady=12)
    tk.Button(window, text="Back", command=main_menu).pack(pady=4)


def about():
    clear_window()

    tk.Label(window, text="About", font=("Arial", 24)).pack(pady=10)
    tk.Label(
        window,
        text="Password manager,\nencrypted with a proprietary script,\nkeys and passwords remain only\non your disk",
        font=("Arial", 12),
    ).pack(pady=70)

    tk.Button(window, text="Authors", command=authors).pack(pady=8)
    tk.Button(window, text="Back", command=main_menu).pack(pady=8)


def exit_app():
    window.destroy()
def login_check(passwrd):
    global attemptsFailed
    with open("data/pass.tsw", "r", encoding="utf-8") as file:
        passToCheck = file.readline()
    if passToCheck == passwrd:
        main_menu()
    else:
        attemptsFailed = attemptsFailed + 1
        if attemptsFailed > 10:
            attemptsFailed = 0
            messagebox.showinfo("To many attempts" , "to many attempts")
            exit_app()
        messagebox.showinfo("Password incorect" , "Incorect password")

def reset_password_check(old , new):
    print(old)
    print(new)
    with open("data/pass.tsw", "r", encoding="utf-8") as file:
        oldpassToCheck = file.readline()
    if oldpassToCheck == old:    
        with open("data/pass.tsw", "w", encoding="utf-8") as file:
            file.write(new)
            messagebox.showinfo("Password updated" , "Password has been changed")
    else:
        messagebox.showinfo("Password incorect" , "Incorect password")

def reset_password():
    clear_window()
    tk.Label(window, text="Reset password", font=("Arial", 25)).pack(pady=30)
    tk.Label(window, text="Old password:").pack()
    password_entry = tk.Entry(window, width=30, show="*")
    password_entry.pack(pady=5)
    tk.Label(window, text="New password:").pack()
    password_entry_new = tk.Entry(window, width=30, show="*")
    password_entry_new.pack(pady=5)

    tk.Button(
        window,
        text="Save",
        command=lambda: reset_password_check(password_entry.get(),password_entry_new.get()),
    ).pack(pady=15)

    tk.Button(
                window,
                text="Back",
                command=lambda: login(),
            ).pack(pady=15)
def info():
    clear_window()
    tk.Label(window, text="If you login first time \n click reset password and\n type password in \n NEW PASSWORD .", font=("Arial", 15)).pack(pady=30)
    tk.Button(
            window,
            text="Back",
            command=lambda: login(),
        ).pack(pady=8)
def login():
    clear_window()
    tk.Label(window, text="Password Manager", font=("Arial", 25)).pack(pady=30)
    tk.Label(window, text="Type password to login", font=("Arial", 20)).pack(pady=30)
    tk.Label(window, text="Password:").pack()
    password_entry = tk.Entry(window, width=30, show="*")
    password_entry.pack(pady=5)

    tk.Button(
        window,
        text="Login",
        command=lambda: login_check(password_entry.get()),
    ).pack(pady=8)
    tk.Button(
            window,
            text="Reset password",
            command=lambda: reset_password(),
        ).pack(pady=8)
    tk.Button(
            window,
            text="Info",
            command=lambda: info(),
        ).pack(pady=8)
    tk.Button(window, text="Exit", width=15, command=exit_app).pack(pady=8)
login()

window.mainloop()
