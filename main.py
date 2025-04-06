import re
from collections import UserDict
from datetime import datetime, timedelta
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Якщо файл не існує, повертаємо порожню книгу

# ======= Базові класи =======

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.match(r"^\d{10}$", value):
            raise ValueError("Phone must be exactly 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(self.date.strftime("%d.%m.%Y"))
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# ======= Клас Record =======

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Phone {old_phone} not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

# ======= Клас AddressBook =======

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact with name {name} not found")

    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                bday_this_year = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=today.year)
                delta_days = (bday_this_year - today).days
                if 0 <= delta_days < 7:
                    day_name = (today + timedelta(days=delta_days)).strftime("%A")
                    upcoming.append(f"{record.name.value} - {record.birthday.value} ({day_name})")

        return upcoming

# ======= Хелпери =======

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Please provide all necessary details."
        except KeyError:
            return "Contact not found."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.lower(), args

# ======= Команди =======

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone updated."
    return "Contact not found."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {', '.join(p.value for p in record.phones)}"
    return "Contact not found."

@input_error
def show_all(args, book):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added to {name}"
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday}"
    return "Birthday not found for this contact."

@input_error
def birthdays(args, book):
    result = book.get_upcoming_birthdays()
    if not result:
        return "No birthdays in the next 7 days."
    return "\n".join(result)

# ======= Основна функція main() =======

def main():
    book = load_data()  # Завантаження адресної книги при запуску
    print("Welcome to the assistant bot!")

    while True:
        user_input = input(">>> ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            save_data(book)  # Збереження книги перед виходом
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
