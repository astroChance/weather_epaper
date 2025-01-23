from PIL import Image,ImageDraw,ImageFont
from dashboard_data import *

import epaper
epap_model = "epd7in3f"
epd = epaper.epaper(epap_model).EPD()


## Make fonts
nasa_font_18 = ImageFont.truetype("./nasalization-rg.otf", 18)
nasa_font_20 = ImageFont.truetype("./nasalization-rg.otf", 20)
nasa_font_28 = ImageFont.truetype("./nasalization-rg.otf", 28)
nasa_font_32 = ImageFont.truetype("./nasalization-rg.otf", 32)

## Text color parameters
main_text_col = epd.RED
sub_text_col1 = epd.BLACK
sub_text_col2 = epd.BLUE


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## GET DATA FOR DISPLAY

pollen_data = get_pollen_data()
tree_pollen_color = pollen_color(pollen_data["TREE POLLEN"])
weed_pollen_color = pollen_color(pollen_data["WEED POLLEN"])
grass_pollen_color = pollen_color(pollen_data["GRASS POLLEN"])
mold_spores_color = pollen_color(pollen_data["MOLD SPORES"])

oz_val, oz_lev, oz_code = get_ozone_current(airnow_api_key=airnow_api_key)
part_val, part_lev, part_code = get_particulate_current(airnow_api_key=airnow_api_key)
oz_fore_lev, oz_fore_code = get_ozone_forecast(airnow_api_key=airnow_api_key)
part_fore_lev, part_fore_code = get_particulate_forecast(airnow_api_key=airnow_api_key)
oz_color = aq_color(oz_code)
part_color = aq_color(part_code)
oz_fore_color = aq_color(oz_fore_code)
part_fore_color = aq_color(part_fore_code)

heights_lat = "29.8068"
heights_long = "-95.4181"
weather_data = make_weather_data(weather_api_key=weather_api_key, 
                        latitude=heights_lat, 
                        longitude=heights_long)
temp_f = weather_data["current"]["temp_f"]
humidity = weather_data["current"]["humidity"]
uvi = weather_data["current"]["uvi"]
weather_id = weather_data["current"]["id"]
curr_uvi_color = uvi_color(uvi)



##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Initialize canvas
my_display = Image.new('RGB', (epd.width, epd.height), epd.WHITE)  
draw = ImageDraw.Draw(my_display)


##----------------------------
## MAKE BOXES

outline_width = 2
corner_radius = 20
outline_color = epd.BLACK

## Upper left quadrant
upper_left_coords = (5,35,395,250)
draw.rounded_rectangle(upper_left_coords, outline=outline_color, 
                       width=outline_width, radius=corner_radius)

## Upper right quadrant
upper_right_coords = (405,35,795,250)
draw.rounded_rectangle(upper_right_coords, outline=outline_color, 
                       width=outline_width, radius=corner_radius)

## Lower zone
lower_coords = (5,260,795,475)
draw.rounded_rectangle(lower_coords, outline=outline_color, 
                       width=outline_width, radius=corner_radius)

##----------------------------
## FILL BOXES

## Upper left-----------------------

## Icons
if temp_f > 85:
    icon_path = "./icons/thermo_hi.bmp"
elif temp_f < 50:
    icon_path = "./icons/thermo_low.bmp"
else:
    icon_path = "./icons/thermo_mid.bmp"
thermometer = Image.open(icon_path)
newsize = (50,110)
thermometer = thermometer.resize(newsize, Image.NEAREST)
my_display.paste(thermometer, (25,40))

humid_uv_xloc = upper_left_coords[0]+250
humid_uv_ylocs = [upper_left_coords[1]+5, upper_left_coords[1]+100]
humid_uv_icon_yoffset = 35
icon_path = "./icons/humidity.bmp"
humid_icon = Image.open(icon_path)
newsize = (40,40)
humid_icon = humid_icon.resize(newsize, Image.NEAREST)
my_display.paste(humid_icon, (humid_uv_xloc, humid_uv_ylocs[0]+humid_uv_icon_yoffset))

if round(uvi)<=2:
    icon_path = "./icons/uv_low.bmp"
elif round(uvi)<=5:
    icon_path = "./icons/uv_medium.bmp"
elif round(uvi)<=7:
    icon_path = "./icons/uv_moderate.bmp"
elif round(uvi)>=8:
    icon_path = "./icons/uv_high.bmp"
else:
    icon_path = "./icons/uv.bmp"
uv_icon = Image.open(icon_path)
newsize = (40,40)
uv_icon = uv_icon.resize(newsize, Image.NEAREST)
my_display.paste(uv_icon, (humid_uv_xloc, humid_uv_ylocs[1]+humid_uv_icon_yoffset))

## Current temperature
display_curr_temp = str(round(temp_f))
draw.text((upper_left_coords[0]+20, upper_left_coords[1]+115), 'Feels\nLike', 
          font=nasa_font_20, fill=sub_text_col1)
draw.text((20, 200), display_curr_temp+' \N{DEGREE SIGN}F', 
          font=nasa_font_32,fill=sub_text_col1)


## Current conditions
condition_xloc = upper_left_coords[0]+120
condition_yloc = upper_left_coords[1]+40
current_condition_icon = get_condition_icon(weather_id)
condition_icon = Image.open(current_condition_icon)
newsize = (100,100)
condition_icon = condition_icon.resize(newsize, Image.NEAREST)
my_display.paste(condition_icon, (condition_xloc, condition_yloc))


## Current humidity
humid_uv_val_xoffset = 75
humid_uv_val_yoffset = 40

display_curr_humidity = str(round(humidity))
draw.text((humid_uv_xloc, humid_uv_ylocs[0]), 
          'HUMIDITY', font=nasa_font_20, fill=sub_text_col1)
draw.text((humid_uv_xloc+humid_uv_val_xoffset, 
           humid_uv_ylocs[0]+humid_uv_val_yoffset), 
          display_curr_humidity+'\N{DEGREE SIGN}', font=nasa_font_28, fill=sub_text_col1)

## UV index
display_curr_uvi = str(round(uvi))
draw.text((humid_uv_xloc, humid_uv_ylocs[1]), 
          'UV INDEX', font=nasa_font_20, fill=sub_text_col1)
draw.text((humid_uv_xloc+humid_uv_val_xoffset, 
           humid_uv_ylocs[1]+humid_uv_val_yoffset), 
          display_curr_uvi, font=nasa_font_28, fill=curr_uvi_color,
         stroke_width=1, stroke_fill=sub_text_col1)

## Upper right-----------------------

# place the icons
allergen_xlocs = [440, 530, 620, 710]
allergen_yloc = 95

icon_path = "./icons/tree.bmp"
tree_7color = Image.open(icon_path)
newsize = (40,40)
tree_7color = tree_7color.resize(newsize, Image.NEAREST)
my_display.paste(tree_7color, (allergen_xlocs[0],allergen_yloc))

icon_path = "./icons/weed.bmp"
weed_7color = Image.open(icon_path)
newsize = (40,40)
weed_7color = weed_7color.resize(newsize, Image.NEAREST)
my_display.paste(weed_7color, (allergen_xlocs[1],allergen_yloc))

icon_path = "./icons/grass.bmp"
grass_7color = Image.open(icon_path)
newsize = (40,40)
grass_7color = grass_7color.resize(newsize, Image.NEAREST)
my_display.paste(grass_7color, (allergen_xlocs[2],allergen_yloc))

icon_path = "./icons/mold.bmp"
mold_7color = Image.open(icon_path)
newsize = (40,40)
mold_7color = mold_7color.resize(newsize, Image.NEAREST)
my_display.paste(mold_7color, (allergen_xlocs[3],allergen_yloc))


# place the icon color levels
draw.text((allergen_xlocs[0]-5, allergen_yloc+50), 
          'TREE', font=nasa_font_18, fill=tree_pollen_color,
         stroke_width=1, stroke_fill=sub_text_col1)
draw.text((allergen_xlocs[1]-5, allergen_yloc+50), 
          'WEED', font=nasa_font_18, fill=weed_pollen_color,
         stroke_width=1, stroke_fill=sub_text_col1)
draw.text((allergen_xlocs[2]-5, allergen_yloc+50), 
          'GRASS', font=nasa_font_18, fill=grass_pollen_color,
         stroke_width=1, stroke_fill=sub_text_col1)
draw.text((allergen_xlocs[3]-5, allergen_yloc+50), 
          'MOLD', font=nasa_font_18, fill=mold_spores_color,
         stroke_width=1, stroke_fill=sub_text_col1)



# place the air quality boxes
today_ozone_coords = (upper_right_coords[0]+100, upper_right_coords[1]+25,
                      upper_right_coords[0]+235, upper_right_coords[1]+50)
today_part_coords = (upper_right_coords[0]+240, upper_right_coords[1]+25,
                      upper_right_coords[0]+375, upper_right_coords[1]+50)
draw.rounded_rectangle(today_ozone_coords, outline=outline_color, 
                       width=outline_width, radius=corner_radius,
                      fill=oz_color)
draw.rounded_rectangle(today_part_coords, outline=outline_color, 
                       width=outline_width, radius=corner_radius,
                      fill=part_color)

tomorrow_ozone_coords = (upper_right_coords[0]+50, upper_right_coords[1]+185,
                      upper_right_coords[0]+185, upper_right_coords[1]+210)
tomorrow_part_coords = (upper_right_coords[0]+210, upper_right_coords[1]+185,
                      upper_right_coords[0]+345, upper_right_coords[1]+210)
draw.rounded_rectangle(tomorrow_ozone_coords, outline=outline_color, 
                       width=outline_width, radius=corner_radius,
                      fill=oz_fore_color)
draw.rounded_rectangle(tomorrow_part_coords, outline=outline_color, 
                       width=outline_width, radius=corner_radius,
                      fill=part_fore_color)


# add the text
draw.text((upper_right_coords[0]+10, upper_right_coords[1]+5), 
          'TODAY', font=nasa_font_20, fill=sub_text_col2)
draw.text((upper_right_coords[0]+10, upper_right_coords[1]+140), 
          'TOMORROW', font=nasa_font_20, fill=sub_text_col2)
draw.text((today_ozone_coords[0]+38, today_ozone_coords[1]-20), 
          'ozone', font=nasa_font_18, fill=sub_text_col1)
draw.text((today_part_coords[0]+10, today_part_coords[1]-20), 
          'particulates', font=nasa_font_18, fill=sub_text_col1)
draw.text((tomorrow_ozone_coords[0]+38, tomorrow_ozone_coords[1]-20), 
          'ozone', font=nasa_font_18, fill=sub_text_col1)
draw.text((tomorrow_part_coords[0]+10, tomorrow_part_coords[1]-20), 
          'particulates', font=nasa_font_18, fill=sub_text_col1)


## Bottom ---------------------------

center_x = epd.width//2
box_top = lower_coords[1]
box_bottom = lower_coords[3]

draw.text((lower_coords[0]+10, lower_coords[1]+5), 
          'HOURLY', font=nasa_font_20, fill=sub_text_col2)
draw.text((lower_coords[2]-75, lower_coords[1]+5), 
          'DAILY', font=nasa_font_20, fill=sub_text_col2)

hourly_xloc = lower_coords[0]+10
hourly_yloc = lower_coords[1]+5
x_bump = 48
for f in weather_data["hourly"]:
    hour = list(f.keys())[0]
    temp = f[hour]["temp_f"]
    id = f[hour]["id"] 

    draw.text((hourly_xloc, hourly_yloc+50), 
          hour, font=nasa_font_20, fill=sub_text_col1)
    draw.text((hourly_xloc, hourly_yloc+90), 
          str(temp)+'\N{DEGREE SIGN}', font=nasa_font_18, fill=sub_text_col1)
    
    condition_icon = Image.open(get_condition_icon(id))
    newsize = (30,30)
    condition_icon = condition_icon.resize(newsize, Image.NEAREST)
    my_display.paste(condition_icon, (hourly_xloc, hourly_yloc+130))

    hourly_xloc = hourly_xloc + x_bump


daily_xloc = center_x+35
daily_yloc = lower_coords[1]+5
x_bump = 70
for f in weather_data["daily"]:
    day = list(f.keys())[0]
    max_temp = f[day]["max_temp"]
    min_temp = f[day]["min_temp"]
    id = f[day]["id"] 

    draw.text((daily_xloc, daily_yloc+30), 
          day, font=nasa_font_20, fill=sub_text_col1)
    draw.text((daily_xloc, daily_yloc+60), 
          "max", font=nasa_font_18, fill=sub_text_col1)
    draw.text((daily_xloc, daily_yloc+80), 
          str(max_temp)+'\N{DEGREE SIGN}', font=nasa_font_18, fill=sub_text_col1)
    draw.text((daily_xloc, daily_yloc+100), 
          "min", font=nasa_font_18, fill=sub_text_col1)
    draw.text((daily_xloc, daily_yloc+120), 
          str(min_temp)+'\N{DEGREE SIGN}', font=nasa_font_18, fill=sub_text_col1)

    condition_icon = Image.open(get_condition_icon(id))
    newsize = (45,45)
    condition_icon = condition_icon.resize(newsize, Image.NEAREST)
    my_display.paste(condition_icon, (daily_xloc, daily_yloc+160))

    daily_xloc = daily_xloc + x_bump


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## PIZZAZZ
icon_path = "./icons/astros.bmp"
astros_logo = Image.open(icon_path)
newsize = (90,90)
astros_7color = astros_7color.resize(newsize, Image.NEAREST)
my_display.paste(astros_7color, (355,210))

draw.text((210, 0), 'LAUNCHPAD STATUS', font=nasa_font_32, fill=main_text_col)

## divider lines
draw.line((center_x-6, box_top+50, center_x-6, box_bottom-10),
         fill=epd.ORANGE, width=4)
draw.line((center_x-2, box_top+50, center_x-2, box_bottom-10),
         fill=epd.YELLOW, width=4)
draw.line((center_x+2, box_top+50, center_x+2, box_bottom-10),
         fill=epd.RED, width=4)


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## SEND DATA

epd.display(epd.getbuffer(my_display))
