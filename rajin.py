# Enemy variables
enemies = []  # List to hold all enemies
enemy_speed = 2
enemy_active = True
enemy_scale = 1.0
enemy_scale_direction = 0.01
enemy_started = False

# Big Ball variables
# big_ball_active = False
big_ball_pos = [0, 0, 50]
big_ball_radius = 30
big_ball_speed = 0.5

# big_ball_respawn_timer = 0
big_ball_respawn_delay = 3
# big_ball_spawned = False
big_ball_active = False
big_ball_spawned = False
big_ball_spawn_timer = 0  # NEW: Timer to track when to first spawn
big_ball_respawn_timer = 0
big_ball_spawn_delay = 5  # Delay in seconds before first spawn


def initialize_enemies():
    global enemies
    enemies = []

    # Generate 6 enemies at different locations
    for _ in range(6):
        while True:
            enemy_row = random.randint(MAZE_SIZE//4, MAZE_SIZE - 2)
            enemy_col = random.randint(1, MAZE_SIZE - 2)
            if maze_grid[enemy_row][enemy_col] == '0':
                x, y = grid_to_world(enemy_row, enemy_col)
                enemies.append({
                    'pos': [x, y, 20],
                    'active': True,
                    'scale': 1.0,
                    'scale_dir': 0.01,
                    'attack_range': 200,
                    'attack_angle': 45,
                    'speed': enemy_speed
                })
                break

def initialize_positions():
    global player_row, player_col, player_pos, player_start_pos, diamond_row, diamond_col, diamond_pos
    global big_ball_active, big_ball_pos, big_ball_respawn_timer
    
    player_row, player_col = 0, 1
    player_pos[0], player_pos[1] = grid_to_world(player_row, player_col)
    player_start_pos = player_pos.copy()

    diamond_row, diamond_col = MAZE_SIZE - 1, MAZE_SIZE - 2
    diamond_pos[0], diamond_pos[1] = grid_to_world(diamond_row, diamond_col)
    
    # big_ball_active = True
    big_ball_pos = [player_start_pos[0], player_start_pos[1], 50]
    big_ball_respawn_timer = 0
    
    initialize_enemies()

initialize_positions()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_maze():
    for row_idx, row in enumerate(maze_grid):
        for col_idx, cell in enumerate(row):
            if cell == '1':
                x, y = grid_to_world(row_idx, col_idx)
                glPushMatrix()
                glTranslatef(x, y, 50)
                glScalef(CELL_SIZE, CELL_SIZE, 100)
                if (row_idx + col_idx) % 2 == 0:
                    glColor3f(0.5, 0.5, 0.5)
                else:
                    glColor3f(0.35, 0.28, 0.18)
                glutSolidCube(1)
                glPopMatrix()

def draw_player():
    if not first_person:
        glPushMatrix()
        glTranslatef(player_pos[0], player_pos[1], player_pos[2])
        glRotatef(player_angle, 0, 0, 1)

        # Body
        glPushMatrix()
        glColor3f(0.8, 0.6, 0.4)
        glScalef(0.5, 0.5, 10)
        glutSolidCube(1)
        glPopMatrix()

        # Head
        glPushMatrix()
        glTranslatef(0, 0, 10)
        glColor3f(1, 0.8, 0.6)
        glutSolidSphere(0.2, 20, 20)
        glPopMatrix()

        # Limbs
        limbs = [
            (-0.3, 0, -0.2, 0.1, 0.1, 0.3),
            (0.3, 0, -0.2, 0.1, 0.1, 0.3),
            (-0.15, 0, -0.5, 0.1, 0.2, 0.1),
            (0.15, 0, -0.5, 0.1, 0.2, 0.1)
        ]
        for px, py, pz, w, h, d in limbs:
            glPushMatrix()
            glTranslatef(px, py, pz)
            glColor3f(0.4, 0.3, 0.8)
            glScalef(w, h, d)
            glutSolidCube(1)
            glPopMatrix()

        # Nose
        glPushMatrix()
        glTranslatef(0.3, 0, 0.8)
        glColor3f(1, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidCone(0.05, 0.1, 10, 2)
        glPopMatrix()

        glPopMatrix()
    else:
        # Draw gun in first person view
        glPushMatrix()
        glTranslatef(0.5, -0.5, -0.5)  # Position the gun in the lower right
        glRotatef(-10, 1, 0, 0)  # Tilt the gun slightly
        
        # Gun body
        glPushMatrix()
        glColor3f(0.3, 0.3, 0.3)
        glScalef(0.5, 0.1, 0.1)
        glutSolidCube(1)
        glPopMatrix()
        
        # Gun barrel
        glPushMatrix()
        glTranslatef(0.5, 0, 0)
        glColor3f(0.2, 0.2, 0.2)
        glScalef(0.5, 0.05, 0.05)
        glutSolidCube(1)
        glPopMatrix()
        
        # Gun handle
        glPushMatrix()
        glTranslatef(0, 0, -0.1)
        glColor3f(0.4, 0.4, 0.4)
        glScalef(0.2, 0.15, 0.2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPopMatrix()

def draw_enemies():
    for enemy in enemies:
        if not enemy['active']:
            continue
            
        # Update enemy scale for pulsing effect
        enemy['scale'] += enemy['scale_dir']
        if enemy['scale'] > 1.2 or enemy['scale'] < 0.8:
            enemy['scale_dir'] = -enemy['scale_dir']
        
        glPushMatrix()
        glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['pos'][2])
        
        # Body
        glPushMatrix()
        glColor3f(1.0, 0.0, 0.0)
        glScalef(enemy['scale'], enemy['scale'], enemy['scale'])
        glutSolidSphere(10, 20, 20)
        glPopMatrix()
        
        # Head
        glPushMatrix()
        glTranslatef(0, 0, 15)
        glColor3f(0.0, 0.0, 0.0)
        glScalef(enemy['scale'], enemy['scale'], enemy['scale'])
        glutSolidSphere(6, 20, 20)
        glPopMatrix()
        
        glPopMatrix()

def draw_bullets():
    current_time = time.time()
    glColor3f(0.0, 0.0, 1.0)  # Blue bullets
    
    for bullet in bullets[:]:
        # Calculate new position
        time_elapsed = current_time - bullet['time']
        distance_traveled = bullet_speed * time_elapsed
        
        # Check if bullet has exceeded max range
        if distance_traveled > 500:  # Max range of 500 units
            bullets.remove(bullet)
            continue
            
        # Calculate new position
        bullet_x = bullet['start'][0] + bullet['direction'][0] * distance_traveled
        bullet_y = bullet['start'][1] + bullet['direction'][1] * distance_traveled
        bullet_z = bullet['start'][2] + bullet['direction'][2] * distance_traveled
        
        # Update bullet position
        bullet['pos'] = [bullet_x, bullet_y, bullet_z]
        
        # Draw bullet
        glPushMatrix()
        glTranslatef(bullet_x, bullet_y, bullet_z)
        glutSolidSphere(bullet_radius, 10, 10)
        glPopMatrix()

def draw_diamond():
    if not diamond_found:
        glPushMatrix()
        glTranslatef(diamond_pos[0], diamond_pos[1], player_pos[2])
        glColor3f(0.0, 0.7, 1.0)
        glRotatef(45, 1, 0, 0)
        glRotatef(45, 0, 1, 0)
        glScalef(15, 15, 30)
        glutSolidOctahedron()
        glPopMatrix()


def draw_big_ball():
    if not big_ball_active:
        return
        
    glPushMatrix()
    glTranslatef(big_ball_pos[0], big_ball_pos[1], big_ball_pos[2])
    glColor3f(1.0, 0.5, 0.0)  # Orange color
    glutSolidSphere(big_ball_radius, 30, 30)
    glPopMatrix()


def update_enemy_positions():
    if game_over:
        return
        
    for enemy in enemies:
        if not enemy['active']:
            continue
            
        # If enemy can see player, move toward player
        if can_see_player(enemy):
            px, py, pz = player_pos
            ex, ey, ez = enemy['pos']
            
            dx = px - ex
            dy = py - ey
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                dx = dx / distance * enemy['speed']
                dy = dy / distance * enemy['speed']
                
                new_x = ex + dx
                new_y = ey + dy
                
                if not is_collision(new_x, new_y):
                    enemy['pos'][0] = new_x
                    enemy['pos'][1] = new_y

def update_game_time():
    global game_time, game_over, first_person
    
    elapsed = time.time() - game_start_time
    remaining = max(0, 180 - int(elapsed))
    game_time = remaining
    
    if game_time <= 0:
        game_over = True
    
    if not first_person and elapsed >= auto_camera_switch_time:
        first_person = True

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    # Draw floor
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.5, 0.2)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    draw_maze()
    draw_diamond()
    draw_player()
    draw_enemies()
    draw_bullets()
    draw_big_ball()
    draw_position_markers()

    # HUD
    draw_text(10, 770, f"Time Remaining: {game_time} sec")
    draw_text(10, 740, f"Lives: {lives}")
    draw_text(10, 710, f"Questions left: {MAX_QUESTIONS - questions_answered}")
    draw_text(10, 680, f"Enemies left: {sum(1 for e in enemies if e['active'])}")
    draw_text(10, 650, f"Big Ball: {'Active' if big_ball_active else f'Respawning in {max(0, big_ball_respawn_delay - (time.time() - big_ball_respawn_timer)):.1f}s'}")
    
    if show_map_view:
        remaining = max(0, MAP_VIEW_DURATION - (time.time() - map_view_start_time))
        draw_text(10, 620, f"Map view: {int(remaining)}s remaining")
    
    if game_over:
        if diamond_found:
            draw_text(400, 400, "CONGRATULATIONS! YOU WON!", GLUT_BITMAP_TIMES_ROMAN_24)
        elif lives <= 0:
            draw_text(400, 400, "GAME OVER! YOU LOST!", GLUT_BITMAP_TIMES_ROMAN_24)
        else:
            draw_text(400, 400, "TIME'S UP! GAME OVER!", GLUT_BITMAP_TIMES_ROMAN_24)
    
    if cheat_mode:
        draw_text(10, 590, "CHEAT MODE: ON")
    
    draw_question()

    glutSwapBuffers()