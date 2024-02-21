import pygame, csv, os, random

##########
# Appearances
##########
window_width = 700
window_height = 450

midnight = '#0C6170'
bluegreen = '#37BEB0'
tiffany = '#83BDC0'
baby = '#DBF5F0'

##########
# Get materials
##########

# get cfg from a .csv file of either node,word or node,node1,node2
with open('assets/cfg.csv', 'r') as inputfile:
    cr = csv.reader(inputfile)
    # get the node that have more nodes in it
    content = [[line[0],[line[1],line[2]]] for line in cr if len(line)>2]
    # get the single words
    inputfile.seek(0) # iterate through the file again
    for line in cr:
        if len(line) <= 2:
            content.append(line)
    # get the cfg dictionary
    cfg = {}
    for row in content:
        try:
            cfg[row[0]].append(row[1])
        except KeyError:
            cfg[row[0]] = [row[1]]

# or just give a dictionary of all possible words
#cfg = {"NP":[["D","N"],"cats","dogs","humans"],"VP":[["V","NP"],"walk","sleep","cry"],"S":[["NP","VP"]],"D":["the","a"],"N":["cat","dog","human"],"V":["love","tolerate","like"]}

# a dictionary that has nodes as keys, and nodes that are identical or can occupy the same syntactic position as the node as values
block_list = {'NP':['NP','N'], 'N':['N','NP'], 'VP':['VP', 'V'], 'V':['V', 'VP'], 'D':['D','NP', 'N']}

##########
# Classes
##########
# button code from:
# https://pythonprogramming.sssaltervista.org/buttons-in-pygame/?doing_wp_cron=1685564739.9689290523529052734375
class Button:
    def __init__(self,text,width,height,pos,elevation,onclickFunction=None):
        #Core attributes 
        self.pressed = False
        self.onclickFunction = onclickFunction
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle 
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = bluegreen

        # bottom rectangle 
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = midnight
        #text
        self.text = text
        self.text_surf = button_font.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw(self):
        # elevation logic 
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center 

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(screen,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(screen,self.top_color, self.top_rect,border_radius = 12)
        screen.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = tiffany
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
            else:
                self.dynamic_elecation = self.elevation
                if self.pressed == True:
                    self.onclickFunction()
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = bluegreen

########
# Functions
########
# generate a sentence in the form of [word1, other_option1, word2, other_option2], where other_option is the wrong answer (a word that wouldn't make sense as a continuation of the previous word)
# for example, for the sentence 'a cat walk', generate might give ['a', 'dog', 'cat', 'love', 'walk', 'cats']
def generate(cfg, node='S'):
    expansion = random.choice(cfg[node])
    if type(expansion) == list:
        return generate(cfg, expansion[0]) + generate(cfg, expansion[1])
    elif type(expansion) == str:
        # block the node that makes sense after the current node
        blocked_nodes = block_list[node]
        # get a dictionary without the blocked node
        option_pool = {key:cfg[key] for key in [i for i in list(cfg.keys()) if i not in blocked_nodes]}
        # get a list of options to choose from from the values of option_pool that are strings
        options = [x for lis in list(option_pool.values()) for x in lis if type(x) == str]
        option = random.choice(options)
        return [expansion, option]

# wipe screen
def wipe():
    pygame.draw.rect(screen, baby, pygame.Rect(0, 0, window_width, window_height))
    pygame.display.flip()

# onclickfunctions for the start button
def start():
    global started, hard, start_button, start_button_hard
    started = True
    hard = False
    wipe()
    init_game()

def start_hard():
    global started, hard
    started = True
    hard = True
    wipe()
    init_game()

# initialise a game of 20 trials
def init_game():
    global trial_count, correct_count, reached_end
    wipe()
    trial_count = 0
    correct_count = 0
    reached_end = False
    init_trial()

# initialise a trial
def init_trial():
    global trial_count, sentence, selected, current_location, last_chengyu_freq, reached_end
    wipe()
    # get a flat sentence list first
    sentence_flat = generate(cfg)
    # then parse the flat sentence into a dictionary of location:options
    sentence = {i:[sentence_flat[i*2], sentence_flat[(i*2)+1]] for i in range(int(len(sentence_flat)/2))}
    # change variables
    selected = [sentence[0][0]]
    current_location = 1
    get_options(current_location)

def get_options(current_location):
    global sentence, options, option_buttons
    # get options
    options = sentence[current_location].copy()
    # scramble the order of correct/incorrect options and get button objects
    random.shuffle(options)
    option_buttons = [Button(option, 170, 70, (132.5+(options.index(option)*262.5), 250), 3, select) for option in options]

def select():
    mouse_pos = pygame.mouse.get_pos()
    # if left button clicked
    if option_l_rect.collidepoint(mouse_pos):
        # if correct
        if options[0] == sentence[current_location][0]:
            correct()
        # if wrong
        else:
            wrong()
    # if right button clicked
    elif option_r_rect.collidepoint(mouse_pos):
        # if correct
        if options[1] == sentence[current_location][0]:
            correct()
        # if wrong
        else:
            wrong()

def correct():
    global current_location, selected, correct_count, trial_count
    # if end of chengyu, start a new trial
    if current_location == len(sentence)-1:
        selected.append(sentence[current_location][0])
        correct_count += 1
        trial_count += 1
        # initialise another trial after some time
        start_time = pygame.time.get_ticks()
        delay = 750
        while True:
            current_time = pygame.time.get_ticks()
            # repeat what's done in main loop to prevent freezing
            message = text_font.render(' '.join(selected), True, midnight)
            screen.blit(message, message.get_rect(topleft = (150, 130)))
            # print correct message
            correct = text_font_small.render('Congrats!', True, midnight)
            screen.blit(correct, correct.get_rect(center = (250, 65)))
            pygame.display.flip()
            if current_time - start_time >= delay:
                init_trial()
                break
    else:
        selected.append(sentence[current_location][0])
        pygame.display.flip()
        current_location += 1
        get_options(current_location)

def wrong():
    global trial_count
    trial_count += 1
    start_time = pygame.time.get_ticks()
    delay = 1000
    while True:
        current_time = pygame.time.get_ticks()
        # repeat what's done in main loop to prevent freezing
        message = text_font.render(' '.join(selected), True, midnight)
        screen.blit(message, message.get_rect(topleft = (150, 130)))
        # print wrong message
        wrong = text_font_small.render('Wrong...', True, midnight)
        screen.blit(wrong, wrong.get_rect(center = (250, 65)))
        # print answer
        answer_list = [i[0] for i in sentence.values()][len(selected):]
        answer = ' '+' '.join(answer_list)
        message = text_font.render(answer, True, tiffany)
        # when consolas size 30, a character is approximately 17 wide?
        screen.blit(message, message.get_rect(topleft = (150+(len(' '.join(selected))*17), 130)))
        pygame.display.flip()
        if current_time - start_time >= delay:
            init_trial()
            break

##########
# Main game
##########
def main():
    global screen, icon, clock, button_font, text_font, text_font_small, button_font_tr, text_font_tr
    global started, hard, selected, current_location, option_buttons, option_l_rect, option_r_rect
    # Set working directory to the location of this .py file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    clock = pygame.time.Clock()
    icon = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('CFG Maze Game')
    screen.fill(baby)
    text_font_small = pygame.font.SysFont('consolas',20)
    text_font = pygame.font.SysFont('consolas',30)
    button_font = pygame.font.SysFont('consolas',30)

    # game variables
    started = False

    # buttons
    start_button = Button('start', 120, 50, (290, 300), 3, start)
    option_l_rect = pygame.Rect(132.5, 250, 170, 70)
    option_r_rect = pygame.Rect(395, 250, 170, 70)

    # main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if not started:
            message1 = text_font.render('Welcome to the CFG Maze game!', True, midnight)
            message2 = text_font_small.render('Please select the option that makes the sentence grammatical.', True, midnight)
            message3 = text_font_small.render('Begin:', True, midnight)
            screen.blit(message1, message1.get_rect(center = (350, 100)))
            screen.blit(message2, message2.get_rect(center = (350, 165)))
            screen.blit(message3, message3.get_rect(center = (350, 230)))
            start_button.draw()
        elif trial_count == 20:
            pygame.draw.rect(screen, baby, pygame.Rect(0, 0, window_width, window_height))
            message1 = text_font.render('Game end!', True, midnight)
            message2 = text_font_small.render('Your score: '+str(correct_count)+'/20', True, midnight)
            message3 = text_font_small.render('Another game?', True, midnight)
            screen.blit(message1, message1.get_rect(center = (350, 110)))
            screen.blit(message2, message2.get_rect(center = (350, 170)))
            screen.blit(message3, message3.get_rect(center = (350, 230)))
            start_button.draw()
        else:
            message = text_font.render(' '.join(selected), True, midnight)
            screen.blit(message, message.get_rect(topleft = (150, 130)))
            score = text_font_small.render('Your score: '+str(correct_count)+'/20', True, midnight)
            screen.blit(score, score.get_rect(center = (550, 65)))
            for option in option_buttons:
                option.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()