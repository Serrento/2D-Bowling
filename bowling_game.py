import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window Dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Game States
start_screen = True
pause = False
game_over = False
win_flag = False

# Score & Round Tries State
current_score = 0
highest_score = 0
MAX_TRIES = 3
tries_left = MAX_TRIES

# Ball State
ball_x = 640.0
ball_y = 50.0
ball_radius = 15.0
ball_vx = 0.0
ball_vy = 0.0
spin = 0.0  # Curve/spin effect
is_launched = False

# Power Meter State
power_level = 0.0
power_direction = 1.0
is_charging = False

# Pin Representation: [x, y, radius, is_standing]
PINS_START_Y = 550.0
pins = []


def init_pins():
    """Initializes pins in a standard 10-pin triangle formation."""
    global pins
    pins = []
    rows = 4
    spacing_x = 35.0
    spacing_y = 40.0
    start_x = 640.0

    for row in range(rows):
        y = PINS_START_Y + row * spacing_y
        row_count = row + 1
        x_offset = start_x - (row_count - 1) * (spacing_x / 2.0)
        for col in range(row_count):
            x = x_offset + col * spacing_x
            pins.append([x, y, 12.0, True])


def draw_pixel(x, y):
    """Utility to render integer coordinates as OpenGL points."""
    glBegin(GL_POINTS)
    glVertex2i(int(x), int(y))
    glEnd()


def draw_line(x1, y1, x2, y2):
    """Midpoint line algorithm implementation."""
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy
    cx, cy = x1, y1

    while True:
        draw_pixel(cx, cy)
        if cx == x2 and cy == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy


def draw_circle(cx, cy, r):
    """Midpoint circle algorithm implementation."""
    cx, cy, r = int(cx), int(cy), int(r)
    x = 0
    y = r
    d = 1 - r

    def plot_symmetric(px, py):
        draw_pixel(cx + px, cy + py)
        draw_pixel(cx - px, cy + py)
        draw_pixel(cx + px, cy - py)
        draw_pixel(cx - px, cy - py)
        draw_pixel(cx + py, cy + px)
        draw_pixel(cx - py, cy + px)
        draw_pixel(cx + py, cy - px)
        draw_pixel(cx - py, cy - px)

    plot_symmetric(x, y)
    while x < y:
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
        plot_symmetric(x, y)


def render_text(x, y, string):
    """Renders bitmap text using GLUT."""
    glRasterPos2f(x, y)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


def check_pin_collisions():
    """Detects collisions between ball and pins, updating score."""
    global pins, ball_x, ball_y, ball_radius, current_score, highest_score

    for pin in pins:
        if pin[3]:  # If standing
            dx = ball_x - pin[0]
            dy = ball_y - pin[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= (ball_radius + pin[2]):
                pin[3] = False  # Knock pin down
                current_score += 10
                if current_score > highest_score:
                    highest_score = current_score


def reset_ball_position():
    """Resets ball position and decrements attempts counter."""
    global ball_x, ball_y, ball_vx, ball_vy, spin, is_launched
    global is_charging, power_level, tries_left, game_over, win_flag

    is_launched = False
    is_charging = False
    power_level = 0.0
    spin = 0.0
    ball_x = 640.0
    ball_y = 50.0
    ball_vx = 0.0
    ball_vy = 0.0

    tries_left -= 1

    # Check game completion states
    all_down = all(not pin[3] for pin in pins)
    if all_down:
        win_flag = True
        game_over = True
    elif tries_left <= 0:
        win_flag = False
        game_over = True


def update_physics():
    """Handles game loop physics ticks."""
    global ball_x, ball_y, ball_vx, ball_vy, spin
    global is_launched, game_over, win_flag
    global power_level, power_direction, is_charging

    if start_screen or pause or game_over:
        return

    # Oscillate power meter while charging after 1st Spacebar tap
    if is_charging:
        power_level += power_direction * 2.5
        if power_level >= 100.0:
            power_level = 100.0
            power_direction = -1.0
        elif power_level <= 0.0:
            power_level = 0.0
            power_direction = 1.0

    # Ball movement & continuous spin acceleration
    if is_launched:
        ball_vx += spin * 0.04
        ball_x += ball_vx
        ball_y += ball_vy

        # Gutter collision reflection
        if ball_x - ball_radius <= 200 or ball_x + ball_radius >= 1080:
            ball_vx = -ball_vx * 0.5

        # Check collision with standing pins
        check_pin_collisions()

        # Friction drag
        ball_vx *= 0.985
        ball_vy *= 0.985

        if abs(ball_vx) < 0.05:
            ball_vx = 0.0
        if abs(ball_vy) < 0.05:
            ball_vy = 0.0

        # Reset launch state when ball stops or exits top lane boundary
        if (ball_vx == 0.0 and ball_vy == 0.0) or ball_y > 700:
            reset_ball_position()


def draw_lane():
    """Renders bowling lane boundaries and gutter lines."""
    glColor3f(0.5, 0.35, 0.1)
    draw_line(200, 0, 200, 720)
    draw_line(1080, 0, 1080, 720)

    # Gutter lines
    glColor3f(0.2, 0.2, 0.2)
    draw_line(220, 0, 220, 720)
    draw_line(1060, 0, 1060, 720)


def draw_pins():
    """Renders standing pins."""
    glColor3f(1.0, 1.0, 1.0)
    for pin in pins:
        if pin[3]:
            draw_circle(pin[0], pin[1], pin[2])


def draw_ball():
    """Renders bowling ball."""
    glColor3f(0.1, 0.5, 0.9)
    draw_circle(ball_x, ball_y, ball_radius)


def draw_trajectory_preview():
    """Renders visual hook indicator and projected arc trajectory path before launch."""
    if is_launched or game_over or start_screen:
        return

    glColor3f(1.0, 0.8, 0.0)
    sim_x = ball_x
    sim_y = ball_y
    sim_vx = 0.0
    sim_vy = 12.0

    for _ in range(25):
        sim_vx += spin * 0.04
        sim_x += sim_vx
        sim_y += sim_vy
        sim_vx *= 0.985
        sim_vy *= 0.985

        if 200 <= sim_x <= 1080 and sim_y <= PINS_START_Y + 120:
            draw_circle(sim_x, sim_y, 2)


def draw_power_bar():
    """Enhanced Power Bar gauge."""
    if is_launched or game_over or start_screen:
        return

    bar_x, bar_y = 1140, 200
    bar_w, bar_h = 30, 240

    # Outer Frame
    glColor3f(0.8, 0.8, 0.8)
    draw_line(bar_x - 2, bar_y - 2, bar_x + bar_w + 2, bar_y - 2)
    draw_line(bar_x - 2, bar_y + bar_h + 2, bar_x + bar_w + 2, bar_y + bar_h + 2)
    draw_line(bar_x - 2, bar_y - 2, bar_x - 2, bar_y + bar_h + 2)
    draw_line(bar_x + bar_w + 2, bar_y - 2, bar_x + bar_w + 2, bar_y + bar_h + 2)

    # Meter Ticks
    glColor3f(0.4, 0.4, 0.4)
    for pct in [0.25, 0.5, 0.75]:
        tick_y = bar_y + int(bar_h * pct)
        draw_line(bar_x - 8, tick_y, bar_x, tick_y)

    # Active Fill Height
    current_height = int((power_level / 100.0) * bar_h)

    for line_y in range(bar_y, bar_y + current_height):
        norm = (line_y - bar_y) / float(bar_h)
        r = min(1.0, norm * 2.0)
        g = min(1.0, (1.0 - norm) * 2.0)
        glColor3f(r, g, 0.1)
        draw_line(bar_x, line_y, bar_x + bar_w, line_y)

    # Text Overlay Label
    glColor3f(1.0, 1.0, 1.0)
    render_text(bar_x - 20, bar_y + bar_h + 15, f"POWER: {int(power_level)}%")


def draw_ui():
    """Renders scoreboard, remaining tries, and gameplay status."""
    glColor3f(1.0, 1.0, 1.0)
    render_text(30, 680, f"Score: {current_score}")
    render_text(30, 650, f"High Score: {highest_score}")
    render_text(30, 620, f"Tries Left: {tries_left}/{MAX_TRIES}")
    render_text(30, 590, f"Spin Curve: {spin:+.1f} (UP/DOWN)")

    if start_screen:
        glColor3f(1.0, 0.8, 0.0)
        render_text(480, 400, "BOWLING 2D GAME")
        render_text(400, 360, "1st SPACE: Start Power Meter | 2nd SPACE: Launch")
    elif pause:
        glColor3f(1.0, 0.0, 0.0)
        render_text(550, 400, "PAUSED")
    elif game_over:
        glColor3f(0.0, 1.0, 0.0) if win_flag else glColor3f(1.0, 0.0, 0.0)
        render_text(500, 400, "STRIKE! YOU CLEARED ALL PINS!" if win_flag else "OUT OF TRIES! GAME OVER")
        render_text(450, 360, "Press 'R' to Restart")

    draw_power_bar()


def display():
    """Main rendering pipeline."""
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    draw_lane()
    draw_pins()
    draw_trajectory_preview()
    draw_ball()
    draw_ui()

    glutSwapBuffers()


def idle():
    """Main execution tick."""
    update_physics()
    glutPostRedisplay()


def keyboard_listener(key, x, y):
    """Two-Tap Spacebar and menu control inputs."""
    global start_screen, pause, is_charging, is_launched, ball_vy, power_level

    if key == b" ":
        if start_screen:
            start_screen = False
        elif not game_over and not pause:
            if not is_launched and not is_charging:
                # 1st Tap: Start power charging oscillation
                is_charging = True
                power_level = 0.0
            elif is_charging:
                # 2nd Tap: Freeze power meter and shoot
                is_charging = False
                is_launched = True
                ball_vy = 6.0 + (power_level / 100.0) * 18.0

    elif key in (b"p", b"P"):
        pause = not pause

    elif key in (b"r", b"R"):
        reset_game()

    elif key in (b"q", b"Q", b"\x1b"):
        sys.exit(0)

    glutPostRedisplay()


def special_key_listener(key, x, y):
    """Handles positioning and spin inputs using arrow keys."""
    global ball_x, spin

    if not start_screen and not game_over and not pause:
        if not is_launched:
            if key == GLUT_KEY_RIGHT and ball_x < 1040:
                ball_x += 15
            elif key == GLUT_KEY_LEFT and ball_x > 240:
                ball_x -= 15
            elif key == GLUT_KEY_UP:
                spin = min(spin + 0.5, 3.0)
            elif key == GLUT_KEY_DOWN:
                spin = max(spin - 0.5, -3.0)
        else:
            if key == GLUT_KEY_UP:
                spin += 0.2
            elif key == GLUT_KEY_DOWN:
                spin -= 0.2

    glutPostRedisplay()


def reset_game():
    """Resets entire board and resets tries count back to 3."""
    global ball_x, ball_y, ball_vx, ball_vy, spin, is_launched
    global power_level, is_charging, power_direction
    global game_over, win_flag, current_score, tries_left

    ball_x = 640.0
    ball_y = 50.0
    ball_vx = 0.0
    ball_vy = 0.0
    spin = 0.0
    is_launched = False

    power_level = 0.0
    is_charging = False
    power_direction = 1.0

    tries_left = MAX_TRIES
    game_over = False
    win_flag = False
    current_score = 0
    init_pins()


def init():
    """Sets initial OpenGL 2D view and properties."""
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    init_pins()


def main():
    """Main execution entry point."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"PyOpenGL Bowling - 3 Tries Round System")

    init()

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)

    glutMainLoop()


if __name__ == "__main__":
    main()