import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import colorchooser, filedialog
from math import radians, cos, sin
from PIL import Image

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画板")

        self.button_frame = tk.Frame(root, bg="lightgray")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建画布
        self.canvas = tk.Canvas(root, bg='white', width=600, height=500)
        self.canvas.pack()


        # 加载并调整图标大小
        self.select_icon = self.resize_icon("tp\裁剪上下线.png", (36, 36))
        self.clear_icon = self.resize_icon("tp\清除.png", (36, 36))
        self.undo_icon = self.resize_icon("tp\icon_cancel.png", (32, 32))
        self.save_icon = self.resize_icon("tp\保存.png", (32, 32))
        self.big_icon = self.resize_icon("tp\H5动画-弹性放大.png", (32, 32))
        self.small_icon = self.resize_icon("tp\视频_缩小.png", (32, 32))
        self.xpc = self.resize_icon("tp\橡皮擦.png", (32, 32))
        self.qianbi = self.resize_icon("tp\铅笔.png", (32, 32))
        self.fill = self.resize_icon("tp\填充颜色.png", (32, 32))

        self.save_button = tk.Button(self.button_frame, image=self.save_icon, text="Save", compound=tk.TOP,
                                     command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.undo_button = tk.Button(self.button_frame, image=self.undo_icon, text="Withdraw", compound=tk.TOP,
                                     command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.cancel_button = tk.Button(self.button_frame, image=self.big_icon, text="Enlarge ", compound=tk.TOP,
                                       command=self.scale_selection)
        self.cancel_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.cancel_button = tk.Button(self.button_frame, image=self.small_icon, text="Narrow", compound=tk.TOP,
                                       command=self.shrink_selection)
        self.cancel_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.select_button = tk.Button(self.button_frame, image=self.select_icon, text="Select", compound=tk.TOP,
                                       command=self.enable_selection)
        self.select_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.pencil_button = tk.Button(self.button_frame, image=self.qianbi, text="Pencil", compound=tk.TOP,
                                       command=self.set_pencil_tool)
        self.pencil_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.eraser_button = tk.Button(self.button_frame, image=self.xpc, text="Eraser", compound=tk.TOP,
                                       command=self.toggle_eraser_mode)
        self.eraser_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.eraser_button = tk.Button(self.button_frame, image=self.fill, text="Fill", compound=tk.TOP,
                                       command=self.activate_fill_mode)
        self.eraser_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.clear_button = tk.Button(self.button_frame, image=self.clear_icon, text="Empty", compound=tk.TOP,
                                      command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=20, pady=10)



        # 初始化画图参数
        self.color = 'black'
        self.fill_color = 'white'
        self.shape = ''
        self.start_x = None
        self.start_y = None
        self.current_shape = None
        self.pencil_path = []  # 记录铅笔路径
        self.fill_mode = False  # 用于切换到填充模式
        self.select_rect = None  # 选择框
        self.select_start_x = None  # 选择框起始坐标
        self.select_start_y = None
        self.selected_items = []  # 选中的项目
        self.dragging = False  # 是否正在拖动选中项
        self.eraser_size = 10
        self.current_shape = None  # 当前绘制的形状
        self.history = []  # 历史记录，用于撤销
        self.control_points = []  # 记录曲线控制点
        # 状态栏
        self.status_label = tk.Label(root, text="坐标: (0, 0)", bd=1, relief=tk.SUNKEN, anchor='w')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.pencil_path = []
        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Button-3>", self.on_right_button_press)  # 右键按下
        self.canvas.bind("<B3-Motion>", self.on_right_mouse_drag)  # 右键拖动
        self.canvas.bind("<ButtonRelease-3>", self.on_right_button_release)  # 右键释放
        self.canvas.bind("<Motion>", self.update_status)


        # 创建菜单
        self.create_menu()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        # 形状菜单
        shape_menu = tk.Menu(menu)
        menu.add_cascade(label='画图', menu=shape_menu)
        shape_menu.add_command(label='铅笔', command=lambda: self.set_shape('pencil'))
        shape_menu.add_command(label='直线', command=lambda: self.set_shape('line'))
        shape_menu.add_command(label='矩形', command=lambda: self.set_shape('rectangle'))
        shape_menu.add_command(label='圆形', command=lambda: self.set_shape('oval'))

        # 新增的操作菜单
        operation_menu = tk.Menu(menu)
        menu.add_cascade(label='旋转', menu=operation_menu)
        operation_menu.add_command(label='镜像反转', command=self.flip_selection)
        operation_menu.add_command(label='X轴翻转', command=self.flip_horizontal)
        operation_menu.add_command(label='Y轴翻转', command=self.flip_vertical)
        operation_menu.add_command(label="旋转图形", command=self.open_rotation_window)

        # 颜色菜单
        color_menu = tk.Menu(menu)
        menu.add_cascade(label='颜色', menu=color_menu)
        color_menu.add_command(label='选择线条颜色', command=self.choose_color)
        color_menu.add_command(label='选择填充颜色', command=self.choose_fill_color)


        fill_menu = tk.Menu(menu)
        menu.add_cascade(label='填充', menu=fill_menu)
        fill_menu.add_command(label='后期填充（铅笔）', command=self.custom_fill_pencil)
        fill_menu.add_command(label='图案填充', command=self.activate_fill_mode)
        # 曲线菜单
        curve_menu = tk.Menu(menu)
        menu.add_cascade(label='曲线', menu=curve_menu)
        curve_menu.add_command(label='抛物线', command=lambda: self.set_shape('parabola'))
        curve_menu.add_command(label='Hermite曲线', command=lambda: self.set_shape('hermite'))
        curve_menu.add_command(label='Bezier曲线', command=lambda: self.set_shape('bezier'))

        # 保存图像
        menu.add_command(label='保存图像', command=self.save_image)

    def resize_icon(self, path, size):
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def set_pencil_tool(self):
        self.shape = 'pencil'

    def on_button_press(self, event):
        if self.shape == 'pencil':
            self.pencil_path = [(event.x, event.y)]  # 开始记录路径

    def on_mouse_drag(self, event):
        if self.shape == 'pencil':
            self.pencil_path.append((event.x, event.y))
            self.draw_pencil_path()

    def draw_pencil_path(self):
        for i in range(1, len(self.pencil_path)):
            self.canvas.create_line(self.pencil_path[i - 1], self.pencil_path[i], fill=self.color, width=2)

    def set_pencil_tool(self):
        if self.shape == 'pencil':
            self.shape = ''  # 退出铅笔模式
            self.canvas.config(cursor="")  # 恢复默认光标
        else:
            self.shape = 'pencil'  # 进入铅笔模式
            self.canvas.config(cursor="hand1")  # 更改光标为十字形，模拟铅笔
    def clear_canvas(self):
        """清空画布"""
        self.canvas.delete("all")


    def toggle_eraser_mode(self):
        """切换橡皮擦模式"""
        if self.shape == 'eraser':
            self.shape = ''  # 退出橡皮擦模式
            self.canvas.config(cursor="")  # 恢复默认光标
        else:
            self.shape = 'eraser'  # 进入橡皮擦模式
            self.canvas.config(cursor="no")  # 更改光标为十字形，模拟橡皮擦

    def on_mouse_drag(self, event):
        """鼠标拖动绘制图形或铅笔路径"""
        if self.shape == 'eraser':
            # 橡皮擦模式下，擦除
            self.erase(event.x, event.y)

    def erase(self, x, y):
        """橡皮擦功能：擦除鼠标位置附近的图形"""
        # 创建一个与橡皮擦大小相同的矩形范围
        erase_area = self.canvas.create_oval(x - self.eraser_size // 2, y - self.eraser_size // 2,
                                             x + self.eraser_size // 2, y + self.eraser_size // 2,
                                             outline="", fill="white", tags="eraser")

        # 找到所有与椭圆重叠的图形
        overlapping_items = self.canvas.find_overlapping(x - self.eraser_size // 2, y - self.eraser_size // 2,
                                                         x + self.eraser_size // 2, y + self.eraser_size // 2)
        for item in overlapping_items:
            if item not in self.canvas.find_withtag("eraser"):  # 确保不删除橡皮擦的临时图形
                self.canvas.delete(item)  # 删除重叠的图形

        # 删除临时擦除区域的椭圆
        self.canvas.delete("eraser")


    def open_rotation_window(self):
        """打开弹出窗口让用户输入旋转角度"""
        rotation_window = tk.Toplevel(self.root)
        rotation_window.title("自定义旋转")

        tk.Label(rotation_window, text="输入角度（°）").pack()
        angle_entry = tk.Entry(rotation_window)
        angle_entry.pack()

        def apply_rotation():
            try:
                angle = float(angle_entry.get())
                self.rotate_selected_items(angle)
            except ValueError:
                print("输入角度（°）")
            rotation_window.destroy()

        tk.Button(rotation_window, text="确定", command=apply_rotation).pack()

    def resize_icon(self, path, size):
        # 打开图标文件
        image = Image.open(path)
        # 调整大小
        image = image.resize(size, Image.LANCZOS)
        # 转换为 Tkinter PhotoImage
        return ImageTk.PhotoImage(image)

    def rotate_selected_items(self, angle):
        """旋转选中的图形"""
        if not self.selected_items:
            return

        x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        angle_rad = radians(angle)  # 将角度转为弧度

        cos_angle = cos(angle_rad)
        sin_angle = sin(angle_rad)

        for item in self.selected_items:
            coords = self.canvas.coords(item)
            rotated_coords = []

            for i in range(0, len(coords), 2):
                x = coords[i] - center_x
                y = coords[i + 1] - center_y

                # 旋转公式
                rotated_x = x * cos_angle - y * sin_angle + center_x
                rotated_y = x * sin_angle + y * cos_angle + center_y
                rotated_coords.extend([rotated_x, rotated_y])

            # 更新图形的坐标
            self.canvas.coords(item, *rotated_coords)

    def flip_horizontal(self):
        """沿X轴翻转选中的图形"""
        if not self.selected_items:
            return
        x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
        center_y = (y1 + y2) / 2

        for item in self.selected_items:
            coords = self.canvas.coords(item)
            flipped_coords = []
            for i in range(1, len(coords), 2):
                flipped_y = 2 * center_y - coords[i]
                flipped_coords.extend([coords[i - 1], flipped_y])
            self.canvas.coords(item, *flipped_coords)

    def flip_vertical(self):
        """沿Y轴翻转选中的图形"""
        if not self.selected_items:
            return
        x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
        center_x = (x1 + x2) / 2

        for item in self.selected_items:
            coords = self.canvas.coords(item)
            flipped_coords = []
            for i in range(0, len(coords), 2):
                flipped_x = 2 * center_x - coords[i]
                flipped_coords.extend([flipped_x, coords[i + 1]])
            self.canvas.coords(item, *flipped_coords)

    def set_shape(self, shape):
        self.shape = shape
        self.control_points = []  # 清空控制点

    def on_button_press(self, event):


        """记录控制点并绘制曲线"""
        if self.shape in ['parabola', 'hermite', 'bezier']:
            # 添加控制点
            self.control_points.append((event.x, event.y))

            # 根据曲线类型绘制
            if self.shape == 'parabola' and len(self.control_points) == 2:
                self.draw_parabola(self.control_points[0], self.control_points[1])
                self.control_points = []  # 绘制完成后清空控制点
            elif self.shape == 'hermite' and len(self.control_points) == 4:
                self.draw_hermite(self.control_points[0], self.control_points[1], self.control_points[2],
                                  self.control_points[3])
                self.control_points = []  # 绘制完成后清空控制点
            elif self.shape == 'bezier' and len(self.control_points) == 4:
                self.draw_bezier(self.control_points[0], self.control_points[1], self.control_points[2],
                                 self.control_points[3])
                self.control_points = []  # 绘制完成后清空控制点
        else:
            # 处理其他形状
            if self.shape == 'selection':
                if self.select_rect:
                    self.canvas.delete(self.select_rect)  # 删除之前的选择框
                self.select_start_x = event.x
                self.select_start_y = event.y
                self.select_rect = self.canvas.create_rectangle(self.select_start_x, self.select_start_y, event.x,

                                                                event.y, outline='blue', fill='', dash=(10, 6))
            elif self.shape == 'eraser':
                # 如果是橡皮擦模式，记录橡皮擦起始位置
                self.erase_item(event.x, event.y)
            elif self.fill_mode:
                # 填充模式下，点击封闭区域进行填充
                self.fill_shape(event.x, event.y)
            elif self.shape == 'pencil':
                self.pencil_path = [(event.x, event.y)]  # 开始记录路径
            else:
                self.start_x = event.x
                self.start_y = event.y

    def draw_parabola(self, start, end):
        """绘制抛物线"""
        points = []
        for t in range(100):
            x = start[0] + t / 100 * (end[0] - start[0])
            y = start[1] + (t / 100) ** 2 * (end[1] - start[1])
            points.append((x, y))
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i + 1], fill=self.color)

    def draw_hermite(self, p0, p1, r0, r1):
        """绘制Hermite曲线"""
        points = []
        for t in range(100):
            t /= 100
            h1 = 2 * t ** 3 - 3 * t ** 2 + 1
            h2 = -2 * t ** 3 + 3 * t ** 2
            h3 = t ** 3 - 2 * t ** 2 + t
            h4 = t ** 3 - t ** 2
            x = h1 * p0[0] + h2 * p1[0] + h3 * r0[0] + h4 * r1[0]
            y = h1 * p0[1] + h2 * p1[1] + h3 * r0[1] + h4 * r1[1]
            points.append((x, y))
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i + 1], fill=self.color)

    def draw_bezier(self, p0, p1, p2, p3):
        """绘制Bezier曲线"""
        points = []
        for t in range(100):
            t /= 100
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
            points.append((x, y))
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i + 1], fill=self.color)

    def scale_selection(self):
        """放大选中的图形"""
        if not self.selected_items:
            return  # 如果没有选中的图形，直接返回

        # 获取选取框的边界坐标
        x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        scale_factor = 2.0  # 放大比例

        # 遍历所有选中项，进行缩放
        for item in self.selected_items:
            self.canvas.scale(item, center_x, center_y, scale_factor, scale_factor)

    def shrink_selection(self):
        """缩小选中的图形"""
        if not self.selected_items:
            return  # 如果没有选中的图形，直接返回

        # 获取选取框的边界坐标
        x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        scale_factor = 0.5  # 缩小比例

        # 遍历所有选中项，进行缩放
        for item in self.selected_items:
            self.canvas.scale(item, center_x, center_y, scale_factor, scale_factor)

    def flip_selection(self):
        """翻转选中图形"""
        if not self.selected_items:
            return  # 如果没有选中的图形，直接返回

        # 获取选取框的边界坐标
        x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # 遍历所有选中项，判断是否是铅笔绘画线段
        for item in self.selected_items:
            coords = self.canvas.coords(item)
            if len(coords) >= 4:  # 确保至少是线段
                new_coords = []
                for i in range(0, len(coords), 2):
                    # 计算每个点相对于中心的对称点
                    new_x = 2 * center_x - coords[i]
                    new_y = 2 * center_y - coords[i + 1]
                    new_coords.extend([new_x, new_y])

                # 更新线段的坐标，实现整体翻转
                self.canvas.coords(item, *new_coords)



    def select_shape(self, event):
        """选择被选择框包围的图形"""
        if self.select_rect:  # 确保选择框已创建
            x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
            self.selected_items = self.canvas.find_overlapping(x1, y1, x2, y2)

            # 计算选择框的中心坐标以设置旋转控制点
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            # 添加旋转控制点
            self.canvas.create_line(center_x, center_y - 10, center_x, center_y + 10, fill='red')  # 垂直线
            self.canvas.create_line(center_x - 10, center_y, center_x + 10, center_y, fill='red')  # 水平线

    def custom_fill_pencil(self):
        # 填充自定义铅笔绘制的封闭区域
        if self.is_closed_shape(self.pencil_path):
            self.fill_pencil_shape()

    def fill_pencil_shape(self):
        # 使用多边形填充铅笔绘制的封闭区域
        self.canvas.create_polygon(self.pencil_path, fill=self.fill_color)

    def choose_color(self):
        self.color = colorchooser.askcolor()[1]

    def choose_fill_color(self):
        """选择填充颜色"""
        self.fill_color = colorchooser.askcolor()[1]

    def activate_fill_mode(self):
        """激活填充模式，鼠标进入填充状态"""
        self.fill_mode = True
        self.shape = ''  # 退出绘图模式
        self.canvas.config(cursor="dotbox")  # 改变鼠标光标为填充模式

    def set_shape(self, shape):
        self.shape = shape
        self.current_shape = None  # 重置当前形状
        self.fill_mode = False  # 离开填充模式
        # 恢复光标为默认状态
        self.canvas.config(cursor="")

    def enable_selection(self):
        """启用选择区域"""
        self.shape = 'selection'  # 设置为选择模式
        self.cancel_selection()  # 取消任何现有的选择

    def cancel_selection(self):
        """取消选择框和选中的项目"""
        if self.select_rect:
            self.canvas.delete(self.select_rect)
            self.select_rect = None
            self.selected_items = []  # 清空选择的项目

    def on_mouse_move(self, event):
        """鼠标移动时更新橡皮擦光标"""
        if self.shape == 'eraser':
            # 记录当前鼠标事件
            self.last_event = event

            # 删除之前绘制的光标圆形
            if hasattr(self, 'cursor'):
                self.canvas.delete(self.cursor)

            # 更新光标
            self.update_cursor(event)

    def on_mouse_leave(self, event):
        """鼠标离开画布时删除光标"""
        if hasattr(self, 'cursor'):
            self.canvas.delete(self.cursor)

    def on_mouse_drag(self, event):
        """鼠标拖动绘制图形或铅笔路径"""
        if self.shape == 'selection' and self.select_rect:
            self.canvas.coords(self.select_rect, self.select_start_x, self.select_start_y, event.x, event.y)
        elif self.shape == 'pencil':
            # 添加当前点到铅笔路径
            self.pencil_path.append((event.x, event.y))

            line_item = self.canvas.create_line(self.pencil_path[-2], self.pencil_path[-1], fill=self.color)

            self.history.append({'type': 'pencil', 'item': line_item})
        elif self.shape in ['line', 'rectangle', 'oval']:
                # 删除上一帧的临时图形
            if self.current_shape:
                self.canvas.delete(self.current_shape)
                # 根据图形类型绘制当前帧的临时图形
            if self.shape == 'line':
                self.current_shape = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                                                 fill=self.color)
            elif self.shape == 'rectangle':
                self.current_shape = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                                      outline=self.color)
            elif self.shape == 'oval':
                self.current_shape = self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y,
                                                                 outline=self.color)
        elif self.shape == 'eraser':
                # 橡皮擦模式下，擦除
             self.erase(event.x, event.y)

    def erase_item(self, x, y):
        """橡皮擦功能：擦除图形"""
        eraser_area = self.canvas.find_overlapping(x - self.eraser_size, y - self.eraser_size, x + self.eraser_size,
                                                   y + self.eraser_size)
        for item in eraser_area:
            self.canvas.delete(item)

    def on_button_release(self, event):
        """完成图形绘制或路径绘制"""
        if self.shape == 'selection' and self.select_rect:
            self.select_shape(event)
        elif self.shape in ['line', 'rectangle', 'oval']:
            if self.current_shape:
                self.history.append({'type': 'draw', 'item': self.current_shape})
                self.current_shape = None  # 清空临时图形
   
        self.canvas.config(cursor="")

    def undo(self):
        """撤销上一步操作"""
        if self.history:
            last_action = self.history.pop()  # 获取上一个操作
            if last_action['type'] == 'pencil':
                # 如果是铅笔路径操作，删除最后绘制的线段
                self.canvas.delete(last_action['item'])
            elif last_action['type'] == 'draw':
                # 如果是图形绘制操作，删除上一个图形
                self.canvas.delete(last_action['item'])


    def on_right_button_press(self, event):
        if self.select_rect:
            self.dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def on_right_mouse_drag(self, event):
        if self.dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.move_selection(dx, dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def on_right_button_release(self, event):
        self.dragging = False

    def select_shape(self, event):
        """选择被选择框包围的图形"""
        if self.select_rect:  # 确保选择框已创建
            x1, y1, x2, y2 = self.canvas.coords(self.select_rect)
            self.selected_items = self.canvas.find_overlapping(x1, y1, x2, y2)

    def move_selection(self, dx, dy):
        """移动选中的图形"""
        for item in self.selected_items:
            if item in self.canvas.find_all():
                self.canvas.move(item, dx, dy)

    def update_status(self, event):
        self.status_label.config(text=f"坐标: ({event.x}, {event.y})")

    def fill_shape(self, x, y):
        """填充点击的封闭区域"""
        shape_id = self.canvas.find_closest(x, y)[0]
        if self.is_closed_shape(shape_id):  # 判断形状是否封闭
            self.canvas.itemconfig(shape_id, fill=self.fill_color)

    def is_closed_shape(self, shape_id):
        """判断形状是否封闭"""
        # 这里可以添加更复杂的判断逻辑
        return True  # 假设形状都是封闭的

    def save_image(self):
        """保存当前画布为图像文件"""
        # 打开文件对话框，选择保存位置和文件名
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")]
        )

        if file_path:  # 如果用户选择了文件名
            # 获取画布的尺寸
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()

            # 创建一个新的图像对象
            image = Image.new("RGB", (width, height), "white")  # 创建白色背景图像
            draw = ImageDraw.Draw(image)  # 创建绘图对象

            # 遍历画布中的所有图形，并在图像上绘制它们
            for item in self.canvas.find_all():
                coords = self.canvas.coords(item)
                fill_color = self.canvas.itemcget(item, "fill")
                width = self.canvas.itemcget(item, "width")

                # 将宽度转换为整数
                width = int(float(width)) if width else 1  # 默认宽度为 1

                # 根据图形类型绘制
                if self.canvas.type(item) == "line":
                    outline_color = self.canvas.itemcget(item, "fill")  # 对于线条，使用填充色作为轮廓色
                    draw.line(coords, fill=outline_color, width=width)
                elif self.canvas.type(item) == "rectangle":
                    outline_color = self.canvas.itemcget(item, "outline")
                    draw.rectangle(coords, fill=fill_color, outline=outline_color)
                elif self.canvas.type(item) == "oval":
                    outline_color = self.canvas.itemcget(item, "outline")
                    draw.ellipse(coords, fill=fill_color, outline=outline_color)
                # 这里可以继续添加其他图形类型

            # 保存图像
            image.save(file_path)
            print(f"图像已保存到: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
