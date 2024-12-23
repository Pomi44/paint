def hex_to_rgb(color):
    """Преобразует цвет в формате hex или название цвета в кортеж RGB."""
    if color.startswith('#'):
        hex_color = color[1:]  # Удаляем символ '#'
    else:
        hex_color = f"{self.root.winfo_rgb(color)[0] >> 8:02x}{self.root.winfo_rgb(color)[1] >> 8:02x}{self.root.winfo_rgb(color)[2] >> 8:02x}"

    if len(hex_color) != 6:  # Проверяем длину
        raise ValueError(f"Неверный формат цвета: {color}")
    
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
