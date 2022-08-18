import glob
from PIL import Image, ImageDraw, ImageFont, ImageDraw
import requests
import io
import os.path

#W, H = (300,200)
#msg = "hello"
#draw.text(((W-w)/2,(H-h)/2), msg, fill="black")
#im.save("hello.png", "PNG")

def draw_text_on_image_at_position(
    input_image_path:str, 
    output_image_path:str, 
    textToDraw:str, 
    costToDraw:str,
    x:int, y:int,
    fillColor:str, fontSize:int):    

    #bail if file exists
    #if os.path.exists(output_image_path):
    #   return

    font1 = "https://github.com/googlefonts/Arimo/raw/main/fonts/ttf/Arimo-Regular.ttf"
    font = load_font_from_uri(fontSize, font1)

    image = Image.open(input_image_path)
    image = image.rotate(270, expand=1)
    draw = ImageDraw.Draw(image)
    textW, textH = draw.textsize(textToDraw, font) # how big is out text
    costW, costH = draw.textsize(costToDraw, font) # how big is out text


    draw.text((x, y), textToDraw, font_size=fontSize,anchor="ls", font=font, fill=fillColor)

    if costToDraw != "":
        xx = (2084 - (costW +300))
        costToDraw = str(costToDraw) + " /mo"
        draw.text((xx,y), costToDraw, font_size=(fontSize-40), anchor="ls", font=font, fill="red")

    image = image.rotate(-270, expand=1)
    image.save(output_image_path)


def create_image_with_text(output_image_path:str, textToDraw:str, x:int, y:int, h:int, w:int, color:str, alignment:str, fillColor:str, fontPath:str, fontSize:int):    
    image = Image.new("RGB", (h, w), color)
    draw = ImageDraw.Draw(image)

    # Load font from URI
    font1 = "https://github.com/googlefonts/Arimo/raw/main/fonts/ttf/Arimo-Regular.ttf"
    truetype_url = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true'
    font = load_font_from_uri(fontSize, font1)

    #font = ImageFont.truetype(fontPath, layout_engine=ImageFont.LAYOUT_BASIC, size=fontSize)
    draw.text((x, y), textToDraw, font=font, anchor="ls", fill=fillColor)
    image.save(output_image_path)


def load_font_from_uri(size:int, url:str):
    # Load font from URI
    truetype_url = url
    r = requests.get(truetype_url, allow_redirects=True)
    return ImageFont.truetype(io.BytesIO(r.content), size=size)


#angled text 
#https://stackoverflow.com/questions/245447/how-do-i-draw-text-at-an-angle-using-pythons-pil
def draw_text_90_into(text: str, into, at):

    # Measure the text area
    font = ImageFont.truetype (r'C:\Windows\Fonts\Arial.ttf', 16)
    wi, hi = font.getsize (text)

    # Copy the relevant area from the source image
    img = into.crop ((at[0], at[1], at[0] + hi, at[1] + wi))

    # Rotate it backwards
    img = img.rotate (270, expand = 1)

    # Print into the rotated area
    d = ImageDraw.Draw (img)
    d.text ((0, 0), text, font = font, fill = (0, 0, 0))

    # Rotate it forward again
    img = img.rotate (90, expand = 1)

    # Insert it back into the source image
    # Note that we don't need a mask
    into.paste (img, at)









if __name__ == "__main__":
    #create_image_with_text("temp\\output2.jpg", "Mmmuuuurrrrrrrrrr", 10.0,525,575,575,"white", "left", "black", "temp\\airstrike.ttf", 44)
    draw_text_on_image_at_position("temp\\tron_grid_test.png", "temp\\output_test.png", "defaultresourcegroup_ea","$299.00", 200,1800, "yellow", 110)

#'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Black.ttf?raw=true'
    # input_image_path:str, 
    # output_image_path:str, 
    # textToDraw:str, 
    # costToDraw:str,
    # x:int, y:int,
    # fillColor:str, fontSize:int):    

