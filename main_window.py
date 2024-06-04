from file_actions import *
import os


# Клас головного вікна
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Файловий Менеджер ver. 0.1.0 alpha")
        self.geometry('960x540')
        self.resizable(False, False)

        # Теперішній шлях (за замовчуванням - шлях до програми)
        current_path = os.path.abspath('')
        # Список попередніх шляхів
        previous_paths = []
        # Список наступних шляхів
        next_paths = []

        # Таблиця файлів
        self.file_tree = ttk.Treeview(self, columns=('1', '2', '3', '4'), show='headings')
        self.file_tree.place(x=0, y=100, height=440, width=943)

        # Скролбар таблиці файлів
        self.file_tree_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.file_tree.yview)
        self.file_tree_scrollbar.place(x=943, y=100, height=440)
        self.file_tree.config(yscrollcommand=self.file_tree_scrollbar.set)

        # Вказання назв колонок та налаштування сортування за їх значеннями
        self.file_tree.heading('1', text="Ім'я",
                               command=lambda: fileactions.sort_treeview(self.file_tree, '1', False))
        self.file_tree.heading('2', text="Розмір",
                               command=lambda: fileactions.sort_treeview(self.file_tree, '2', False))
        self.file_tree.heading('3', text="Тип",
                               command=lambda: fileactions.sort_treeview(self.file_tree, '3', False))
        self.file_tree.heading('4', text="Дата змінення",
                               command=lambda: fileactions.sort_treeview(self.file_tree, '4', False))

        # Поле вводу шляху
        self.folder_entry = ttk.Entry(font=('Calibri', 12))
        self.folder_entry.place(x=200, y=0, height=50, width=710)

        # Поле пошуку
        self.search_entry = ttk.Entry(font=('Calibri', 12))
        self.search_entry.place(x=600, y=50, height=50, width=260)

        # Створення об'єкта класу FileActions
        fileactions = FileActions(current_path, previous_paths, next_paths)

        # Початкове завантаження таблиці
        fileactions.load_folder(self.file_tree)
        self.folder_entry.insert(0, os.path.abspath(current_path))

        # Метод переходу до вказаного шляху
        def goto():
            global current_path
            current_path = fileactions.goto(self.folder_entry, self.file_tree)

        # Метод переходу на каталог вгору
        def up_folder():
            global current_path
            current_path = fileactions.up_folder(self.folder_entry, self.file_tree)

        #Метод переходу в попередній каталог
        def goto_previous():
            global current_path
            current_path = fileactions.goto_previous(self.folder_entry, self.file_tree)

        # Метод переходу в наступний каталог
        def goto_next():
            global current_path
            current_path = fileactions.goto_next(self.folder_entry, self.file_tree)

        # Метод оновлення каталогу
        def refresh():
            fileactions.refresh(self.file_tree)

        # Метод пошуку файлів
        def search_item():
            fileactions.search_item(self.search_entry, self.file_tree, '1')

        # Метод відкривання файлу
        def open():
            fileactions.open(self.folder_entry, self.file_tree)

        # Метод видалення файлів
        def delete():
            fileactions.delete_files(self.file_tree)

        # Метод копіювання файлів
        def copy():
            fileactions.copy_window(self.file_tree)

        # Метод переміщення файлів
        def move():
            fileactions.move_window(self.file_tree)

        # Метод створення файлу
        def new():
            fileactions.new_file_window(self.file_tree)

        # Метод перейменування файлу
        def rename():
            fileactions.rename(self.file_tree)

        # Кнопка "Назад"
        self.back_btn = ttk.Button(text='<', command=goto_previous)
        self.back_btn.place(x=0, y=0, height=50, width=50)

        # Кнопка "Вперед"
        self.forward_btn = ttk.Button(text='>', command=goto_next)
        self.forward_btn.place(x=50, y=0, height=50, width=50)

        # Кнопка "Вгору"
        self.up_btn = ttk.Button(text='^', command=up_folder)
        self.up_btn.place(x=100, y=0, height=50, width=50)

        # Кнопка "Оновити"
        self.refresh_btn = ttk.Button(text='⟳', command=refresh)
        self.refresh_btn.place(x=150, y=0, height=50, width=50)

        # Кнопка "Перейти до"
        self.goto_btn = ttk.Button(text='->', command=goto)
        self.goto_btn.place(x=910, y=0, height=50, width=50)

        # Кнопка "Відкрити"
        self.openfile_btn = ttk.Button(text='Відкрити', command=open)
        self.openfile_btn.place(x=0, y=50, height=50, width=100)

        # Кнопка "Створити"
        self.newfile_btn = ttk.Button(text='Створити', command=new)
        self.newfile_btn.place(x=100, y=50, height=50, width=100)

        # Кнопка "Копіювати"
        self.copyfile_btn = ttk.Button(text='Копіювати', command=copy)
        self.copyfile_btn.place(x=200, y=50, height=50, width=100)

        # Кнопка "Перемістити"
        self.movefile_btn = ttk.Button(text='Перемістити', command=move)
        self.movefile_btn.place(x=300, y=50, height=50, width=100)

        # Кнопка "Перейменувати"
        self.rename_btn = ttk.Button(text='Перейменувати', command=rename)
        self.rename_btn.place(x=400, y=50, height=50, width=100)

        # Кнопка "Видалити"
        self.delfile_btn = ttk.Button(text='Видалити', command=delete)
        self.delfile_btn.place(x=500, y=50, height=50, width=100)

        # Кнопка "Пошук"
        self.search_btn = ttk.Button(text='Пошук', command=search_item)
        self.search_btn.place(x=860, y=50, height=50, width=100)


# Виклик головного вікна
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
