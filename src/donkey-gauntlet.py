#!/usr/bin/env python
# donkey-gauntlet.py
# donkey-gauntlet — original Python/Pygame game inspired by Donkey.bas (c) 1981 Microsoft
# Copyright (c) 2025 Peter Clifton
# Licensed under the GNU General Public License v3.0 (GPL-3.0). See LICENSE for details.

import pygame, sys, random
import time

pygame.init()



#-----------------------------------------------
# Video Driver check
#-----------------------------------------------
# If opened in non desktop env might open without
# input being configured properly.
# to avoid this we check and exit if it
# appears not in X11 or Wayland env

# Detect which SDL video driver is actually being used
driver = pygame.display.get_driver()

# Check for common “non-GUI” backends
if driver in ("fbcon", "directfb", "svgalib", "kmsdrm", "offscreen", "dummy"):
    print(f"  Warning: SDL video driver is '{driver}'.")
    print("   This mode may not support keyboard or mouse input properly.")
    print("   Run this app from a desktop environment with X11 or Wayland.")
    # print("   If you’re testing headless, use: SDL_VIDEODRIVER=dummy")
    exitgame()
else:
    print(f"Using SDL video driver: {driver}")



pygame.mixer.init() # for sounds
pygame.display.set_caption("donkey-gauntlet")

#-----------------------------------------------
# Aux variables
#-----------------------------------------------
WIDTH, HEIGHT = 400,400
TEXT_COLOR = 255, 255, 0
LINE_COLOR = 255, 0, 0
BG = 0,0,0
GAME_BG = 32,126,133
GAME_FG = 255,255,255
ROAD_COLOR = 86, 91, 92
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
font30 = pygame.font.Font(None,30)
font20 = pygame.font.Font(None,20)
font16 = pygame.font.Font(None,16)
font10 = pygame.font.Font(None,10)

#-----------------------------------------------
# Game state variables
#-----------------------------------------------

# For debugging
#TICK_LIMIT = 10000
#ticks = 0

line_top = 420
line_top_offset = 0 # cycles per iteration in range 0 <= lto <= 39
line_length = 20

car_in_right_lane_flag = 0
CAR_START_Y = 375
CAR_START_X = 165
CAR_WIDTH = 20
CAR_HEIGHT = 30 # i.e. length
car_y = 375
car_x = 165

DONKEY_START_Y = -20
DONKEY_END_Y = 420
DONKEY_X_IN_LEFT_LANE = 160
donkey_in_right_lane_flag = 0
donkey_x = 155
DONKEY_WIDTH = 30
DONKEY_HEIGHT = 20
donkey_in_play = 0
donkey_y = -20
DONKEY_COLOR = 161, 59, 16
FIRST_DONKEY_PACE = 1
donkeyPace = FIRST_DONKEY_PACE

crashed = False
keep_playing = True
score  = 0


#-----------------------------------------------
# Functions
#-----------------------------------------------

def exitgame():
    pygame.quit()
    sys.exit()

def intro():
    screen.fill(BG)
    text = font.render("donkey-gauntlet", True, TEXT_COLOR)
    screen.blit(text, (100,160))
    text = font16.render("inspired by Donkey.bas", True, TEXT_COLOR)
    screen.blit(text, (130,195))
    time.sleep(0.1)
    pygame.display.flip()
    time.sleep(5.0)


def countdown():
    screen.fill(BG)
    time.sleep(0.25)
    text1 = font16.render("Avoid the donkeys", True, TEXT_COLOR)
    text2 = font20.render("Use SPACE to change lanes", True, TEXT_COLOR)
    text3 = font30.render("Press spacebar to continue", True, TEXT_COLOR)
    step = 0
    while step < 3:
        if step >= 0:
            screen.blit(text1, (60,100))
        if step >= 1:
            screen.blit(text2, (60,165))
        if step >= 2:
            screen.blit(text3, (60,230))
        pygame.display.flip()
        step = step + 1
        time.sleep(0.9)
    
    pygame.event.clear()
    waitin_space_press = True
    while waitin_space_press:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            exitgame()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                waitin_space_press = False


#-----------------------------------------------
# Inner game loop
#-----------------------------------------------
def game():
    #global ticks 
    global car_in_right_lane_flag
    
    #while (ticks < TICK_LIMIT) and (not crashed):
    while (not crashed):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitgame()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    car_in_right_lane_flag = 1 - car_in_right_lane_flag
                    playSound_changelanes()

        draw_fixed_background()
        draw_dashed_centre_line() # this will also incr-cycle line_top_offset value
        donkey_update()
        donkey_draw()
        car_update()
        car_draw()
        score_draw()
        check_for_crash()
      
        pygame.display.flip()
        #ticks = ticks + 1
        clock.tick(60)

def check_for_crash():
    global crashed
    if (abs(car_y - donkey_y) < 10) and (abs(car_x - donkey_x) < 10):
        crashed = True
        playSound_crash()
        playSound_crash()
        playSound_crash()

def car_update():
    global car_x
    car_x = CAR_START_X + (60 * car_in_right_lane_flag)

def donkey_update():
    global donkey_y
    global donkey_in_play
    global donkey_in_right_lane_flag
    global donkey_x
    global donkeyPace
    global score
    
    if donkey_in_play == 1:
        donkey_y = donkey_y + donkeyPace
    elif line_top_offset == 20 and random.random() < 0.5: # create new donkey
        donkey_in_right_lane_flag = (1 if random.random() < 0.5 else 0)
        donkeyPace = donkeyPace + (1 if random.random() < 0.5 else 0)
        donkey_x = DONKEY_X_IN_LEFT_LANE + (70 * donkey_in_right_lane_flag)
        donkey_in_play = 1
    
    if donkey_y > DONKEY_END_Y:
        donkey_in_play = 0
        donkey_y = DONKEY_START_Y
        score = score + 1

def donkey_draw():
    if donkey_in_play:
        left = donkey_x - (DONKEY_WIDTH/2)
        top = donkey_y - (DONKEY_HEIGHT/2)
        pygame.draw.rect(screen, DONKEY_COLOR,
                        (left, top, DONKEY_WIDTH, DONKEY_HEIGHT))

def draw_fixed_background():
    screen.fill(GAME_BG)
    # road background:                left, top, width, heigt
    pygame.draw.rect(screen, ROAD_COLOR, (128,0, 144, 400))
    # draw the left and right road border lines
    pygame.draw.line(screen, GAME_FG, (130,0), (130, 400))
    pygame.draw.line(screen, GAME_FG, (270,0), (270, 400))

def draw_dashed_centre_line():
    global line_top_offset
    for line_top in range(-20, 460, 40):
        pygame.draw.line(screen, GAME_FG, 
                        (200, line_top + line_top_offset), 
                        (200, line_top + line_top_offset + line_length))
    line_top_offset = line_top_offset +1
    if line_top_offset >= 40:
        line_top_offset = 0

def car_draw():
    left = car_x - (CAR_WIDTH/2)
    top = car_y - (CAR_HEIGHT/2)
    pygame.draw.rect(screen, GAME_FG,
        ( left, top, CAR_WIDTH, CAR_HEIGHT))

def score_draw():
    text = font20.render("Score: {}".format(score), True, GAME_FG)
    screen.blit(text, (285, 370))


def reset_game_variables():
    #global ticks
    global line_top_offset
    global car_in_right_lane_flag
    global donkey_in_right_lane_flag
    global donkey_in_play
    global car_y
    global car_x
    global donkey_y
    global donkey_x
    global crashed
    global donkeyPace
    global score
    #ticks = 0
    line_top_offset = 0
    car_in_right_lane_flag = 0
    donkey_in_right_lane_flag = 0
    donkey_in_play = 0
    car_y = CAR_START_Y
    car_x = CAR_START_X
    donkey_x = DONKEY_X_IN_LEFT_LANE
    donkey_y = DONKEY_START_Y
    crashed = False
    donkeyPace = FIRST_DONKEY_PACE
    score = 0

def result_screen():
    global keep_playing
    screen.fill(BG)
    text = font30.render("Game over!", True, TEXT_COLOR)
    text2 = font16.render("Press space bar to continue or any other key to quit", True, TEXT_COLOR)
    screen.blit(text, (145,170))
    screen.blit(text2, (60,200))
    pygame.display.flip()

    pygame.event.clear()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            exitgame()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game_variables()
                break
            else:
                keep_playing = False
                break
   

#-----------------------------------------------
# Sound effects
#-----------------------------------------------
def playSound_changelanes():
    pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=b'x00'*100))

def playSound_crash():
    pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=b'xff'*4000))


#-----------------------------------------------
# Main loop
#-----------------------------------------------
def main():
    # Intro sequence
    intro()
    countdown()

    # Outside of game loop
    while keep_playing:
        game()
        time.sleep(2.0)
        result_screen()

    exitgame()

if __name__ == "__main__":
    main()
