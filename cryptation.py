import os
import random

letters = []
fileName = ""


def LoadFile(namefile):
    """Load plaintext from <namefile>.txt for encryption."""
    global fileName, letters
    fileName = namefile

    with open(fileName + ".txt", "r", encoding="utf-8") as file:
        letters = list(file.read())


def EncryptFile(key_directory=None):
    """Encrypt the file loaded with LoadFile and save its key separately."""
    global letters, fileName

    final_numbers = []
    key_pairs = []

    for letter in letters:
        int_letter = ord(letter)
        r1 = random.randint(1, 10_000_000)
        r2 = random.randint(1, 10_000_000)

        z = int_letter * r1 + r2
        final_numbers.append(str(z))
        key_pairs.append((r1, r2))

    encrypted_path = fileName + ".tsw"
    with open(encrypted_path, "w", encoding="utf-8") as file:
        file.write(" ".join(final_numbers))

    if key_directory is None:
        key_path = fileName + ".key"
    else:
        os.makedirs(key_directory, exist_ok=True)
        base_name = os.path.basename(fileName)
        key_path = os.path.join(key_directory, base_name + ".key")

    with open(key_path, "w", encoding="utf-8") as file:
        for r1, r2 in key_pairs:
            file.write(f"{r1} {r2}\n")

    plain_path = fileName + ".txt"
    if os.path.exists(plain_path):
        os.remove(plain_path)

    return encrypted_path, key_path


def Decryption(filename2, key_directory=None):
    """Decrypt data and RETURN plaintext without creating .txt or deleting files."""
    encrypted_path = filename2 + ".tsw"

    if key_directory is None:
        key_path = filename2 + ".key"
    else:
        base_name = os.path.basename(filename2)
        key_path = os.path.join(key_directory, base_name + ".key")

    with open(encrypted_path, "r", encoding="utf-8") as file:
        encrypted_numbers = file.read().split()

    with open(key_path, "r", encoding="utf-8") as file:
        key_lines = file.readlines()

    if len(encrypted_numbers) != len(key_lines):
        raise ValueError("Encrypted file and key do not contain the same number of entries.")

    decrypted_text = ""

    for i, encrypted_number in enumerate(encrypted_numbers):
        z = int(encrypted_number)
        r1, r2 = map(int, key_lines[i].split())
        int_letter = (z - r2) // r1
        decrypted_text += chr(int_letter)

    return decrypted_text
