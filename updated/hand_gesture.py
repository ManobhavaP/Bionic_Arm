import cv2
import mediapipe as mp
import math
import socket

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    angle = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
    return angle + 360 if angle < 0 else angle

# Function to update hand state
def update_hand_state(hand_landmarks):
    thumb_angle = calculate_angle([hand_landmarks[2].x, hand_landmarks[2].y],
                                  [hand_landmarks[3].x, hand_landmarks[3].y],
                                  [hand_landmarks[4].x, hand_landmarks[4].y])
    index_angle = calculate_angle([hand_landmarks[5].x, hand_landmarks[5].y],
                                  [hand_landmarks[6].x, hand_landmarks[6].y],
                                  [hand_landmarks[8].x, hand_landmarks[8].y])
    middle_angle = calculate_angle([hand_landmarks[9].x, hand_landmarks[9].y],
                                   [hand_landmarks[10].x, hand_landmarks[10].y],
                                   [hand_landmarks[12].x, hand_landmarks[12].y])
    ring_angle = calculate_angle([hand_landmarks[13].x, hand_landmarks[13].y],
                                 [hand_landmarks[14].x, hand_landmarks[14].y],
                                 [hand_landmarks[16].x, hand_landmarks[16].y])
    pinky_angle = calculate_angle([hand_landmarks[17].x, hand_landmarks[17].y],
                                  [hand_landmarks[18].x, hand_landmarks[18].y],
                                  [hand_landmarks[20].x, hand_landmarks[20].y])

    thumb_bent = 1 if thumb_angle > 150 else 0
    index_bent = 1 if index_angle > 150 else 0
    middle_bent = 1 if middle_angle > 150 else 0
    ring_bent = 1 if ring_angle > 150 else 0
    pinky_bent = 1 if pinky_angle > 150 else 0

    return [thumb_bent, index_bent, middle_bent, ring_bent, pinky_bent]

# Set up socket communication
host = '192.168.223.40'  # Replace with your Pico W IP address
port = 8080
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Initialize Mediapipe and OpenCV
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    # Convert the BGR image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            hand_state = update_hand_state(hand_landmarks.landmark)
            state_string = ','.join([str(state) for state in hand_state])
            print(f"Sending hand state: {state_string}")  # Print the hand state being sent
            client_socket.send((state_string + '\n').encode())
    
    cv2.imshow('Hand Tracking', frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()
