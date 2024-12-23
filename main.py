from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk

class Paint(object):
    DEFAULT_COLOR = 'black'
    DEFAULT_LINE_WIDTH = 5

    def __init__(self):
        self.root = Tk()
        self.root.title("Paint")

        self.create_menu()

        self.line_width = self.DEFAULT_LINE_WIDTH
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.old_x = None
        self.old_y = None
        self.drawing_shape = None
        self.start_x = None
        self.start_y = None
        self.current_shape_id = None

        self.recent_colors = []
        self.history = []  # Хранение истории действий
        self.redo_stack = []  # Хранение для повтора

        self.tool_panel = Frame(self.root)
        self.tool_panel.pack(side=TOP, fill=X)

        self.create_tool_buttons()

        self.c = Canvas(self.root, bg='white', width=800, height=800)
        self.c.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

        self.image = Image.new("RGB", (800, 800), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.c.bind('<ButtonPress-1>', self.start_shape)
        self.c.bind('<Button-3>', self.bucket_fill)  # Правый клик для заливки

        # Обработчики клавиатуры
        self.root.bind('<Control-z>', self.undo)
        self.root.bind('<Control-y>', self.redo)

        self.root.mainloop()

    def create_menu(self):
        menubar = Menu(self.root)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Load", command=self.load_image)
        file_menu.add_command(label="Clear", command=self.clear_canvas)
        menubar.add_cascade(label="File", menu=file_menu)

        shapes_menu = Menu(menubar, tearoff=0)
        shapes_menu.add_command(label="Квадрат", command=self.select_square)
        shapes_menu.add_command(label="Круг", command=self.select_circle)
        shapes_menu.add_command(label="Прямая сплошная", command=self.select_line)
        shapes_menu.add_command(label="Прямая пунктиром", command=self.select_dashed_line)
        menubar.add_cascade(label="Shapes", menu=shapes_menu)

        self.root.config(menu=menubar)

    def create_tool_buttons(self):
        pen_button = Button(self.tool_panel, text="Ручка", command=self.use_pen)
        pen_button.pack(side=LEFT, padx=5, pady=5)

        eraser_button = Button(self.tool_panel, text="Ластик", command=self.use_eraser)
        eraser_button.pack(side=LEFT, padx=5, pady=5)

        fill_button = Button(self.tool_panel, text="Заливка", command=self.use_bucket_fill)
        fill_button.pack(side=LEFT, padx=5, pady=5)

        undo_button = Button(self.tool_panel, text="Назад", command=self.undo)
        undo_button.pack(side=LEFT, padx=5, pady=5)

        redo_button = Button(self.tool_panel, text="Вперед", command=self.redo)
        redo_button.pack(side=LEFT, padx=5, pady=5)

        self.line_width_scale = Scale(self.tool_panel, from_=1, to=10, orient=HORIZONTAL, label="Толщина линии")
        self.line_width_scale.set(self.line_width)
        self.line_width_scale.pack(side=LEFT, padx=10, pady=5)

        color_button = Button(self.tool_panel, text="Выбор цвета", command=self.choose_color)
        color_button.pack(side=LEFT, padx=5, pady=5)

        self.color_display = Label(self.tool_panel, bg=self.color, width=10, height=2)
        self.color_display.pack(side=LEFT, padx=10, pady=5)

        self.color_frame = Frame(self.tool_panel)
        self.color_frame.pack(side=LEFT, padx=5, pady=5)

        Label(self.color_frame, text="Последние цвета:").pack()

        self.color_buttons = []
        for _ in range(5):
            btn = Button(self.color_frame, bg='white', command=lambda c=None: self.set_color(c), width=2, height=1)
            btn.pack(side=LEFT, padx=1, pady=1)
            self.color_buttons.append(btn)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                   filetypes=[("PNG files", "*.png"),
                                                              ("JPEG files", "*.jpg"),
                                                              ("All files", "*.*")])
        if file_path:
            self.image.save(file_path)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"),
                                                           ("JPEG files", "*.jpg"),
                                                           ("All files", "*.*")])
        if file_path:
            loaded_image = Image.open(file_path).convert("RGB")
            self.image.paste(loaded_image)
            self.update_canvas()

    def clear_canvas(self):
        self.c.delete("all")
        self.image = Image.new("RGB", (800, 800), "white")
        self.draw = ImageDraw.Draw(self.image)

    def undo(self, event=None):
        if self.history:
            last_action = self.history.pop()
            self.redo_stack.append(self.image.copy())  # Сохраняем текущее состояние в redo_stack
            self.image = last_action  # Восстанавливаем предыдущее состояние
            self.update_canvas()

    def redo(self, event=None):
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.history.append(self.image.copy())  # Сохраняем текущее состояние в history
            self.image = action  # Восстанавливаем состояние
            self.update_canvas()

    def update_canvas(self):
        self.c.delete("all")
        # Создаем изображение для отображения
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.c.create_image(0, 0, anchor=NW, image=self.tk_image)

    def use_bucket_fill(self):
        self.drawing_shape = 'bucket_fill'  # Устанавливаем режим заливки

    def choose_color(self):
        color = askcolor(color=self.color)[1]
        if color:
            self.color = color
            self.add_recent_color(color)
            self.update_color_display()

    def update_color_display(self):
        self.color_display.config(bg=self.color)

    def change_line_width(self, value):
        self.line_width = int(value)

    def select_square(self):
        self.drawing_shape = 'square'
        self.eraser_on = False

    def select_circle(self):
        self.drawing_shape = 'circle'
        self.eraser_on = False

    def select_line(self):
        self.drawing_shape = 'line'
        self.eraser_on = False

    def select_dashed_line(self):
        self.drawing_shape = 'dashed_line'
        self.eraser_on = False

    def use_pen(self):
        self.eraser_on = False
        self.drawing_shape = None

    def bucket_fill(self, event):
        x, y = event.x, event.y
        target_color = self.image.getpixel((x, y))  # Получаем цвет пикселя
        target_color_hex = '#{:02x}{:02x}{:02x}'.format(*target_color)  # Преобразуем в hex
        if target_color_hex == self.color:
            return  # Если цвет уже тот же, ничего не делаем

        # Сохраняем текущее состояние перед заливкой
        self.history.append(self.image.copy())
        self.redo_stack.clear()  # Очищаем стек повтора

        self._flood_fill(x, y, target_color, self.hex_to_rgb(self.color))
        self.update_canvas()

    def _flood_fill(self, x, y, target_color, replacement_color):
        stack = [(x, y)]

        while stack:
            x, y = stack.pop()

            if x < 0 or x >= self.image.width or y < 0 or y >= self.image.height:
                continue
            if self.image.getpixel((x, y)) != target_color:
                continue
            if self.image.getpixel((x, y)) == replacement_color:
                continue

            self.image.putpixel((x, y), replacement_color)

            # Добавляем соседние пиксели в стек
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

    def hex_to_rgb(self, color):
        """Преобразует цвет в формате hex или название цвета в кортеж RGB."""
        if color.startswith('#'):
            hex_color = color[1:]  # Удаляем символ '#'
        else:
            # Преобразуем название цвета в RGB
            hex_color = f"{self.root.winfo_rgb(color)[0] >> 8:02x}{self.root.winfo_rgb(color)[1] >> 8:02x}{self.root.winfo_rgb(color)[2] >> 8:02x}"

        if len(hex_color) != 6:  # Проверяем длину
            raise ValueError(f"Неверный формат цвета: {color}")
        
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def set_color(self, color):
        if color:
            self.color = color
            self.update_color_display()

    def add_recent_color(self, color):
        if color and color not in self.recent_colors:
            self.recent_colors.append(color)
            if len(self.recent_colors) > 5:
                self.recent_colors.pop(0)
            self.update_color_buttons()

    def update_color_buttons(self):
        for btn, color in zip(self.color_buttons, self.recent_colors):
            btn.config(bg=color)
            btn.config(command=lambda c=color: self.set_color(c))

    def use_eraser(self):
        self.eraser_on = True
        self.drawing_shape = None

    def start_shape(self, event):
        # Сохраняем текущее состояние перед началом рисования
        self.history.append(self.image.copy())
        self.redo_stack.clear()  # Очищаем стек повтора

        if self.drawing_shape in ['square', 'circle', 'line', 'dashed_line']:
            self.start_x = event.x
            self.start_y = event.y
            if self.drawing_shape == 'square':
                self.current_shape_id = self.c.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline=self.color, width=self.line_width)
            elif self.drawing_shape == 'circle':
                self.current_shape_id = self.c.create_oval(self.start_x, self.start_y, self.start_x, self.start_y, outline=self.color, width=self.line_width)
            elif self.drawing_shape == 'line':
                self.current_shape_id = self.c.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill=self.color, width=self.line_width)
            elif self.drawing_shape == 'dashed_line':
                self.current_shape_id = self.c.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill=self.color, width=self.line_width, dash=(4, 2))

    def paint(self, event):
        if self.drawing_shape is None:
            paint_color = 'white' if self.eraser_on else self.color
            if self.old_x and self.old_y:
                self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                                   width=self.line_width, fill=paint_color,
                                   capstyle=ROUND, smooth=TRUE, splinesteps=36)
                self.draw.line([self.old_x, self.old_y, event.x, event.y],
                               fill=paint_color, width=self.line_width)
            self.old_x = event.x
            self.old_y = event.y

        if self.current_shape_id:
            end_x = event.x
            end_y = event.y
            if self.drawing_shape == 'square':
                self.c.coords(self.current_shape_id, self.start_x, self.start_y, end_x, end_y)
            elif self.drawing_shape == 'circle':
                self.c.coords(self.current_shape_id, self.start_x, self.start_y, end_x, end_y)
            elif self.drawing_shape == 'line':
                self.c.coords(self.current_shape_id, self.start_x, self.start_y, end_x, end_y)
            elif self.drawing_shape == 'dashed_line':
                self.update_dashed_line(end_x, end_y)

    def update_dashed_line(self, end_x, end_y):
        self.c.delete(self.current_shape_id)
        self.current_shape_id = self.c.create_line(self.start_x, self.start_y, end_x, end_y,
                                                    width=self.line_width, fill=self.color, dash=(4, 2))

    def reset(self, event):
        if self.current_shape_id:
            end_x = event.x
            end_y = event.y
            if self.drawing_shape == 'square':
                self.draw.rectangle([self.start_x, self.start_y, end_x, end_y], outline=self.color, width=self.line_width)
            elif self.drawing_shape == 'circle':
                self.draw.ellipse([self.start_x, self.start_y, end_x, end_y], outline=self.color, width=self.line_width)
            elif self.drawing_shape == 'line':
                self.draw.line([self.start_x, self.start_y, end_x, end_y], fill=self.color, width=self.line_width)
            elif self.drawing_shape == 'dashed_line':
                self.draw.line([self.start_x, self.start_y, end_x, end_y], fill=self.color, width=self.line_width)

            # Сохраняем состояние после завершения рисования
            self.history.append(self.image.copy())
            self.redo_stack.clear()  # Очищаем стек повтора

        self.current_shape_id = None
        self.old_x, self.old_y = None, None
        self.drawing_shape = None

if __name__ == '__main__':
    Paint()