import cv2
import mediapipe as mp
import pygame
import os
import time

# ========== Mediapipe Setup ==========
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# ========== Pygame Setup ==========
pygame.init()
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Agri-Bot Simulation")

bot_speed = 3

# ========== Field Setup ==========
FIELD_X, FIELD_Y = 50, 50
FIELD_WIDTH, FIELD_HEIGHT = 500, 300
FIELD_COLOR = (144, 238, 144)       # light green for field
CROP_UNPLOWED_COLOR = (210, 180, 140)
CROP_PLOWED_COLOR = (139, 69, 19)
CROP_SEEDED_COLOR = (34, 139, 34)
CROP_WATERED_COLOR = (0, 100, 255)

# ========== Crops Setup ==========
CROP_RADIUS = 8
CROP_SPACING_X = 50
CROP_SPACING_Y = 50
CROP_COLS = int((FIELD_WIDTH - 20) // CROP_SPACING_X)
CROP_ROWS = int((FIELD_HEIGHT - 20) // CROP_SPACING_Y)

crops = []
for i in range(CROP_ROWS):
    row = []
    for j in range(CROP_COLS):
        x = FIELD_X + 20 + j * CROP_SPACING_X
        y = FIELD_Y + 20 + i * CROP_SPACING_Y
        row.append({
            "pos": (x, y),
            "plowed": False,
            "seeded": False,
            "watered": False,
            "water_time": 0,
            "grown": False
        })
    crops.append(row)

# ========== Bot Setup ==========
bot_x = FIELD_X + 20
bot_y = FIELD_Y + FIELD_HEIGHT - 20

if os.path.exists("bot.jpeg"):
    bot_image = pygame.image.load("bot.jpeg")
    bot_image = pygame.transform.scale(bot_image, (40, 40))
else:
    bot_image = None

# ========== Camera ==========
cap = cv2.VideoCapture(0)

# ========== Gesture Helper Functions ==========
def is_fist(landmarks):
    finger_tips = [8, 12, 16, 20]
    finger_knuckles = [5, 9, 13, 17]
    folded = 0
    for tip, knuckle in zip(finger_tips, finger_knuckles):
        if landmarks[tip].y > landmarks[knuckle].y:
            folded += 1
    return folded == 4

def is_open_palm(landmarks):
    finger_tips = [8, 12, 16, 20]
    finger_knuckles = [5, 9, 13, 17]
    extended = 0
    for tip, knuckle in zip(finger_tips, finger_knuckles):
        if landmarks[tip].y < landmarks[knuckle].y:
            extended += 1
    return extended == 4

def thumb_direction(landmarks, handedness):
    thumb_tip = landmarks[4].x
    thumb_base = landmarks[2].x
    if handedness == "Right" and thumb_tip > thumb_base:
        return "Right"
    elif handedness == "Left" and thumb_tip < thumb_base:
        return "Left"
    return None

def is_index_down(landmarks):
    tip = landmarks[8]
    pip = landmarks[6]
    mcp = landmarks[5]
    vertical_straight = abs(tip.x - mcp.x) < 0.1
    return tip.y > pip.y and vertical_straight

def is_index_up(landmarks):
    tip = landmarks[8]
    pip = landmarks[6]
    mcp = landmarks[5]
    vertical_straight = abs(tip.x - mcp.x) < 0.1
    other_fingers_folded = (landmarks[12].y > landmarks[10].y and
                            landmarks[16].y > landmarks[14].y and
                            landmarks[20].y > landmarks[18].y)
    return tip.y < pip.y and vertical_straight and other_fingers_folded

def is_pinky_up(landmarks):
    tip = landmarks[20]
    pip = landmarks[18]
    mcp = landmarks[17]
    vertical_straight = abs(tip.x - mcp.x) < 0.1
    other_fingers_folded = (landmarks[8].y > landmarks[6].y and
                            landmarks[12].y > landmarks[10].y and
                            landmarks[16].y > landmarks[14].y)
    return tip.y < pip.y and vertical_straight and other_fingers_folded

def is_peace_sign(landmarks):
    fingers_extended = landmarks[8].y < landmarks[6].y and landmarks[12].y < landmarks[10].y
    fingers_folded = landmarks[16].y > landmarks[14].y and landmarks[20].y > landmarks[18].y
    return fingers_extended and fingers_folded

# ========== Activity Flags ==========
plowing = False
seeding = False
watering = False
water_drops = []

# ========== Main Loop ==========
running = True
while running:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = "None"

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, hand_label in zip(result.multi_hand_landmarks, result.multi_handedness):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark
            handedness = hand_label.classification[0].label

            # ===== Plowing =====
            if handedness == "Right" and is_index_up(landmarks):
                plowing = True
                cv2.putText(frame, "Plowing Started 🔨", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif handedness == "Left" and is_index_up(landmarks):
                plowing = False
                cv2.putText(frame, "Plowing Stopped ✋", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # ===== Seeding =====
            if handedness == "Right" and is_pinky_up(landmarks):
                seeding = True
                cv2.putText(frame, "Seeding Started 🌱", (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 2)
            elif handedness == "Left" and is_pinky_up(landmarks):
                seeding = False
                cv2.putText(frame, "Seeding Stopped ✋", (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 128), 2)

            # ===== Movement =====
            if is_fist(landmarks):
                direction = thumb_direction(landmarks, handedness)
                if direction == "Right":
                    gesture = "Right"
                elif direction == "Left":
                    gesture = "Left"
                else:
                    gesture = "Stop"
            elif is_open_palm(landmarks):
                gesture = "Forward"
            elif is_index_down(landmarks):
                gesture = "Down"
            elif is_peace_sign(landmarks):
                if handedness == "Right":
                    watering = True
                    cv2.putText(frame, "Watering Started 💧", (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 128), 2)
                elif handedness == "Left":
                    watering = False
                    cv2.putText(frame, "Watering Stopped ✋", (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 128), 2)

    # ===== Pygame Events =====
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ===== Draw Sky and Field =====
    win.fill((135, 206, 235))  # sky
    pygame.draw.rect(win, FIELD_COLOR, (FIELD_X, FIELD_Y, FIELD_WIDTH, FIELD_HEIGHT))

    # ===== Draw Crops =====
    for row in crops:
        for crop in row:
            x, y = crop["pos"]
            # Base color
            color = CROP_PLOWED_COLOR if crop["plowed"] else CROP_UNPLOWED_COLOR
            pygame.draw.circle(win, color, (x, y), CROP_RADIUS)
            pygame.draw.rect(win, (139, 69, 19), (x-2, y, 4, 8))  # stem

            # Seeded but not watered → small green dot (sapling)
            if crop["seeded"] and not crop["grown"]:
                pygame.draw.circle(win, CROP_SEEDED_COLOR, (x, y-10), 4)

            # Watered → grow tree
            if crop["watered"]:
                crop["grown"] = True
                pygame.draw.rect(win, (101, 67, 33), (x-3, y-10, 6, 10))  # trunk
                pygame.draw.polygon(win, CROP_SEEDED_COLOR, [(x, y-20), (x-8, y-10), (x+8, y-10)])  # canopy

    # ===== Move Bot =====
    if gesture == "Forward" and bot_y - bot_speed > FIELD_Y:
        bot_y -= bot_speed
    elif gesture == "Down" and bot_y + bot_speed < FIELD_Y + FIELD_HEIGHT:
        bot_y += bot_speed
    elif gesture == "Right" and bot_x + bot_speed < FIELD_X + FIELD_WIDTH:
        bot_x += bot_speed
    elif gesture == "Left" and bot_x - bot_speed > FIELD_X:
        bot_x -= bot_speed

    # ===== Plowing =====
    if plowing:
        for row in crops:
            for crop in row:
                cx, cy = crop["pos"]
                if abs(bot_x - cx) < bot_speed + 5 and abs(bot_y - cy) < bot_speed + 5:
                    crop["plowed"] = True

    # ===== Seeding =====
    if seeding:
        for row in crops:
            for crop in row:
                if crop["plowed"] and not crop["seeded"]:
                    cx, cy = crop["pos"]
                    if abs(bot_x - cx) < bot_speed + 5 and abs(bot_y - cy) < bot_speed + 5:
                        crop["seeded"] = True

    # ===== Watering =====
    if watering:
        water_drops.append([bot_x, bot_y])
    for drop in water_drops[:]:
        drop[1] += 5
        for row in crops:
            for crop in row:
                cx, cy = crop["pos"]
                if abs(drop[0] - cx) < 10 and abs(drop[1] - cy) < 10:
                    crop["watered"] = True
                    crop["water_time"] = time.time()
        if drop[1] > FIELD_Y + FIELD_HEIGHT:
            water_drops.remove(drop)
    for drop in water_drops:
        pygame.draw.circle(win, (30, 144, 255), (drop[0], drop[1]), 6)

    # ===== Draw Bot =====
    if bot_image:
        win.blit(bot_image, (bot_x - 20, bot_y - 20))
    else:
        pygame.draw.circle(win, (0, 255, 0), (bot_x, bot_y), 20)

    pygame.display.update()
    cv2.imshow("Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
