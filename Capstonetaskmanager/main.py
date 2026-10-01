from datetime import datetime

# Global Variables
user_file = "user.txt"
tasks_file = "tasks.txt"
users = {}
current_user = ""


# Load / Save Helpers
def load_users():
    global users
    users = {}

    try:
        with open(user_file, "r") as f:
            for line in f:
                if line.strip():
                    username, password = line.strip().split(", ")
                    users[username.lower()] = password
    except FileNotFoundError:
        pass


def save_user(username, password):
    try:
        with open(user_file, "a") as f:
            f.write(f"\n{username}, {password}")
    except FileNotFoundError:
        with open(user_file, "w") as f:
            f.write(f"{username}, {password}")

    users[username.lower()] = password


def load_tasks():
    tasks = []

    try:
        with open(tasks_file, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(", ")
                    if len(parts) == 6:
                        tasks.append({
                            "user": parts[0],
                            "title": parts[1],
                            "desc": parts[2],
                            "assigned": parts[3],
                            "due": parts[4],
                            "completed": parts[5]
                        })
    except FileNotFoundError:
        pass

    return tasks


def save_tasks(tasks):
    with open(tasks_file, "w") as f:
        for i, t in enumerate(tasks):
            if i != 0:
                f.write("\n")
            f.write(
                f"{t['user']}, {t['title']}, {t['desc']}, "
                f"{t['assigned']}, {t['due']}, {t['completed']}"
            )


# Utility
def print_tasks_table(tasks):
    headers = (
        f"{'#':<3} {'User':<10} {'Title':<15} "
        f"{'Description':<20} {'Assigned':<12} "
        f"{'Due':<12} {'Completed':<10} {'Overdue':<8}"
    )
    print(headers)
    print("-" * 95)

    for i, t in enumerate(tasks, 1):
        overdue = ""
        due_date = datetime.strptime(t['due'], "%Y-%m-%d")

        if t['completed'].lower() == "no":
            if due_date < datetime.today():
                overdue = "Yes"

        print(
            f"{i:<3} {t['user']:<10} {t['title']:<15} "
            f"{t['desc']:<20} {t['assigned']:<12} "
            f"{t['due']:<12} {t['completed']:<10} "
            f"{overdue:<8}"
        )

    print("-" * 95)


# Task Functions
def reg_user():
    if current_user != "admin":
        print("Only admin can register users.\n")
        return

    while True:
        new_username = input("Enter new username: ").lower()

        if new_username in users:
            print("Username exists.\n")
            continue

        new_password = input("Enter password: ")
        confirm = input("Confirm password: ")

        if new_password != confirm:
            print("Passwords do not match.\n")
            continue

        save_user(new_username, new_password)
        print("User registered successfully!\n")
        break


def add_task():
    assigned_user = input("Assign task to: ").lower()

    if assigned_user not in users:
        print("User does not exist.\n")
        return

    title = input("Task title: ")
    desc = input("Task description: ")
    due = input("Due date (YYYY-MM-DD): ")

    assigned = datetime.today().strftime("%Y-%m-%d")
    tasks = load_tasks()

    tasks.append({
        "user": assigned_user,
        "title": title,
        "desc": desc,
        "assigned": assigned,
        "due": due,
        "completed": "No"
    })

    save_tasks(tasks)
    print("Task added!\n")


def view_all():
    tasks = load_tasks()

    if not tasks:
        print("No tasks available.\n")
        return

    print_tasks_table(tasks)


def view_mine():
    tasks = load_tasks()

    user_indices = [
        i for i, t in enumerate(tasks)
        if t['user'].lower() == current_user
    ]

    if not user_indices:
        print("No tasks assigned to you.\n")
        return

    user_tasks = [tasks[i] for i in user_indices]
    print_tasks_table(user_tasks)

    choice = input(
        "Enter task number to edit/complete or -1 to return: "
    )

    if choice == "-1":
        return

    if not choice.isdigit():
        print("Invalid input.\n")
        return

    if not (1 <= int(choice) <= len(user_tasks)):
        print("Invalid input.\n")
        return

    real_index = user_indices[int(choice) - 1]
    task = tasks[real_index]

    if task['completed'].lower() == "yes":
        print("Task already completed.\n")
        return

    action = input("Mark complete (m) or edit (e)? ").lower()

    if action == "m":
        task['completed'] = "Yes"

    elif action == "e":
        new_user = input(
            "Change assigned user or press Enter to skip: "
        ).lower()

        if new_user and new_user in users:
            task['user'] = new_user

        new_due = input(
            "Change due date or press Enter to skip: "
        )

        if new_due:
            task['due'] = new_due

    tasks[real_index] = task
    save_tasks(tasks)

    print("Task updated!\n")


# Reports
def generate_reports():
    tasks = load_tasks()

    total_tasks = len(tasks)
    total_users = len(users)

    completed = sum(
        1 for t in tasks if t['completed'].lower() == "yes"
    )
    incomplete = total_tasks - completed

    overdue = 0
    for t in tasks:
        if t['completed'].lower() == "no":
            due = datetime.strptime(t['due'], "%Y-%m-%d")
            if due < datetime.today():
                overdue += 1

    with open("task_overview.txt", "w") as f:
        f.write(f"Total tasks: {total_tasks}\n")
        f.write(f"Completed tasks: {completed}\n")
        f.write(f"Incomplete tasks: {incomplete}\n")
        f.write(f"Overdue tasks: {overdue}\n")

    with open("user_overview.txt", "w") as f:
        f.write(f"Total users: {total_users}\n")
        f.write(f"Total tasks: {total_tasks}\n")

        for user in users:
            user_tasks = [
                t for t in tasks
                if t['user'].lower() == user.lower()
            ]

            num_tasks = len(user_tasks)

            completed_tasks = len([
                t for t in user_tasks
                if t['completed'].lower() == "yes"
            ])

            incomplete_tasks = len([
                t for t in user_tasks
                if t['completed'].lower() == "no"
            ])

            overdue_tasks = 0
            for t in user_tasks:
                if t['completed'].lower() == "no":
                    due = datetime.strptime(
                        t['due'], "%Y-%m-%d"
                    )
                    if due < datetime.today():
                        overdue_tasks += 1

            percent_total = (
                num_tasks / total_tasks * 100
            ) if total_tasks else 0

            percent_completed = (
                completed_tasks / num_tasks * 100
            ) if num_tasks else 0

            percent_incomplete = (
                incomplete_tasks / num_tasks * 100
            ) if num_tasks else 0

            percent_overdue = (
                overdue_tasks / num_tasks * 100
            ) if num_tasks else 0

            f.write(f"\nUser: {user}\n")
            f.write(f"Total tasks assigned: {num_tasks}\n")
            f.write(
                f"% of total tasks: "
                f"{percent_total:.2f}%\n"
            )
            f.write(
                f"% completed: "
                f"{percent_completed:.2f}%\n"
            )
            f.write(
                f"% incomplete: "
                f"{percent_incomplete:.2f}%\n"
            )
            f.write(
                f"% overdue: "
                f"{percent_overdue:.2f}%\n"
            )


def display_statistics():
    try:
        with open("task_overview.txt", "r") as f:
            print("\n--- Task Overview ---")
            print(f.read())
    except FileNotFoundError:
        print("Generating reports...")
        generate_reports()

    try:
        with open("user_overview.txt", "r") as f:
            print("\n--- User Overview ---")
            print(f.read())
    except FileNotFoundError:
        print("Generating reports...")
        generate_reports()


# Login
load_users()

while True:
    current_user = input("Username: ").lower()
    password = input("Password: ")

    if current_user not in users:
        print("Username not found\n")
    elif users[current_user] != password:
        print("Incorrect password\n")
    else:
        print(f"Welcome {current_user}\n")
        break


# Menu
while True:
    if current_user == "admin":
        menu = input("""
r   - register user
a   - add task
va  - view all tasks
vm  - view my tasks
ds  - display statistics
gr  - generate reports
e   - exit
: """).lower()
    else:
        menu = input("""
a  - add task
va - view all tasks
vm - view my tasks
e  - exit
: """).lower()

    if menu == "r":
        reg_user()
    elif menu == "a":
        add_task()
    elif menu == "va":
        view_all()
    elif menu == "vm":
        view_mine()
    elif menu == "gr":
        generate_reports()
    elif menu == "ds":
        display_statistics()
    elif menu == "e":
        print("Goodbye!")
        break
    else:
        print("Invalid option\n")