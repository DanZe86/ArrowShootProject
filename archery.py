import math
import turtle

G = 9.81

dt = 0.02
SCALE = 40
MAX_EXTRA_X = 5.0

v0 = 22.0
x0, y0 = 0.5, 1.5

target_x = 20.0
target_y = 3.5
target_r = 0.35

R1 = target_r / 3
R2 = 2 * target_r / 3

ANGLE_MIN = 0
ANGLE_MAX = 60
SLIDER_X_MIN = -300
SLIDER_X_MAX = 300
SLIDER_Y = -280

angle_deg = 18.0

screen = turtle.Screen()
screen.title("Archery target: angle slider + space to shoot")
screen.setup(width=1100, height=700)
screen.bgcolor("white")


def to_screen(x_m: float, y_m: float) -> tuple[float, float]:
    offset_x = -500
    offset_y = -240
    return (x_m * SCALE + offset_x, y_m * SCALE + offset_y)


def score_for_vertical_deviation(dy: float) -> int:
    if dy <= R1:
        return 10
    elif dy <= R2:
        return 5
    elif dy <= target_r:
        return 1
    else:
        return 0


def compute_trajectory(angle_deg_local: float) -> list[tuple[float, float]]:
    a = math.radians(angle_deg_local)
    vx = v0 * math.cos(a)
    vy0 = v0 * math.sin(a)

    t = 0.0
    traj = [(x0, y0)]

    while True:
        t += dt
        x = x0 + vx * t
        y = y0 + vy0 * t - 0.5 * G * t * t
        traj.append((x, y))

        if y <= 0:
            break
        if x > target_x + MAX_EXTRA_X:
            break

    return traj


def hit_side_target(
    traj: list[tuple[float, float]]
) -> tuple[bool, float, float, tuple[float, float] | None, int, int | None]:
    for i in range(1, len(traj)):
        x0p, y0p = traj[i - 1]
        x1p, y1p = traj[i]

        if x0p <= target_x <= x1p:
            if x1p == x0p:
                y_at = y1p
            else:
                t = (target_x - x0p) / (x1p - x0p)
                y_at = y0p + t * (y1p - y0p)

            dy = abs(y_at - target_y)
            hit = (target_y - target_r) <= y_at <= (target_y + target_r)
            pts = score_for_vertical_deviation(dy) if hit else 0

            return hit, y_at, dy, ((target_x, y_at) if hit else None), i, pts

    return False, float("nan"), float("inf"), None, -1, None


static_pen = turtle.Turtle()
static_pen.hideturtle()
static_pen.speed(0)


def draw_ground():
    static_pen.pensize(3)
    static_pen.color("black")
    static_pen.up()
    static_pen.goto(-520, -240)
    static_pen.down()
    static_pen.forward(1040)


def draw_side_target():
    cx, cy = to_screen(target_x, target_y)
    _, y_top = to_screen(target_x, target_y + target_r)
    _, y_bot = to_screen(target_x, target_y - target_r)

    static_pen.color("green")
    static_pen.pensize(8)
    static_pen.up()
    static_pen.goto(cx, y_bot)
    static_pen.down()
    static_pen.goto(cx, y_top)

    static_pen.up()
    static_pen.goto(cx, cy)
    static_pen.dot(8, "green")

    static_pen.pensize(2)
    for dy in (R1, R2):
        _, y1 = to_screen(target_x, target_y + dy)
        _, y2 = to_screen(target_x, target_y - dy)
        static_pen.up()
        static_pen.goto(cx - 15, y1)
        static_pen.down()
        static_pen.goto(cx + 15, y1)
        static_pen.up()
        static_pen.goto(cx - 15, y2)
        static_pen.down()
        static_pen.goto(cx + 15, y2)


info = turtle.Turtle()
info.hideturtle()
info.up()


def render_info(text: str):
    info.clear()
    info.goto(-520, 300)
    info.write(text, font=("Arial", 14, "normal"))


slider_line = turtle.Turtle()
slider_line.hideturtle()
slider_line.speed(0)

handle = turtle.Turtle()
handle.shape("circle")
handle.color("blue")
handle.shapesize(0.9)
handle.up()
handle.speed(0)

slider_label = turtle.Turtle()
slider_label.hideturtle()
slider_label.up()
slider_label.speed(0)


def x_to_angle(x: float) -> float:
    x = max(SLIDER_X_MIN, min(SLIDER_X_MAX, x))
    return ANGLE_MIN + (x - SLIDER_X_MIN) / (SLIDER_X_MAX - SLIDER_X_MIN) * (ANGLE_MAX - ANGLE_MIN)


def angle_to_x(a: float) -> float:
    a = max(ANGLE_MIN, min(ANGLE_MAX, a))
    return SLIDER_X_MIN + (a - ANGLE_MIN) / (ANGLE_MAX - ANGLE_MIN) * (SLIDER_X_MAX - SLIDER_X_MIN)


def update_slider_ui():
    slider_label.clear()
    slider_label.goto(-60, SLIDER_Y + 18)
    slider_label.write(f"Angle α: {angle_deg:.1f}°", font=("Arial", 12, "normal"))
    handle.goto(angle_to_x(angle_deg), SLIDER_Y)


def on_drag_handle(x, y):
    global angle_deg

    handle.ondrag(None)

    x = max(SLIDER_X_MIN, min(SLIDER_X_MAX, x))
    handle.setx(x)
    handle.sety(SLIDER_Y)

    angle_deg = x_to_angle(x)

    slider_label.clear()
    slider_label.goto(-60, SLIDER_Y + 18)
    slider_label.write(f"Angle α: {angle_deg:.1f}°", font=("Arial", 12, "normal"))

    render_info(f"Angle α = {angle_deg:.1f}° | SPACE = shoot | C = clear")

    handle.ondrag(on_drag_handle)


def draw_slider():
    slider_line.pensize(5)
    slider_line.color("gray")
    slider_line.up()
    slider_line.goto(SLIDER_X_MIN, SLIDER_Y)
    slider_line.down()
    slider_line.goto(SLIDER_X_MAX, SLIDER_Y)

    slider_line.up()
    slider_line.goto(SLIDER_X_MIN, SLIDER_Y - 25)
    slider_line.write(f"{ANGLE_MIN}°", font=("Arial", 10, "normal"))

    slider_line.goto(SLIDER_X_MAX - 30, SLIDER_Y - 25)
    slider_line.write(f"{ANGLE_MAX}°", font=("Arial", 10, "normal"))

    handle.ondrag(on_drag_handle)
    update_slider_ui()


shot_pen = turtle.Turtle()
shot_pen.hideturtle()
shot_pen.speed(0)

marker = turtle.Turtle()
marker.hideturtle()
marker.speed(0)
marker.up()


def clear_shot():
    shot_pen.clear()
    marker.clear()
    render_info(f"Angle α = {angle_deg:.1f}° | SPACE = shoot | C = clear")


def draw_hit_marker(x_m: float, y_m: float):
    marker.clear()
    sx, sy = to_screen(x_m, y_m)
    marker.goto(sx, sy)
    marker.dot(10, "black")


def draw_trajectory_to_side_target(
    traj: list[tuple[float, float]],
    cross_index: int,
    hit_point: tuple[float, float] | None,
    color="brown",
):
    shot_pen.color(color)
    shot_pen.pensize(2)

    if cross_index == -1 or hit_point is None:
        first = True
        for (x, y) in traj:
            sx, sy = to_screen(x, y)
            if first:
                shot_pen.up()
                shot_pen.goto(sx, sy)
                shot_pen.down()
                first = False
            else:
                shot_pen.goto(sx, sy)
        return

    first = True
    for i, (x, y) in enumerate(traj):
        if i > cross_index - 1:
            break
        sx, sy = to_screen(x, y)
        if first:
            shot_pen.up()
            shot_pen.goto(sx, sy)
            shot_pen.down()
            first = False
        else:
            shot_pen.goto(sx, sy)

    hx, hy = hit_point
    hsx, hsy = to_screen(hx, hy)
    shot_pen.goto(hsx, hsy)


def shoot():
    clear_shot()
    traj = compute_trajectory(angle_deg)

    hit, y_at, dy, hit_point, cross_index, pts = hit_side_target(traj)

    draw_trajectory_to_side_target(
        traj,
        cross_index=cross_index if hit else -1,
        hit_point=hit_point if hit else None,
        color="brown",
    )

    if hit and hit_point is not None:
        draw_hit_marker(hit_point[0], hit_point[1])
        result = "HIT ✅"
        y_text = f"{y_at:.3f}"
        dy_text = f"{dy:.3f}"
        pts_text = f"{pts}"
    else:
        result = "MISS ❌"
        y_text = "—"
        dy_text = "—"
        pts_text = "0"

    render_info(
        f"α={angle_deg:.1f}° | {result} | y@target={y_text} m | dy={dy_text} m | pts={pts_text} | SPACE=shoot | C=clear"
    )


def init():
    draw_ground()
    draw_side_target()
    draw_slider()
    render_info(f"Angle α = {angle_deg:.1f}° | SPACE = shoot | C = clear")

    screen.listen()
    screen.onkeypress(shoot, "space")
    screen.onkeypress(clear_shot, "c")


init()
turtle.done()
