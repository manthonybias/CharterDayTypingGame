import pygame, sys, random, copy

# Initialize pygame
pygame.init()

# nltk natural language toolkit
from nltk.corpus import words
wordlist = words.words()
len_indexes = []
length = 1

#wordlist sorting mechanism
wordlist.sort(key=len)
for i in range(len(wordlist)):
    if len(wordlist[i]) > length:
        length += 1
        len_indexes.append(i)
len_indexes.append(len(wordlist))


# Create window
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT)) #create window with 800x600px size
pygame.display.set_caption("Pygame Demonstration - Charter Day") #set title on app
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) #following tutorial, used to overlay opake layer on screen
timer = pygame.time.Clock() #control game speed
fps = 60

# Debugging variables
debug_frame_index = 0
debug_anim_speed = .50 # Higher is faster
debug_playing_attack = False

# Game Variables
level = 1
active_string = ""
score = 0
lives = 5
paused = True
submit = ""
#user = character(100, HEIGHT- 300, False)
word_objects = []
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
           'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
new_level = True
#Selecting different len strings in the game, by default
selected_d = [False, True, False, False, False, False, False]

# Load in assets (fonts/sounds)
header_font = pygame.font.Font('assets/fonts/Square.ttf', 50)
pause_font = pygame.font.Font('assets/fonts/1up.ttf', 38)
banner_font = pygame.font.Font('assets/fonts/1up.ttf', 28) #1up 28
font = pygame.font.Font('assets/fonts/Blockletter.otf', 28) #AldotheApache
# Character Animations
atk1 = pygame.image.load('assets/samurai1assets/Attack_1.png').convert_alpha()
atk2 = pygame.image.load('assets/samurai1assets/Attack_2.png').convert_alpha()
atk3 = pygame.image.load('assets/samurai1assets/Attack_3.png').convert_alpha()
run2 = pygame.image.load('assets/samurai1assets/Run.png').convert_alpha()
idle = pygame.image.load('assets/samurai1assets/Idle.png').convert_alpha()
# Sound effects
pygame.mixer.init() # pygame audio mixer
pygame.mixer.music.load('assets/sounds/music.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1) # Loops argument, -1 loops infinitely
click = pygame.mixer.Sound('assets/sounds/click.mp3')
click.set_volume(0.3)
woosh = pygame.mixer.Sound('assets/sounds/Swoosh.mp3')
woosh.set_volume(0.2)
wrong = pygame.mixer.Sound('assets/sounds/Instrument Strum.mp3')
wrong.set_volume(0.3)
sliceSounds = [pygame.mixer.Sound('assets/sounds/samuraisounds/slice1.mp3'), pygame.mixer.Sound('assets/sounds/samuraisounds/slice2.wav')]
sliceSounds[0].set_volume(0.5)
sliceSounds[1].set_volume(0.3)



# high score read in from text file
file = open('high_score.txt', 'r')
read = file.readlines()
high_score = int(read[0])
file.close()

class character:
    def __init__(self, home_x_pos, home_y_pos, inAnim):
        self.home_x_pos = home_x_pos
        self.home_y_pos = home_y_pos
        self.inAnim = inAnim

    xposHome = 100
    yposHome = 300
    def draw(self):
        screen.blit(atk1, (self.x_pos, self.y_pos))


class Word:
    def __init__(self, text, speed, y_pos, x_pos):
        self.text = text
        self.speed = speed
        self.y_pos = y_pos
        self.x_pos = x_pos

    def draw(self):
        color = 'black'
        screen.blit(font.render(self.text, True, color), (self.x_pos, self.y_pos))
        act_len = len(active_string)
        if active_string == self.text[:act_len]:
            screen.blit(font.render(active_string, True, 'green'), (self.x_pos, self.y_pos))

    def update(self):
        self.x_pos -= self.speed

class Button:
    def __init__(self, x_pos, y_pos, text, clicked, surf):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.clicked = clicked
        self.surf = surf
    def draw(self):
        circle = pygame.draw.circle(self.surf, (36, 87, 49), (self.x_pos, self.y_pos), 35)
        if circle.collidepoint(pygame.mouse.get_pos()): #"Hover method"
            butts = pygame.mouse.get_pressed()
            if butts[0]: #refers to mouse 1
                pygame.draw.circle(self.surf, (190, 35, 35), (self.x_pos, self.y_pos), 35)
                self.clicked = True
            else:
                pygame.draw.circle(self.surf, (190, 89, 135), (self.x_pos, self.y_pos), 35)
        pygame.draw.circle(self.surf, 'white', (self.x_pos, self.y_pos), 35, 3)
        self.surf.blit(pause_font.render(self.text, True, 'white'), (self.x_pos - 15, self.y_pos - 27)) #changed offset

def getImgSlices(img, countFrames):
    frames = []
    horizontalRes = img.get_width()
    verticalRes = img.get_height()
    frame_w = horizontalRes // countFrames
    frame_h = verticalRes

    for i in range(countFrames):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)

        # Make an independent frame surface
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame.blit(img, (0, 0), rect)

        frames.append(frame)
    return frames


def draw_screen():
    #header section
    screen.blit(banner_font.render(f'SCORE: {score}', True, 'black'), (250, 10))
    screen.blit(banner_font.render(f'BEST: {high_score}', True, 'black'), (550, 10))
    screen.blit(banner_font.render(f'LIVES: {lives}', True, 'black'), (10, 10))

    #footer section
    pygame.draw.rect(screen, (45, 105, 58), pygame.Rect(0, HEIGHT-100, WIDTH, 100)) #x start, y start (32, 42, 68)
    pygame.draw.line(screen, 'white', (250, HEIGHT-100), (250, HEIGHT), 2) #footer partition line
    pygame.draw.line(screen, 'white', (700, HEIGHT - 100), (700, HEIGHT), 2) #footer partition
    pygame.draw.line(screen, 'white', (0, HEIGHT - 100), (WIDTH, HEIGHT-100), 2) #footer top outline

    #misc outlines
    pygame.draw.rect(screen, 'white', pygame.Rect(0, 0, WIDTH, HEIGHT), 5) #window outline
    pygame.draw.rect(screen, 'black', pygame.Rect(0, 0, WIDTH, HEIGHT), 2)  # window outline

    #text for showing the current level, player's current input, high score, score, lives, and pause
    screen.blit(header_font.render(f'Level: {level}', True, 'white'), (10, HEIGHT-75)) #current level text
    screen.blit(header_font.render(f'"{active_string}"', True, 'white'), (270, HEIGHT-75))

    #put pause button here
    pause_btn = Button(748, HEIGHT - 52, "II", False, screen)
    pause_btn.draw()
    return pause_btn.clicked

def draw_pause():
    choice_commits = copy.deepcopy(selected_d)
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0, 0, 0, 100), [100, 100, 600, 300], 0, 5)
    pygame.draw.rect(surface, (0, 0, 0, 200), [100, 100, 600, 300], 5, 5)

    #define buttons for pause menu
    resume_btn = Button(160, 200, ">", False, surface)
    resume_btn.draw()
    quit_btn = Button(410, 200, "X", False, surface)
    quit_btn.draw()
    #define text for pause menu
    surface.blit(header_font.render('MENU', True, 'white'), (110, 110))
    surface.blit(header_font.render('PLAY', True, 'white'), (210, 175))
    surface.blit(header_font.render('QUIT', True, 'white'), (450, 175))
    surface.blit(header_font.render('Active Letter Lengths', True, 'white'), (110, 250))
    #define buttons for letter length selection
    for i in range(len(selected_d)):
        btn = Button(160 + (i * 80), 350, str(i + 2), False, surface)
        btn.draw()
        if btn.clicked:
            if choice_commits[i]:
                choice_commits[i] = False
            else:
                choice_commits[i] = True
        if selected_d[i]:
            pygame.draw.circle(surface, 'green', (160 + (i * 80), 350), 35, 5)

    screen.blit(surface, (0,0))
    return resume_btn.clicked, choice_commits, quit_btn.clicked

def check_answer(scor):
    for wrd in word_objects:
        if wrd.text == submit:
            points = wrd.speed * len(wrd.text) * 10 * (len(wrd.text) / 4)
            scor += int(points)
            word_objects.remove(wrd)
            woosh.play()
    return scor

# Generate new level function
def generate_level():
    word_objs = []
    include = []
    vertical_spacing = (HEIGHT - 150) // level
    if True not in selected_d:
        selected_d[0] = True
    for i in range(len(selected_d)):
        if selected_d[i]:
            include.append((len_indexes[i], len_indexes[i+1]))
    for i in range(level):
        speed = random.randint(2, 3)
        y_pos = random.randint(10 + (i * vertical_spacing), (i+1) *vertical_spacing)
        x_pos = random.randint(WIDTH, WIDTH + 1000)
        ind_sel = random.choice(include)
        index = random.randint(ind_sel[0], ind_sel[1])
        text = wordlist[index].lower()
        new_word = Word(text, speed, y_pos, x_pos)
        word_objs.append(new_word)
    return word_objs

# Check high score
def check_high_score():
    global high_score
    if score > high_score:
        high_score = score
        file = open('high_score.txt', 'w')
        file.write(str(int(high_score)))
        file.close()

atkanims = [getImgSlices(atk1, 4), getImgSlices(atk2, 5), getImgSlices(atk3, 4)]
idleanim = getImgSlices(idle, 6)
debug_current_anim = random.choice(atkanims)
# Game loop
running = True
while running:
    screen.fill("gray")
    timer.tick(fps)
    # draw background screen stuff and statuses and get pause button status
    pause_butt = draw_screen()
    if paused:
        resume_butt, changes, quit_butt = draw_pause()
        if resume_butt:
            paused = False
        if quit_butt:
            #add checking for high score before exiting program
            check_high_score()
            running = False
    if new_level and not paused:
        word_objects = generate_level()
        new_level = False
    else:
        for w in word_objects:
            w.draw()
            if not paused:
                w.update()
            if w.x_pos < -200: #if a word exits the screen by 200px remove life
                word_objects.remove(w)
                lives -= 1
    if len(word_objects) <= 0 and not paused:
        level += 1
        new_level = True
    if submit != "":
        init = score
        score = check_answer(score)
        submit = ""
        if init == score:
            wrong.play()
            pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            check_high_score()
            running = False
        if event.type == pygame.KEYDOWN:
            if not paused:
                if event.unicode.lower() in letters: #list of valid letters, keystrokes
                    active_string += event.unicode.lower()

                    debug_current_anim = random.choice(atkanims)
                    debug_frame_index = 0
                    debug_playing_attack = True
                    random.choice(sliceSounds).play()



                    random.choice(sliceSounds).play()
                if event.key == pygame.K_BACKSPACE and len(active_string) > 0:
                    active_string = active_string[:-1]
                    click.play()
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    submit = active_string
                    active_string = ""
            if event.key == pygame.K_ESCAPE:
                if paused:
                    paused = False
                else:
                    paused = True

        if event.type == pygame.MOUSEBUTTONUP and paused:
            if event.button == 1:
                selected_d = changes
    if pause_butt:
        paused = True

    if lives < 1:
        paused = True
        level = 1
        lives = 5
        word_objects = []
        new_level = True
        check_high_score()
        score = 0
    debug_frame_index += debug_anim_speed

    if debug_playing_attack:
        # play chosen attack ONCE, then go back to idle
        if debug_frame_index >= len(debug_current_anim):
            debug_frame_index = 0
            debug_playing_attack = False
        frame = debug_current_anim[int(debug_frame_index)]
    else:
        # loop idle forever
        if debug_frame_index >= len(idleanim):
            debug_frame_index = 0
        frame = idleanim[int(debug_frame_index)]

    screen.blit(frame, (50, (HEIGHT / 2) - frame.get_height() / 2))

    pygame.display.flip() #updates screen

pygame.quit()