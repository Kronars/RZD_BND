import os
import re
import sys
import pandas as pd
from PIL import Image, ImageOps, ImageFont
from PIL import ImageDraw

class Cell:
    def __init__(self, scrim, size, coord, km) -> None:
        self.scrim_img = scrim[0]
        self.scrim_draw = scrim[1]
        self.img = Image.new('RGB', size, 'white')
        self.draw = ImageDraw.Draw(self.img)
        self.w, self.h = size
        self.x, self.y = coord
        self.km = km
        self.buffer = None
        self.center = lambda wh, sz: int((wh/2)-(sz/2))

    def draw_cell(self):
        self.draw.rectangle((0, 0, self.w, self.h),
                            width=3, outline='black')
        self.put_text(self.km) if self.h == 180 else lambda: None
        return self.img

    def put_text(self, text, kagle=50, color='black'):
        text = str(text)
        w, h = self.w, self.h
        font = ImageFont.truetype("arial.ttf", kagle)
        img_txt = Image.new('L', font.getsize(text))
        draw_txt = ImageDraw.Draw(img_txt)
        draw_txt.text((0,0), text, font=font, fill=255)
        img_txt = ImageOps.invert(img_txt)
        img_txt = img_txt.rotate(90, expand=1)
        w = self.center(w, font.getsize(text)[0])
        h = self.center(h, font.getsize(text)[1])
        self.img.paste(img_txt, (w, h))

    #! метод Жени
    def add_icon(self, icons):
        const, r_x, r_y = 20, 70, 70
        for icon in icons:
            if icon != 'bridge.png':
                icon = Image.open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'modules', 'Pics', icon))
                icon = icon.resize((r_x, r_y), resample=0)
                x, y = self.x, self.y
                self.scrim_img.paste(icon, (x + 15, y + const)) #x, y-координаты угла ячейки. x+3 - смещение на константу 3. y+const - смещение вниз
                const += r_y + 3 #количеств пикселей для отступа вниз + 10 для зазора между иконок
            else:
                icon = Image.open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'modules', 'Pics', icon))
                icon = icon.resize((r_x, r_y), resample=0)
                x, y = self.x, self.y
                self.scrim_img.paste(icon, (x + 20, y - 620))

    def add_line(self, data_dict, column_name=None):
        percent = data_dict['Процент']
        x = self.x + percent
        y = self.y
        vert_line = lambda x, y, y2, color: self.scrim_draw.line((x, y, x, y2), width=5, fill=color)
        tilt_line = lambda x, y, k, color: self.scrim_draw.line((x, y, x + k, y - k), width=5, fill=color)
        tilt_line_k = int((((self.y * 3.5) ** 2) / 2) ** 0.5)
        vert_down_y = y + 900
        if column_name == 'Светофоры':
            color = data_dict['Цвет']
            color = 'red' if color == 'красный' else 'blue'
            vertical_line_y = y + 900
            vert_line(x, y, vertical_line_y, color)
            tilt_line(x, y, vert_down_y, color)
        elif column_name == 'Граничные стрелки станций':
            color = 'red'
            self.add_dotted_lines(x, y, color)
            # tilt_line(x, y, tilt_line_k, color)
            # vert_line(x, y, vert_down_y, color)
        elif column_name == 'Оси станций':
            color = 'green'
            self.add_dotted_lines(x, y, color)
            # vert_line(x, y, tilt_line_k, color)
            # tilt_line(x, y, vert_down_y, color)
    
    def add_dotted_lines(self, x, y, color):
        global_x = x
        global_y = y
        h = 28000 - self.y
        stop = int(h * 3.5)
        step = 15
        grand_step = stop/int(stop/step)
        for x in range(x, stop+int(stop/step), step):
            self.scrim_draw.line((x, y, x + 2, y+2), width=10, fill=color)
            y -= grand_step
            
        stop1 = h    
        for _ in range(global_x, stop1+int(stop1/step), step):
            self.scrim_draw.line((global_x, global_y, global_x, global_y+5), width=5, fill=color)
            global_y += step       

class Grid:
    def __init__(self, path, min, max) -> None:
        self.path_to_save = os.path.join(path, 'Nomogramm.png')
        self.min = min
        self.max = max+1
        self.delta = (max-min)
        self.km = [i for i in range(self.min, self.max)]
        self.cells = dict()
        self.scale_factor = 1
        self.line_tilt_w = 1600
        self.cell_w = 100 * self.scale_factor
        self.cell_h1 = 360 * self.scale_factor
        self.cell_h2 = 180 * self.scale_factor
        self.cell_h3 = 240 * self.scale_factor
        self.cell_h4 = 120 * self.scale_factor
        self.rect_h = 2600 * self.scale_factor
        self.rect_w = self.cell_w * self.delta + self.line_tilt_w
        self.x_start = 0
        self.y_start = self.rect_h
        self.upper_line = self.rect_h - (self.cell_h1 + self.cell_h2 + self.cell_h3 + self.cell_h4)
        self.img = Image.new('RGB', (self.rect_w, self.rect_h), 'white')
        self.draw = ImageDraw.Draw(self.img)
        self.scrim = (self.img, self.draw)
    
    def draw_field(self):
        self.draw.rectangle((0, 0, self.rect_w, self.rect_h), width=5, outline='black')

    def save(self):
        self.img.save(self.path_to_save, 'PNG')

    def draw_grid(self):
        for i, km in enumerate(self.km):
            y = self.rect_h
            self.cells[km] = []
            for h in (self.cell_h1, self.cell_h2, self.cell_h3, self.cell_h4):
                x = i * self.cell_w
                y -= h
                cell = Cell(self.scrim, (self.cell_w, h), (x, y), km)
                cell_img = cell.draw_cell()
                self.cells[km].append(cell)
                self.img.paste(cell_img, (x, y))
            end_line = int((((self.upper_line * 3.5) ** 2) / 2) ** 0.5)
            self.draw.line([(x, y), (x+end_line, y-end_line)], width=2, fill='black')
        end_line = int((((self.upper_line * 3.5) ** 2) / 2) ** 0.5)
        # self.tilt_line_k = end_line
        self.draw.line([(x + self.cell_w, y), (x+end_line + self.cell_w, y-end_line)], width=2, fill='black')
        self.img.save(self.path_to_save, 'PNG')

def draw_nomogramma(data, output_path, start, end):
    grid = Grid(output_path, start, end)
    grid.draw_field()
    grid.draw_grid()
    data.set_index('Киллометр', inplace=True)
    for km, row in data.iterrows():
        bridges = row['Мосты']
        icons_to_add = []
        light = row['Светофоры']
        stations = row['Оси станций']
        start_end_station = row['Граничные стрелки станций']
        cars = row['Переезды'] # параметр 'Наличие дежурного' ? 
        ktsm = row['Комплексы технических средств мониторинга (КТСМ)'] 
        yks = row['Устройства контроля схода подвижного состава (УКСПС)']
        obr = row['Обрывные места']
        lep = row['Места пересечения с ЛЭП']
        
        if cars and cars['Наличие дежурного'] == 'С дежурным':
            icons_to_add.append('green_car.png')
        elif cars and cars['Наличие дежурного'] == 'Без дежурного':
            icons_to_add.append('red_car.png')

        if isinstance(light, dict):
            grid.cells[km][3].add_line(light, 'Светофоры')

        if isinstance(start_end_station, dict):
            grid.cells[km][3].add_line(start_end_station, 'Граничные стрелки станций')
    
        if isinstance(stations, dict):
            grid.cells[km][3].add_line(stations, 'Оси станций')
            
        if isinstance(bridges, dict):
            icons_to_add.append('bridge.png')
            
        icons_to_add.append('yellow_box.png') if ktsm else lambda: None
        icons_to_add.append('blue_box.png') if yks else lambda: None
        icons_to_add.append('red_arrow.png') if obr else lambda: None
        icons_to_add.append('LEP.png') if lep else lambda: None

        grid.cells[km][0].add_icon(icons_to_add)


    grid.save()
