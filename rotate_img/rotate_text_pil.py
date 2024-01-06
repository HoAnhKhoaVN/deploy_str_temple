from PIL import Image, ImageFont, ImageDraw

text = 'Tĩnh'
font = ImageFont.truetype('arial.ttf', 30)
width, height = font.getsize(text)

image1 = Image.new('RGBA', (200, 150), (205, 115, 96, 0))
# draw1 = ImageDraw.Draw(image1)
# draw1.text((0, 0), text=text, font=font, fill=(255, 128, 0))

image2 = Image.new('RGBA', (width, height), (205, 115, 96, 0))
draw2 = ImageDraw.Draw(image2)
draw2.text((0, 0), text=text, font=font, fill=(16, 5, 5))

image2 = image2.rotate(13, expand= True)

px, py = 10, 10
sx, sy = image2.size

image1.paste(image2, (px, py, px + sx, py + sy), image2)

image1.save("rotate_text_pil.png")