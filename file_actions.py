import os
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

# Клас, що виконує взаємодію з папками
class FileActions:
    def __init__(self, folder_path, previous_paths, next_paths):
        self.folder_path = folder_path
        self.previous_paths = previous_paths
        self.next_paths = next_paths

    # Отримує вміст каталогу для подальшого завантаження у таблицю
    def get_folder_contents(self):
        file_list = []
        files = os.scandir(self.folder_path)
        for entry in files:
            if entry.is_file():
                file = self.folder_path+"\\"+entry.name
                extension = os.path.splitext(entry.name)[1]
                mod_time = datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
                file_list.append((entry.name, entry.stat().st_size,
                                  f'Файл {extension}', mod_time))
            elif entry.is_dir():
                file = self.folder_path + "\\" + entry.name
                mod_time = datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
                file_list.append((entry.name, 0, 'Папка', mod_time))
        return tuple(file_list)

    # Заповнює таблицю файлів
    def load_folder(self, treeview):
        file_list = self.get_folder_contents()

        for file in file_list:
            treeview.insert('', 'end', values=file)

    # Записує тільки що відкритий каталог у рядок шляху
    def write_to_entry(self, entry):
        entry.delete(0, tk.END)
        entry.insert(0, os.path.abspath(self.folder_path))

    # Додає попередній каталог у список попередніх каталогів та очищує список наступних
    def add_to_prev(self):
        if not self.previous_paths or self.previous_paths[-1] != self.folder_path:
            self.previous_paths.append(self.folder_path)
            self.next_paths.clear()

    # Очищує таблицю файлів
    def clear_table(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

    # Оновлює таблицю файлів
    def refresh(self, treeview):
        self.clear_table(treeview)
        self.load_folder(treeview)

    # Отримує назви виділених у таблиці файлів
    def get_selection(self, treeview):
        selected_item = treeview.selection()
        item_selection = []
        for i in range(len(selected_item)):
            item_name = treeview.item(selected_item[i])['values'][0]
            item_selection.append(item_name)
        return item_selection

    # Перехід до вказаної у полі вводу папки
    def goto(self, entry, treeview):
        entered_path = entry.get()
        if os.path.isdir(entered_path):
            self.add_to_prev()
            self.folder_path = entered_path
            self.refresh(treeview)
        else:
            messagebox.showerror(title='Помилка', message='Введений шлях не існує.')
            self.write_to_entry(entry)
        return self.folder_path

    # Перехід на одну папку вгору
    def up_folder(self, entry, treeview):
        self.add_to_prev()
        path = self.folder_path.split('\\')
        if path[-1] == '':
            path.pop(-1)
        path.pop(-1)
        if len(path) == 1:
            path.append('\\')
        self.folder_path = "\\".join(path)
        self.write_to_entry(entry)
        self.refresh(treeview)
        return self.folder_path

    # Перехід у попередню папку
    def goto_previous(self, entry, treeview):
        if not self.previous_paths:
            return
        else:
            self.next_paths.append(self.folder_path)
            self.folder_path = self.previous_paths[-1]
            self.previous_paths.pop()
            self.write_to_entry(entry)
            self.refresh(treeview)
            return self.folder_path

    # Перехід у наступну папку
    def goto_next(self, entry, treeview):
        if not self.next_paths:
            return
        else:
            self.previous_paths.append(self.folder_path)
            self.folder_path = self.next_paths[-1]
            self.next_paths.pop()
            self.write_to_entry(entry)
            self.refresh(treeview)
            return self.folder_path

    # Сортувати таблицю файлів за значенням вказаного стовпця
    def sort_treeview(self, treeview, column, reverse):
        try:
            item_list = [(int(treeview.set(k, column)), k) for k in treeview.get_children('')]
        except Exception:
            item_list = [(treeview.set(k, column), k) for k in treeview.get_children('')]
        item_list.sort(reverse=reverse)
        for index, (_, k) in enumerate(item_list):
            treeview.move(k, '', index)
        treeview.heading(column, command=lambda: self.sort_treeview(treeview, column, not reverse))

    # Пошук предмета у таблиця за назвою
    def search_item(self, entry, treeview, column):
        self.refresh(treeview)
        searched = entry.get()
        for item in treeview.get_children(''):
            if searched not in treeview.set(item, column):
                treeview.delete(item)

    # Відкрити файл або папку
    def open(self, entry, treeview):
        selected_item = treeview.selection()
        if len(selected_item) != 1:
            messagebox.showerror(title='Помилка', message='Виберіть один файл або папку.')
            return
        item_name = treeview.item(selected_item[0])['values'][0]
        item_path = self.folder_path+'\\'+item_name
        # Якщо виділений елемент - папка, здійснюється перехід до вказаного каталогу
        if os.path.isdir(item_path):
            self.add_to_prev()
            self.folder_path = item_path
            self.write_to_entry(entry)
            self.refresh(treeview)
        # Якщо виділений елемент - файл, файл відкривається з допомогою стандартної програми
        else:
            try:
                os.startfile(item_path)
            except Exception as error:
                messagebox.showerror(title='Помилка', message=f'{error}')

    # Видаляє виділені у таблиці файли
    def delete_files(self, treeview):
        selection = self.get_selection(treeview)
        if messagebox.askyesno(title=f'Видалення {len(selection)} файлів',
                               message=f'Підтвердити видалення {len(selection)} файлів? '
                                       f'Після видалення дані файли повернути буде неможливо.'):
            while len(selection) != 0:
                file_name = selection[0]
                file = self.folder_path + '\\' + file_name
                try:
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                    else:
                        os.remove(file)
                    selection.pop(0)
                except Exception as error:
                    err_message = messagebox.Message(master=None,
                                                     icon=messagebox.ERROR,
                                                     title='Помилка',
                                                     message=f'Помилка при видаленні файлу "{file_name}":\n\n'
                                                             f'{error}\n\n'
                                                             f'Повторити спробу?',
                                                     type=messagebox.ABORTRETRYIGNORE).show()
                    if err_message == 'abort':
                        break
                    elif err_message == 'retry':
                        continue
                    else:
                        selection.pop(0)
            self.refresh(treeview)

    # Копіює виділені файли у каталог, вказаний у вікні
    def copy_files(self, treeview, destination, selection):
        while len(selection) != 0:
            file_name = selection[0]
            full_src = self.folder_path+'\\'+file_name
            full_dest = destination+'\\'+file_name
            try:
                if os.path.isdir(file_name):
                    if os.path.exists(full_dest):
                        if messagebox.askyesno(title='Помилка',
                                               message=f'Файл "{full_dest} вже існує. Замінити?"'):
                            os.remove(full_dest)
                            shutil.copytree(full_src, full_dest)
                        else:
                            continue
                    else:
                        shutil.copytree(full_src, full_dest)
                else:
                    if os.path.exists(full_dest):
                        if messagebox.askyesno(title='Помилка',
                                               message=f'Файл "{full_dest} вже існує. Замінити?"'):
                            os.remove(full_dest)
                            shutil.copy2(full_src, full_dest)
                        else:
                            continue
                    else:
                        shutil.copy2(full_src, full_dest)
                selection.pop(0)
            except Exception as error:
                err_message = messagebox.Message(master=None,
                                                 icon=messagebox.ERROR,
                                                 title='Помилка',
                                                 message=f'Помилка при копіюванні файлу "{file_name}":\n\n'
                                                         f'{error}\n\n'
                                                         f'Повторити спробу?',
                                                 type=messagebox.ABORTRETRYIGNORE).show()
                if err_message == 'abort':
                    break
                elif err_message == 'retry':
                    continue
                else:
                    selection.pop(0)
        self.refresh(treeview)

    # Вікно, де вказується шлях до каталогу, куди копіюються файли
    def copy_window(self, treeview):
        copy_window = tk.Tk()
        copy_window.title('Вікно копіювання')
        copy_window.geometry('400x200')
        copy_window.resizable(False, False)

        selection = self.get_selection(treeview)

        def copy_action():
            dest_path = dest_entry.get()
            if os.path.isdir(dest_path):
                self.copy_files(treeview, dest_path, selection)
            else:
                messagebox.showerror(title='Помилка', message='Вкажіть правильний шлях.')

        sel_number = ttk.Label(copy_window, text=f'Обрано файлів: {len(selection)}')
        sel_number.place(x=0, y=0)

        src_label = ttk.Label(copy_window, text='Початковий шлях:')
        src_label.place(x=0, y=40)

        src_entry = ttk.Entry(copy_window)
        src_entry.place(x=0, y=60, width=400, height=40)
        src_entry.insert(0, self.folder_path)
        src_entry.config(state=tk.DISABLED)

        dest_label = ttk.Label(copy_window, text='Кінцевий шлях:')
        dest_label.place(x=0, y=100)

        dest_entry = ttk.Entry(copy_window)
        dest_entry.place(x=0, y=120, width=400, height=40)

        copy_btn = ttk.Button(copy_window, text='Копіювати', command=copy_action)
        copy_btn.place(x=280, y=160, width=120, height=40)

        copy_window.mainloop()

    # Переміщає виділені файли до вказаного у вікні каталогу
    def move_files(self, treeview, destination, selection):

        while len(selection) != 0:
            file_name = selection[0]
            full_src = self.folder_path+'\\'+file_name
            full_dest = destination+'\\'+file_name
            try:
                if os.path.exists(full_dest):
                    if messagebox.askyesno(title='Помилка',
                                           message=f'Файл "{full_dest} вже існує. Замінити?"'):
                        os.remove(full_dest)
                        shutil.move(full_src, full_dest)
                    else:
                        continue
                else:
                    shutil.move(full_src, full_dest)
                selection.pop(0)
            except Exception as error:
                err_message = messagebox.Message(master=None,
                                                 icon=messagebox.ERROR,
                                                 title='Помилка',
                                                 message=f'Помилка при переміщенні файлу "{file_name}":\n\n'
                                                         f'{error}\n\n'
                                                         f'Повторити спробу?',
                                                 type=messagebox.ABORTRETRYIGNORE).show()
                if err_message == 'abort':
                    break
                elif err_message == 'retry':
                    continue
                else:
                    selection.pop(0)
        self.refresh(treeview)

    # Вікно, де вказується каталог, до якого переміщуютсья файли
    def move_window(self, treeview):
        move_window = tk.Tk()
        move_window.title('Вікно переміщення')
        move_window.geometry('400x200')
        move_window.resizable(False, False)

        selection = self.get_selection(treeview)

        def move_action():
            dest_path = dest_entry.get()
            if os.path.isdir(dest_path):
                self.move_files(treeview, dest_path, selection)
            else:
                messagebox.showerror(title='Помилка', message='Вкажіть правильний шлях.')

        sel_number = ttk.Label(move_window, text=f'Обрано файлів: {len(selection)}')
        sel_number.place(x=0, y=0)

        src_label = ttk.Label(move_window, text='Початковий шлях:')
        src_label.place(x=0, y=40)

        src_entry = ttk.Entry(move_window)
        src_entry.place(x=0, y=60, width=400, height=40)
        src_entry.insert(0, self.folder_path)
        src_entry.config(state=tk.DISABLED)

        dest_label = ttk.Label(move_window, text='Кінцевий шлях:')
        dest_label.place(x=0, y=100)

        dest_entry = ttk.Entry(move_window)
        dest_entry.place(x=0, y=120, width=400, height=40)

        move_btn = ttk.Button(move_window, text='Перемістити', command=move_action)
        move_btn.place(x=280, y=160, width=120, height=40)

        move_window.mainloop()

    # Створює файл у каталозі, вказаному у вікні
    def new_file(self, file_name):
        try:
            file = open(file_name, 'x')
            file.close()
        except Exception as error:
            messagebox.showerror(title='Помилка',
                                 message=f'Помилка при створенні файлу:\n\n{error}')

    # Вікно, де вказуєтьса каталог, де буде створено новий файл
    def new_file_window(self, treeview):
        new_file_window = tk.Tk()
        new_file_window.title('Вікно створення файлу')
        new_file_window.geometry('400x160')
        new_file_window.resizable(False, False)

        def new_file_action():
            path = path_entry.get()
            file_name = path+'\\'+file_name_entry.get()
            if os.path.isdir(path):
                self.new_file(file_name)
                self.refresh(treeview)
            else:
                messagebox.showerror(title='Помилка', message='Вкажіть правильний шлях.')

        path_label = ttk.Label(new_file_window, text='Шлях до файлу:')
        path_label.place(x=0, y=0)

        path_entry = ttk.Entry(new_file_window)
        path_entry.place(x=0, y=20, width=400, height=40)
        path_entry.insert(0, self.folder_path)

        file_name_label = ttk.Label(new_file_window, text='Назва файлу:')
        file_name_label.place(x=0, y=60)

        file_name_entry = ttk.Entry(new_file_window)
        file_name_entry.place(x=0, y=80, width=400, height=40)

        move_btn = ttk.Button(new_file_window, text='Створити', command=new_file_action)
        move_btn.place(x=280, y=120, width=120, height=40)

        new_file_window.mainloop()

    # Перейменовує файл
    def rename_file(self, old_name, new_name):
        try:
            os.rename(old_name, new_name)
        except Exception as error:
            messagebox.showerror(title='Помилка',
                                 message=f'Помилка при перейменуванні файлу:\n\n{error}')

    # Вікно, де вказується нова назва файлу
    def rename_window(self, treeview, old_name):
        rename_window = tk.Tk()
        rename_window.title('Вікно перейменування файлу')
        rename_window.geometry('400x100')
        rename_window.resizable(False, False)

        def rename_action():
            new_name = self.folder_path + '\\' + new_name_entry.get()
            self.rename_file(old_name, new_name)
            self.refresh(treeview)

        new_name_label = ttk.Label(rename_window, text='Введіть нову назву файлу:')
        new_name_label.place(x=0, y=0)

        new_name_entry = ttk.Entry(rename_window)
        new_name_entry.place(x=0, y=20, width=400, height=40)

        rename_btn = ttk.Button(rename_window, text='Перейменувати', command=rename_action)
        rename_btn.place(x=280, y=60, width=120, height=40)

        rename_window.mainloop()

    # Отримує виділений файл
    def rename(self, treeview):
        selected_item = treeview.selection()
        if len(selected_item) != 1:
            messagebox.showerror(title='Помилка', message='Виберіть один файл або папку.')
            return
        else:
            item_name = treeview.item(selected_item[0])['values'][0]
            item_path = self.folder_path + '\\' + item_name
            self.rename_window(treeview, item_path)