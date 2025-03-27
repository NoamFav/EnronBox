import os


def count_emails(maildir="maildir"):
    total = 0
    user_count = 0
    for user in os.listdir(maildir):
        user_path = os.path.join(maildir, user)
        if not os.path.isdir(user_path):
            continue
        user_count += 1

        for folder in os.listdir(user_path):
            folder_path = os.path.join(user_path, folder)
            if not os.path.isdir(folder_path):
                continue

            emails = [
                f
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
                and not f.startswith(".")
            ]
            total += len(emails)

    return user_count, total


users, emails = count_emails("maildir")
print(f"📁 Users: {users}")
print(f"✉️  Total emails: {emails}")
