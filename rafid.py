camera_pos = (0, 500, 500)
fovY = 120  # Field of view
GRID_LENGTH = 1000  # Length of grid lines

# Game state variables
CELL_SIZE = 80
MAZE_SIZE = 15
player_pos = [0, 0, 10]
player_angle = 0
player_speed = 5
diamond_pos = [0, 0, 1]
diamond_found = False
score = 0
lives = 5
cheat_mode = False
first_person = False

# Mouse control variables
mouse_x = 0
mouse_y = 0
mouse_sensitivity = 0.05
# Question variables
question_active = False
current_question = None
questions_answered = 0
MAX_QUESTIONS = 5
top_down_view = False
top_down_view_time = 0
TOP_DOWN_VIEW_DURATION = 10
questions = [
    {
        "question": "What is 2+2?",
        "options": ["3", "4"],
        "correct": 1
    },
    {
        "question": "Which is a primary color?",
        "options": ["Red", "Green"],
        "correct": 0
    },
    {
        "question": "Python is a...",
        "options": ["Snake", "Programming language"],
        "correct": 1
    },
    {
        "question": "What is the capital of France?",
        "options": ["London", "Paris"],
        "correct": 1
    },
    {
        "question": "Which is larger?",
        "options": ["Elephant", "Mouse"],
        "correct": 0
    }
]




def generate_maze(size):
    maze = [['1'] * size for _ in range(size)]

    def carve(x, y):
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < size and 0 < ny < size and maze[ny][nx] == '1':
                maze[ny - dy // 2][nx - dx // 2] = '0'
                maze[ny][nx] = '0'
                carve(nx, ny)

    maze[1][1] = '0'
    carve(1, 1)
    maze[0][1] = '0'
    maze[size - 1][size - 2] = '0'
    return ["".join(row) for row in maze]


maze_grid = generate_maze(MAZE_SIZE)

def grid_to_world(row, col):
    x = col * CELL_SIZE - (MAZE_SIZE * CELL_SIZE) / 2 + CELL_SIZE / 2
    y = (MAZE_SIZE - 1 - row) * CELL_SIZE - (MAZE_SIZE * CELL_SIZE) / 2 + CELL_SIZE / 2
    return x, y



def show_question():
    global question_active, current_question, questions_answered
    
    if questions_answered >= MAX_QUESTIONS:
        return
        
    available_questions = [q for q in questions if "asked" not in q]
    if not available_questions:
        return
        
    current_question = random.choice(available_questions)
    current_question["asked"] = True
    question_active = True
    questions_answered += 1



def draw_question():
    if not question_active or not current_question:
        return

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    glBegin(GL_POINTS)
    glVertex2f(0, 0)
    glEnd()

    # Question box
    glColor3f(0.2, 0.2, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(200, 300)
    glVertex2f(800, 300)
    glVertex2f(800, 500)
    glVertex2f(200, 500)
    glEnd()

    # Question text
    glColor3f(1, 1, 1)
    question_x = 250
    question_y = 450
    glRasterPos2f(question_x, question_y)
    for ch in current_question["question"]:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    # Options
    option_y = 400
    for i, option in enumerate(current_question["options"]):
        glRasterPos2f(300, option_y - i * 50)
        option_text = f"{i + 1}. {option}"
        for ch in option_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def handle_answer(answer):
    global question_active, show_map_view, map_view_start_time
    
    if not question_active or not current_question:
        return
        
    question_active = False
    
    if answer == current_question["correct"]:
        show_map_view = True
        map_view_start_time = time.time()

def keyboardListener(key, x, y):
    global player_pos, player_angle, cheat_mode, first_person, question_active

    if game_over:
        return

    key = key.decode('utf-8').lower()
    if question_active:
        if key == '1':
            handle_answer(0)
        elif key == '2':
            handle_answer(1)
        glutPostRedisplay()
        return
    
    dx, dy = 0, 0
    rotate = 0
    if key == 'w':
        dx = player_speed * math.cos(math.radians(player_angle))
        dy = player_speed * math.sin(math.radians(player_angle))
    elif key == 's':
        dx = -player_speed * math.cos(math.radians(player_angle))
        dy = -player_speed * math.sin(math.radians(player_angle))
    elif key == 'a':
        rotate = 5
    elif key == 'd':
        rotate = -5
    elif key == 'c':
        cheat_mode = not cheat_mode
    elif key == 'v':
        first_person = not first_person
        if first_person:
            center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
            center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
            glutWarpPointer(center_x, center_y)
            global mouse_x, mouse_y
            mouse_x = center_x
            mouse_y = center_y
            glutSetCursor(GLUT_CURSOR_NONE)
        else:
            glutSetCursor(GLUT_CURSOR_INHERIT)
    elif key == ' ' and first_person:  # Space to shoot
        shoot_bullet()

    if rotate != 0:
        player_angle = (player_angle + rotate) % 360
    else:
        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy
        if not is_collision(new_x, new_y) or cheat_mode:
            player_pos[0] = new_x
            player_pos[1] = new_y
            check_diamond_collision()

    glutPostRedisplay()

def mouseMotionListener(x, y):
    global mouse_x, mouse_y, player_angle
    
    if first_person:
        dx = x - mouse_x
        dy = y - mouse_y
        
        player_angle -= dx * mouse_sensitivity
        player_angle %= 360
        
        mouse_x = x
        mouse_y = y
        
        if glutGet(GLUT_WINDOW_WIDTH) > 0 and glutGet(GLUT_WINDOW_HEIGHT) > 0:
            center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
            center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
            glutWarpPointer(center_x, center_y)
            mouse_x = center_x
            mouse_y = center_y
        
        glutPostRedisplay()

def enterMouseListener(state):
    if state == GLUT_ENTERED and first_person:
        center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
        center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
        glutWarpPointer(center_x, center_y)
        global mouse_x, mouse_y
        mouse_x = center_x
        mouse_y = center_y

def specialKeyListener(key, x, y):
    global camera_pos
    
    if game_over:
        return
        
    x, y, z = camera_pos

    if key == GLUT_KEY_UP:
        y += 10
    elif key == GLUT_KEY_DOWN:
        y -= 10
    elif key == GLUT_KEY_LEFT:
        x -= 10
    elif key == GLUT_KEY_RIGHT:
        x += 10

    camera_pos = (x, y, z)
    glutPostRedisplay()

def mouseListener(button, state_btn, x, y):
    global first_person, mouse_x, mouse_y, question_active
    
    if game_over:
        return
        
    if button == GLUT_RIGHT_BUTTON and state_btn == GLUT_DOWN:
        if not question_active and questions_answered < MAX_QUESTIONS and not top_down_view:
            show_question()
        else:
            first_person = not first_person
            if first_person:
                center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
                center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
                glutWarpPointer(center_x, center_y)
                mouse_x = center_x
                mouse_y = center_y
                glutSetCursor(GLUT_CURSOR_NONE)
            else:
                glutSetCursor(GLUT_CURSOR_INHERIT)
    elif button == GLUT_LEFT_BUTTON and state_btn == GLUT_DOWN and first_person:
        shoot_bullet()
        
    glutPostRedisplay()