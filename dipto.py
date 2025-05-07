# Timer variables
game_start_time = 0
game_time = 180
game_over = False
auto_camera_switch_time = 3
enemy_start_time = 6
bullets = []
bullet_speed = 60
bullet_radius = 1
last_shot_time = 0
shot_cooldown = 0.5

# Map view variables
show_map_view = False
map_view_start_time = 0
MAP_VIEW_DURATION = 5
player_start_pos = [0, 0, 10]

def update_big_ball():
    global big_ball_active, big_ball_spawned, big_ball_pos
    global big_ball_spawn_timer, big_ball_respawn_timer
    global lives, player_pos, game_over

    current_time = time.time()

    # Spawn after initial delay
    if not big_ball_spawned:
        if current_time - game_start_time >= big_ball_spawn_delay:
            big_ball_spawned = True
            big_ball_active = True
            big_ball_pos = [player_start_pos[0], player_start_pos[1], 50]
        return

    # Handle respawn after hit
    if not big_ball_active:
        if current_time - big_ball_respawn_timer >= big_ball_respawn_delay:
            big_ball_active = True
            # Spawn near player but not too close
            angle = random.uniform(0, 2*math.pi)
            distance = random.uniform(100, 200)
            big_ball_pos = [
                player_pos[0] + distance * math.cos(angle),
                player_pos[1] + distance * math.sin(angle),
                50
            ]
        return

    # Movement logic - REMOVED WALL COLLISION CHECK
    px, py, _ = player_pos
    bx, by, _ = big_ball_pos
    dx = px - bx
    dy = py - by
    distance = math.sqrt(dx * dx + dy * dy)

    if distance > 0:
        dx = dx / distance * big_ball_speed
        dy = dy / distance * big_ball_speed
        # Simply update position without collision check
        big_ball_pos[0] += dx
        big_ball_pos[1] += dy

    # Collision with player
    if distance < big_ball_radius + 15:
        lives -= 1
        big_ball_active = False
        big_ball_respawn_timer = current_time

        if lives <= 0:
            game_over = True
        else:
            angle = math.atan2(py - by, px - bx)
            player_pos[0] = bx + (big_ball_radius + 20) * math.cos(angle)
            player_pos[1] = by + (big_ball_radius + 20) * math.sin(angle)


def check_diamond_collision():
    global diamond_found, game_over
    if not diamond_found:
        px, py, pz = player_pos
        dx, dy, dz = diamond_pos
        distance = math.sqrt((px - dx) ** 2 + (py - dy) ** 2)
        if distance < 20:
            diamond_found = True
            game_over = True
def check_enemy_collision():
    global lives, game_over
    
    px, py, pz = player_pos
    
    for enemy in enemies:
        if not enemy['active']:
            continue
            
        ex, ey, ez = enemy['pos']
        distance = math.sqrt((px - ex) ** 2 + (py - ey) ** 2)
        
        if distance < 20:
            lives -= 1
            angle = math.atan2(ey - py, ex - px)
            enemy['pos'][0] = px + 50 * math.cos(angle)
            enemy['pos'][1] = py + 50 * math.sin(angle)
            
            if lives <= 0:
                game_over = True
            break

def check_bullet_collisions():
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if not enemy['active']:
                continue
                
            bx, by, bz = bullet['pos']
            ex, ey, ez = enemy['pos']
            distance = math.sqrt((bx - ex) ** 2 + (by - ey) ** 2 + (bz - ez) ** 2)
            
            if distance < 15:  # Bullet hit enemy
                enemy['active'] = False
                if bullet in bullets:
                    bullets.remove(bullet)
                break
def update_bullets():
    current_time = time.time()
    
    # Remove bullets that have traveled too far
    for bullet in bullets[:]:
        time_elapsed = current_time - bullet['time']
        if time_elapsed * bullet_speed > 500:  # Max range
            bullets.remove(bullet)

def shoot_bullet():
    global last_shot_time
    
    current_time = time.time()
    if current_time - last_shot_time < shot_cooldown:
        return
        
    last_shot_time = current_time
    
    # Calculate bullet direction based on player angle
    angle_rad = math.radians(player_angle)
    direction = (
        math.cos(angle_rad),
        math.sin(angle_rad),
        0  # Flat trajectory
    )
    
    # Start bullet slightly in front of player
    start_pos = (
        player_pos[0] + direction[0] * 10,
        player_pos[1] + direction[1] * 10,
        player_pos[2] + 5  # Gun height
    )
    
    bullets.append({
        'start': start_pos,
        'pos': list(start_pos),
        'direction': direction,
        'time': current_time
    })
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    if show_map_view or top_down_view:
        glOrtho(-GRID_LENGTH/2, GRID_LENGTH/2, -GRID_LENGTH/2, GRID_LENGTH/2, -1000, 1000)
    elif first_person:
        gluPerspective(90, 1.25, 0.1, 1500)
    else:
        gluPerspective(fovY, 1.25, 0.1, 1500)
        
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if show_map_view or top_down_view:
        gluLookAt(0, 0, 1000, 0, 0, 0, 0, 1, 0)
    elif first_person:
        x, y, z = player_pos
        forward_x = math.cos(math.radians(player_angle))
        forward_y = math.sin(math.radians(player_angle))
        gluLookAt(x, y, z + 5, x + forward_x, y + forward_y, z + 5, 0, 0, 1)
    else:
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def update():
    global top_down_view, top_down_view_time, show_map_view, map_view_start_time
    
    if not game_over:
        update_game_time()
        update_enemy_positions()
        update_bullets()
        update_big_ball()
        check_enemy_collision()
        check_bullet_collisions()
        check_diamond_collision()
            
    if top_down_view and time.time() - top_down_view_time > TOP_DOWN_VIEW_DURATION:
        top_down_view = False
        
    if show_map_view and time.time() - map_view_start_time > MAP_VIEW_DURATION:
        show_map_view = False
        
    glutPostRedisplay()

def main():
    global game_start_time, mouse_x, mouse_y
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Maze Diamond Hunter")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMotionFunc(mouseMotionListener)
    glutPassiveMotionFunc(mouseMotionListener)
    glutEntryFunc(enterMouseListener)
    glutIdleFunc(update)
    
    mouse_x = glutGet(GLUT_WINDOW_WIDTH) // 2
    mouse_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
    
    game_start_time = time.time()

    glutMainLoop()

if __name__ == "__main__":
    main()