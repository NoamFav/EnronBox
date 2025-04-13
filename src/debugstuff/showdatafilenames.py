import os

def show_real_filenames(maildir_path):
    for root, dirs, files in os.walk(maildir_path):
        for name in dirs + files:
            print(repr(name))

show_real_filenames(r"C:\Users\Admin\OneDrive\Documenten\univeriteit maastricht\all the branches\NLP_project\maildir")
