import pygame
import math

pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('ShootingGame assets/font/myFont.ttf', 32)
big_font = pygame.font.Font('ShootingGame assets/font/myFont.ttf', 60)
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
bgs = []
banners = []
guns = []
target_images = [[], [], []]
targets = {1: [10, 5, 3],
           2: [12, 8, 5],
           3: [15, 12, 8, 3]
           }
level = 1
points = 0
total_shots = 0
mode = 0  # freeplay = 0, accuracy = 1, time = 2
ammo = 0
time_passed = 0
time_remaining = 0
counter = 1
best_freeplay = 0
best_ammo = 0
best_timed = 0
shot = False
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True
one_coords = [[], [], []]
two_coords = [[], [], []]
three_coords = [[], [], [], []]
menu_img = pygame.image.load(f'ShootingGame assets/menu/mainMenu.png')
game_over_img = pygame.image.load(f'ShootingGame assets/menu/gameOver.png')
pause_img = pygame.image.load(f'ShootingGame assets/menu/pause.png')
# backgound, targets, bannery a zbrane v levelech
for i in range(1, 4):
    bgs.append(pygame.image.load(f'ShootingGame assets/bg/{i}.png'))
    banners.append(pygame.image.load(f'ShootingGame assets/banners/{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'ShootingGame assets/guns/{i}.png'), (100, 100)))
    if i < 3:
        for j in range(1, 4):
            target_images[i - 1].append(
                pygame.transform.scale(pygame.image.load(f'ShootingGame assets/targets/{i}/{j}.png'),
                                       (120 - (j * 18), 80 - (j * 12))))
    else:
        for j in range(1, 5):
            target_images[i - 1].append(
                pygame.transform.scale(pygame.image.load(f'ShootingGame assets/targets/{i}/{j}.png'),
                                       (120 - (j * 18), 80 - (j * 12))))
# zapis high scores do textaku
file = open('high_scores.txt', 'r')
read_file = file.readlines()
file.close()
best_freeplay = int(read_file[0])
best_ammo = int(read_file[1])
best_timed = int(read_file[2])

# sound
pygame.mixer.init()
pygame.mixer.music.load('ShootingGame assets/sound/bg_music.mp3')
plate_sound = pygame.mixer.Sound('ShootingGame assets/sound/assets_sounds_Broken plates.wav')
plate_sound.set_volume(.2)
bird_sound = pygame.mixer.Sound('ShootingGame assets/sound/assets_sounds_Drill Gear.mp3')
bird_sound.set_volume(.2)
laser_sound = pygame.mixer.Sound('ShootingGame assets/sound/assets_sounds_Laser Gun.wav')
laser_sound.set_volume(.3)
pygame.mixer.music.play()


# ingame zobrazuje score/ radek 330 starting, hodnoty to bere z global hodnot
def draw_score():
    points_text = font.render(f'Points: {points}', True, 'black')
    screen.blit(points_text, (320, 660))
    shots_text = font.render(f'Total shots: {total_shots}', True, 'black')
    screen.blit(shots_text, (320, 687))
    time_text = font.render(f'Time Elapsed: {time_passed}', True, 'black')
    screen.blit(time_text, (320, 714))
    # podle modu vypisuje posledni hodnotu
    if mode == 0:
        mode_text = font.render(f'Freeplay!', True, 'black')

    if mode == 1:
        mode_text = font.render(f'Ammo remaining: {ammo}', True, 'black')

    if mode == 2:
        mode_text = font.render(f'Time Remaining: {time_remaining}', True, 'black')
    screen.blit(mode_text, (320, 741))


# zbrane
def draw_gun():
    mouse_pos = pygame.mouse.get_pos()
    gun_point = (WIDTH / 2, HEIGHT - 200)
    lasers = ['red', 'purple', 'green']
    clicks = pygame.mouse.get_pressed()
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])  # prepona = protilehla/prilehly
    else:
        slope = -10000
    angle = math.atan(slope)  # tan-1 (prepona)
    rotation = math.degrees(angle)  # radiany -> stupne
    if mouse_pos[0] < WIDTH / 2:
        gun = pygame.transform.flip(guns[level - 1], True, False)  # zrcadlove otoceni gun
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation),
                        (WIDTH / 2, HEIGHT - 250))  # .rotate rotuje protismeru hodin
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)  # vystrely
    else:
        gun = guns[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation),
                        (WIDTH / 2, HEIGHT - 250))  # tady bude uhel vzdy zaporny, proto odecitame od 270
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)


def move_enemies(coords): #posouvani enemaku v levelu
    if level == 1 or level == 2:  #odpovida poctu radku enemy
        max_val = 3
    else:
        max_val = 4
    for i in range(max_val): #prochazeni coords enemaku
        for j in range(len(coords[i])):
            my_coords = coords[i][j]  #[[], [], [], []]
            if my_coords[0] < -150:
                coords[i][j] = WIDTH, my_coords[1] #kdyz vyjede z obrazovky tak se vrati zprava
            else:
                coords[i][j] = (my_coords[0] - 2 ** i, my_coords[1]) #posouvani scalujici s radou odspodu
    return coords #vraci coords na jejich posunute pozici


def check_shot(targets, coords): #targets dava rectangle enemies viz. draw level; coords a targets jsou vesme totozny
    global points
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)): # targets zadany jako list trech listu , <rect(x,y(roh), z, l (velikost stran))>
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j) #vyhodis z coords zasazenej
                points += 10 + 10 * (i ** 2) #scaluje s hodnotnejsima enemakama
                if level == 1:
                    bird_sound.play()
                elif level == 2:
                    plate_sound.play()
                elif level == 3:
                    laser_sound.play()
    return coords #vraci coords zredukovane o ty sestrelene


def draw_level(coords): #dostava pozice enemies
    if level == 1 or level == 2:
        target_rects = [[], [], []] #pripravuje list podle levelu
    else:
        target_rects = [[], [], [], []] #pripravuje list podle levelu
    for i in range(len(coords)): #prochazi postupne 3 listy
        for j in range(len(coords[i])): #prohazi kazdy list
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]), #do prazdnych target_rects vytvari obdelniky drzi se podle coords akorat k x pricita 20
                                                    (60 - i * 12, 60 - i * 12))) #zmensuji se postupne
            screen.blit(target_images[level - 1][i], coords[i][j]) #pridavani obrazku
    return target_rects


def draw_menu():
    global game_over, pause, mode, menu, level, time_passed, total_shots, points, ammo, time_remaining
    global best_timed, best_ammo, best_freeplay, write_values, clicked, new_coords
    game_over = False
    pause = False
    screen.blit(menu_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    screen.blit(font.render(f'{best_freeplay}', True, 'black'), (340, 580))
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (650, 580))
    timed_button = pygame.rect.Rect((170, 661), (260, 100))
    screen.blit(font.render(f'{best_timed}', True, 'black'), (350, 710))
    reset_button = pygame.rect.Rect((475, 661), (260, 100))
    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False
        time_passed = 0
        ammo = 81
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False
        time_remaining = 30
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_ammo = 0
        best_timed = 0
        clicked = True
        write_values = True


def draw_game_over():
    global level, pause, game_over, menu, points, total_shots, time_passed, time_remaining, clicked
    if mode == 0:
        display_score = time_passed
    else:
        display_score = points
    screen.blit(game_over_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    exit_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    screen.blit(big_font.render(f'{display_score}', True, 'black'), (650, 570))
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        game_over = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run
        run = False


def draw_pause():
    global level, pause, menu, points, total_shots, time_passed, time_remaining, clicked
    screen.blit(pause_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    resume_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        pygame.mixer.music.play()
        level = 0
        pause = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
        clicked = True


run = True
while run:
    timer.tick(fps)
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1  #zaznamenava cas
            time_passed += 1
            if mode == 2:
                time_remaining -= 1
    if new_coords:
        one_coords = [[], [], []] #restart coords
        two_coords = [[], [], []]
        three_coords = [[], [], [], []]
        for i in range(3): # coords pro lvl 1
            my_list = targets[1] # targets line 16
            for j in range(my_list[i]): #podle toho kolik je enemies v targets tolikrat se to vypisuje
                one_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(3): # coords pro lvl 2
            my_list = targets[2]
            for j in range(my_list[i]):
                two_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(4): # coords pro lvl 3
            my_list = targets[3]
            for j in range(my_list[i]):
                three_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))
        new_coords = False

    screen.fill('black')
    screen.blit(bgs[level - 1], (0, 0)) #zobrazeni bckgrounds
    screen.blit(banners[level - 1], (0, HEIGHT - 200)) #zobrazeni banneru
    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()

    if level == 1:
        target_boxes = draw_level(one_coords) #dostane rectangles
        one_coords = move_enemies(one_coords)
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_enemies(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False
    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_enemies(three_coords)
        if shot:
            three_coords = check_shot(target_boxes, three_coords)
            shot = False

    if level > 0:
        draw_gun()
        draw_score()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200): #zaznamenava strely
                shot = True
                total_shots += 1
                if mode == 1: #odecita naboje
                    ammo -= 1
            if (670 < mouse_position[0] < 860) and (660 < mouse_position[1] < 715): #policko pro pausu
                resume_level = level
                pause = True
            if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760): #tlacitko restart
                menu = True
                pygame.mixer.music.play() #zapne musicku znova
                clicked = True
                new_coords = True #restart coords
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

    if level > 0:
        if target_boxes == [[], [], []]: #posouva level
            level += 1
        if level == 3 and target_boxes == [[], [], [], []] or (mode == 1 and ammo == 0) or ( #ukoncuje hru
                mode == 2 and time_remaining == 0):
            new_coords = True #restart coords
            pygame.mixer.music.play() #restart musicky
            if mode == 0:
                if time_passed < best_freeplay or best_freeplay == 0: #kontroluje high scores
                    best_freeplay = time_passed
                    write_values = True
            if mode == 1:
                if points > best_ammo:
                    best_ammo = points
                    write_values = True
            if mode == 2:
                if points > best_timed:
                    best_timed = points
                    write_values = True
            game_over = True
    if write_values: #prepisuje hodnoty do textaku
        file = open('high_scores.txt', 'w')
        file.write(f'{best_freeplay}\n{best_ammo}\n{best_timed}')
        file.close()
        write_values = False
    pygame.display.flip()

pygame.quit()

# zmenit fixne dane hodnoty k urceni pozic na obrazovce
# make it fullscreen
# add more enemies to fill the gap in each row
# add my own assets
# add more difficult levels(things not moving in rows,poping up random on screen,...)
#zvladnout lip coords