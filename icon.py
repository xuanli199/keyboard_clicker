from PIL import Image, ImageDraw
import os

def create_icon():
    # 创建一个64x64的图像，背景为蓝色
    img = Image.new('RGB', (64, 64), color=(0, 120, 212))
    draw = ImageDraw.Draw(img)
    
    # 绘制一个简单的键盘图标
    # 键盘外框
    draw.rectangle([(10, 20), (54, 44)], outline=(255, 255, 255), width=2)
    
    # 键盘按键
    for i in range(3):
        for j in range(4):
            draw.rectangle([(14 + j*10, 24 + i*6), (20 + j*10, 28 + i*6)], 
                          fill=(200, 200, 200), outline=(255, 255, 255))
    
    # 保存图标
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keyboard_icon.ico")
    img.save(icon_path, format="ICO")
    return icon_path

if __name__ == "__main__":
    create_icon()
    print("图标已创建")