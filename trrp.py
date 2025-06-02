import tkinter as tk
from tkinter import ttk, messagebox
from pynput import mouse, keyboard

# ==================== Настройка главного окна ====================
window = tk.Tk()
window.title("Global Mouse Counter + Visual Keyboard")
window.resizable(False, False)

# ==================== Переменные для счётчика мыши ====================
click_count     = tk.IntVar(value=0)      # текущее значение счётчика кликов
click_increment = tk.IntVar(value=1)      # шаг прибавления/вычитания
global_mode     = tk.BooleanVar(value=False)  # флаг «глобального режима» мыши

mouse_listener    = None  # объект pynput-слушателя мыши
keyboard_listener = None  # объект pynput-слушателя клавиатуры

# ==================== Функции-обработчики для мышиного счётчика ====================
def handle_click():
    """Добавляет click_increment к click_count и обновляет метку."""
    click_count.set(click_count.get() + click_increment.get())
    update_mouse_label()

def handle_increment():
    """
    Увеличивает click_increment на 1, «тратя» 1 клик из click_count.
    Если кликов не хватает, показывает предупреждение и сбрасывает оба значения.
    """
    if click_count.get() >= 1:
        click_count.set(click_count.get() - 1)
        click_increment.set(click_increment.get() + 1)
        update_mouse_label()
    else:
        messagebox.showwarning(
            "Not enough clicks",
            "Нужно хотя бы 1 клик, чтобы увеличить шаг."
        )
        click_increment.set(1)
        click_count.set(0)
        update_mouse_label()

def handle_decrement():
    """
    Уменьшает click_count на текущее click_increment (если хватает).
    Иначе — предупреждение.
    """
    if click_count.get() >= click_increment.get():
        click_count.set(click_count.get() - click_increment.get())
        update_mouse_label()
    else:
        messagebox.showwarning(
            "Not enough clicks",
            "Нельзя уменьшить: недостаточно кликов."
        )

def update_mouse_label():
    """Обновляет метку с большим числом кликов."""
    mouse_count_label.config(text=str(click_count.get()))

# ==================== Функции для глобального слушателя мыши ====================
def on_global_mouse_click(x, y, button, pressed):
    """
    Колбэк pynput для мыши: если это нажатие ЛКМ — через after вызываем handle_click() в главном потоке.
    """
    if pressed and button == mouse.Button.left:
        window.after(0, handle_click)

def start_global_mouse_listener():
    """Запускает слушатель pynput.mouse."""
    global mouse_listener
    if mouse_listener is None:
        mouse_listener = mouse.Listener(on_click=on_global_mouse_click)
        mouse_listener.start()

def stop_global_mouse_listener():
    """Останавливает слушатель мыши, если он запущен."""
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None

def toggle_global_mouse_mode():
    """
    Включаем или выключаем «глобальный режим» мыши по флагу global_mode.
    """
    if global_mode.get():
        try:
            start_global_mouse_listener()
        except Exception as e:
            messagebox.showerror("Error", f"Не удалось запустить слушатель мыши:\n{e}")
            global_mode.set(False)
    else:
        stop_global_mouse_listener()

# ==================== Словари соответствия для map_key_to_name ====================
PUNCT_MAPPING = {
    '`': 'grave',
    '-': 'minus',
    '=': 'equal',
    '[': 'left_bracket',
    ']': 'right_bracket',
    '\\': 'backslash',
    ';': 'semicolon',
    '\'': 'apostrophe',
    ',': 'comma',
    '.': 'period',
    '/': 'slash',
}
SHIFT_MAPPING = {
    '!': '1',    '@': '2',  '#': '3',  '$': '4',  '%': '5',
    '^': '6',    '&': '7',  '*': '8',  '(': '9',  ')': '0',
    '_': 'minus','+': 'equal',
    '{': 'left_bracket', '}': 'right_bracket',
    '|': 'backslash',
    ':': 'semicolon', '"': 'apostrophe',
    '<': 'comma', '>': 'period', '?': 'slash',
    '~': 'grave'
}

# ==================== Подготовка визуальной клавиатуры ====================
keyboard_rows = [
    # Row 1
    [
        ('esc',       'Esc',       4),
        ('grave',     '`',         4),
        ('1',         '1',         4),  ('2', '2', 4),  ('3','3',4),
        ('4','4',4),  ('5','5',4),  ('6','6',4),  ('7','7',4),
        ('8','8',4),  ('9','9',4),  ('0','0',4),
        ('minus','-', 4),  ('equal','=', 4),
        ('backspace','Bksp',8)
    ],
    # Row 2
    [
        ('tab',    'Tab',      6),
        ('q','Q',   4),  ('w','W',4), ('e','E',4), ('r','R',4),
        ('t','T',4), ('y','Y',4), ('u','U',4), ('i','I',4),
        ('o','O',4), ('p','P',4),
        ('left_bracket','[',4), ('right_bracket',']',4),
        ('backslash','\\',6)
    ],
    # Row 3
    [
        ('caps_lock','Caps', 6),
        ('a','A',4), ('s','S',4), ('d','D',4), ('f','F',4),
        ('g','G',4), ('h','H',4), ('j','J',4), ('k','K',4),
        ('l','L',4),
        ('semicolon',';',4), ('apostrophe','\'',4),
        ('enter','Enter',8)
    ],
    # Row 4
    [
        ('shift_l','Shift',8),
        ('z','Z',4), ('x','X',4), ('c','C',4), ('v','V',4),
        ('b','B',4), ('n','N',4), ('m','M',4),
        ('comma',',',4), ('period','.',4), ('slash','/',4),
        ('shift_r','Shift',8)
    ],
    # Row 5
    [
        ('ctrl_l','Ctrl',6),
        ('alt_l','Alt',4),
        ('space','Space',30),
        ('alt_r','Alt',4),
        ('ctrl_r','Ctrl',6)
    ],
]

# Словарь: key_name → Label-виджет
key_widgets = {}
# Стандартный фон клавиш, чтобы вернуть при отпускании
default_key_bg = None

def build_keyboard_visual(parent_frame):
    """
    Строит визуальную клавиатуру внутри parent_frame.
    Заполняет key_widgets и сохраняет default_key_bg.
    """
    global default_key_bg

    for row_index, row_keys in enumerate(keyboard_rows):
        col = 0
        for key_name, display_text, width_chars in row_keys:
            lbl = tk.Label(
                parent_frame,
                text=display_text,
                width=width_chars,
                height=2,
                relief='raised',
                borderwidth=2,
                bg='white',
                fg='black',
                font=('Arial', 10, 'bold')
            )
            lbl.grid(row=row_index, column=col, padx=2, pady=2)
            key_widgets[key_name] = lbl

            if default_key_bg is None:
                default_key_bg = lbl.cget('bg')

            col += 1

def map_key_to_name(key):
    """
    Преобразует объект pynput.key (Key или KeyCode) в строковое «имя» клавиши,
    соответствующее тому, как мы её назвали в key_widgets.
    """
    try:
        ch = key.char
    except AttributeError:
        ch = None

    if ch is not None:
        if ch == ' ':
            return 'space'
        if ch in SHIFT_MAPPING:
            return SHIFT_MAPPING[ch]
        if ch in PUNCT_MAPPING:
            return PUNCT_MAPPING[ch]
        if ch.isalpha() or ch.isdigit():
            return ch.lower()
        return None

    try:
        name = key.name
    except AttributeError:
        return None

    if name in ('enter', 'return'):
        return 'enter'
    if name == 'backspace':
        return 'backspace'
    if name == 'tab':
        return 'tab'
    if name == 'caps_lock':
        return 'caps_lock'
    if name in ('shift', 'shift_l', 'shift_r'):
        if name == 'shift_l':
            return 'shift_l'
        if name == 'shift_r':
            return 'shift_r'
        return 'shift_l'
    if name in ('ctrl_l', 'ctrl_r'):
        return name
    if name in ('alt_l', 'alt_r'):
        return name
    if name == 'esc':
        return 'esc'
    if name == 'space':
        return 'space'
    if name in ('left_bracket','right_bracket','backslash',
                'semicolon','apostrophe','comma','period','slash'):
        return name
    if name in ('minus','equal','grave'):
        return name
    return None

def on_global_key_press(key):
    """
    Колбэк pynput для нажатия клавиши.
    Подсвечиваем соответствующий Label клавиатуры.
    """
    key_name = map_key_to_name(key)
    if key_name and key_name in key_widgets:
        window.after(0, lambda: key_widgets[key_name].config(bg='yellow'))

def on_global_key_release(key):
    """
    Колбэк pynput для отпускания клавиши.
    Возвращаем фон Label к default_key_bg.
    """
    key_name = map_key_to_name(key)
    if key_name and key_name in key_widgets:
        window.after(0, lambda: key_widgets[key_name].config(bg=default_key_bg))

def start_global_keyboard_listener():
    """Запускает pynput.keyboard.Listener с колбэками нажатия и отпускания."""
    global keyboard_listener
    if keyboard_listener is None:
        keyboard_listener = keyboard.Listener(
            on_press=on_global_key_press,
            on_release=on_global_key_release
        )
        keyboard_listener.start()

def stop_global_keyboard_listener():
    """Останавливает слушатель клавиатуры, если он запущен."""
    global keyboard_listener
    if keyboard_listener is not None:
        keyboard_listener.stop()
        keyboard_listener = None

# ==================== Обработчик закрытия окна ====================
def on_closing():
    """
    При закрытии — останавливаем оба слушателя и выходим,
    иначе фоновые потоки pynput не завершатся корректно.
    """
    stop_global_mouse_listener()
    stop_global_keyboard_listener()
    window.destroy()

# ==================== Сборка UI ====================

# --- Frame для мышиного счётчика ---
mouse_frame = ttk.LabelFrame(window, text="Mouse Counter", padding=10)
mouse_frame.pack(fill="x", padx=10, pady=(10, 5))

click_button = ttk.Button(mouse_frame, text="Click Me", command=handle_click)
click_button.grid(row=0, column=0, padx=5, pady=5)

decrement_button = ttk.Button(mouse_frame, text="Decrease", command=handle_decrement)
decrement_button.grid(row=0, column=1, padx=5, pady=5)

increment_button = ttk.Button(mouse_frame, text="Increase Increment", command=handle_increment)
increment_button.grid(row=0, column=2, padx=5, pady=5)

global_check = ttk.Checkbutton(
    mouse_frame,
    text="Global Mouse Mode",
    variable=global_mode,
    command=toggle_global_mouse_mode
)
global_check.grid(row=1, column=0, columnspan=3, pady=5)

mouse_count_label = ttk.Label(
    mouse_frame,
    text="0",
    font=("Arial", 36, "bold"),
    anchor="center"
)
mouse_count_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))

# --- Frame для визуальной клавиатуры ---
keyboard_frame = ttk.LabelFrame(window, text="Visual Keyboard (Press any key)", padding=10)
keyboard_frame.pack(fill="x", padx=10, pady=(5, 10))

build_keyboard_visual(keyboard_frame)

# ==================== Запуск слушателей и главное окно ====================
start_global_keyboard_listener()
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
