import streamlit as st 
import cv2 
import mediapipe as mp    
import numpy as np 
import time
import math 
from collections import deque, Counter 
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration 
import av 
import asyncio 


st.set_page_config(
    page_title="Neural HandSense AI",
    page_icon="📸🧘🙌",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700&family=Exo+2:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Exo 2', sans-serif;
        transition: all 0.3s ease;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #8A2BE2 0%, #00BFFF 50%, #9370DB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: -0.5px;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 20px rgba(138, 43, 226, 0.5);
        animation: textGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes textGlow {
        0% { text-shadow: 0 0 10px rgba(138, 43, 226, 0.5); }
        100% { text-shadow: 0 0 25px rgba(138, 43, 226, 0.8), 0 0 35px rgba(0, 191, 255, 0.6); }
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
        position: relative;
    }
    
    .sub-header::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #8A2BE2, #00BFFF);
        border-radius: 3px;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #a0a0a0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }
    
    .metric-value {
        font-size: 1.6rem;
        color: #ffffff;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
    }
    
    .gesture-card {
        background: rgba(20, 20, 30, 0.6);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(138, 43, 226, 0.3);
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .gesture-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        z-index: -1;
        background: linear-gradient(45deg, #8A2BE2, #00BFFF, #9370DB, #8A2BE2);
        background-size: 400%;
        border-radius: 20px;
        animation: glowingBorder 3s linear infinite;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .gesture-card:hover::before {
        opacity: 1;
    }
    
    .gesture-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px rgba(138, 43, 226, 0.3);
        border: 1px solid rgba(138, 43, 226, 0.6);
    }
    
    @keyframes glowingBorder {
        0% { background-position: 0 0; }
        50% { background-position: 400% 0; }
        100% { background-position: 0 0; }
    }
    
    .glowing {
        background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(0, 191, 255, 0.2));
        border: 1px solid rgba(138, 43, 226, 0.5);
        box-shadow: 0 0 30px rgba(138, 43, 226, 0.4);
        animation: pulse 2s infinite;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a15 0%, #070710 100%);
        border-right: 1px solid rgba(138, 43, 226, 0.2);
        box-shadow: 5px 0 15px rgba(0, 0, 0, 0.3);
    }
    
    .help-text {
        color: #cccccc;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .stSlider > div > div {
        background: linear-gradient(90deg, #8A2BE2 0%, #00BFFF 100%);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.5);
    }
    
    .stSelectbox > div > div {
        background: rgba(30, 30, 45, 0.7);
        color: white;
        border-radius: 12px;
        border: 1px solid rgba(138, 43, 226, 0.3);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border: 1px solid rgba(138, 43, 226, 0.6);
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.3);
    }
    
    .stCheckbox > label {
        color: white;
        font-weight: 500;
        padding: 8px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stCheckbox > label:hover {
        background: rgba(138, 43, 226, 0.1);
        transform: translateX(5px);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #8A2BE2 0%, #00BFFF 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(138, 43, 226, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: all 0.6s ease;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(138, 43, 226, 0.5);
    }
    
    .tab-container {
        background: rgba(30, 30, 45, 0.7);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(138, 43, 226, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .tab-container:hover {
        border: 1px solid rgba(138, 43, 226, 0.4);
        box-shadow: 0 0 20px rgba(138, 43, 226, 0.2);
    }
    
    .fps-counter {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(10, 10, 20, 0.8);
        color: #00ff9d;
        padding: 8px 15px;
        border-radius: 20px;
        font-family: 'Orbitron', monospace;
        font-size: 0.9rem;
        font-weight: 600;
        border: 1px solid rgba(0, 255, 157, 0.3);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        animation: pulse 2s infinite;
    }
    
    .mode-indicator {
        position: absolute;
        top: 15px;
        left: 15px;
        background: rgba(10, 10, 20, 0.8);
        color: #8A2BE2;
        padding: 8px 15px;
        border-radius: 20px;
        font-family: 'Orbitron', monospace;
        font-size: 0.9rem;
        font-weight: 600;
        border: 1px solid rgba(138, 43, 226, 0.3);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { 
            box-shadow: 0 0 5px rgba(138, 43, 226, 0.4);
        }
        50% { 
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.8);
        }
        100% { 
            box-shadow: 0 0 5px rgba(138, 43, 226, 0.4);
        }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .icon-button {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 20px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(138, 43, 226, 0.2);
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        position: relative;
        overflow: hidden;
    }
    
    .icon-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, rgba(138, 43, 226, 0.1), rgba(0, 191, 255, 0.1));
        clip-path: circle(0% at 50% 50%);
        transition: all 0.4s ease;
    }
    
    .icon-button:hover::before {
        clip-path: circle(100% at 50% 50%);
    }
    
    .icon-button:hover {
        background: rgba(138, 43, 226, 0.1);
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(138, 43, 226, 0.2);
        border: 1px solid rgba(138, 43, 226, 0.4);
    }
    
    .stat-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        background: rgba(138, 43, 226, 0.15);
        color: #8A2BE2;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(138, 43, 226, 0.3);
        transition: all 0.3s ease;
    }
    
    .stat-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(138, 43, 226, 0.3);
        background: rgba(138, 43, 226, 0.25);
    }
    
    .dev-card {
        background: rgba(30, 30, 45, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(138, 43, 226, 0.3);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .dev-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(138, 43, 226, 0.1), rgba(0, 191, 255, 0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite linear;
        z-index: 0;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .dev-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(138, 43, 226, 0.25);
        border: 1px solid rgba(138, 43, 226, 0.5);
    }
    
    .project-card {
        background: rgba(30, 30, 45, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(138, 43, 226, 0.3);
        margin-bottom: 2rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .project-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #8A2BE2, #00BFFF);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.5s ease;
    }
    
    .project-card:hover::after {
        transform: scaleX(1);
    }
    
    .project-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 45px rgba(138, 43, 226, 0.3);
    }
    
    .social-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 10px 20px;
        border-radius: 25px;
        background: rgba(138, 43, 226, 0.1);
        color: #8A2BE2;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0.75rem;
        text-decoration: none;
        transition: all 0.3s ease;
        border: 1px solid rgba(138, 43, 226, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .social-badge::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, rgba(138, 43, 226, 0.2), rgba(0, 191, 255, 0.2));
        clip-path: circle(0% at 50% 50%);
        transition: all 0.4s ease;
        z-index: -1;
    }
    
    .social-badge:hover::before {
        clip-path: circle(100% at 50% 50%);
    }
    
    .social-badge:hover {
        background: rgba(138, 43, 226, 0.2);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 20px rgba(138, 43, 226, 0.3);
        color: #8A2BE2;
        border: 1px solid rgba(138, 43, 226, 0.5);
    }
    
    .tech-pill {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 25px;
        background: linear-gradient(45deg, rgba(138, 43, 226, 0.15), rgba(0, 191, 255, 0.15));
        color: #ffffff;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem;
        border: 1px solid rgba(138, 43, 226, 0.3);
        transition: all 0.3s ease;
    }
    
    .tech-pill:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(138, 43, 226, 0.3);
        background: linear-gradient(45deg, rgba(138, 43, 226, 0.25), rgba(0, 191, 255, 0.25));
    }
    
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    .gradient-border {
        border: double 3px transparent;
        border-radius: 20px;
        background-image: linear-gradient(rgba(20, 20, 30, 0.7), rgba(20, 20, 30, 0.7)), 
                          linear-gradient(45deg, #8A2BE2, #00BFFF, #9370DB);
        background-origin: border-box;
        background-clip: content-box, border-box;
        animation: borderGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes borderGlow {
        0% { box-shadow: 0 0 10px rgba(138, 43, 226, 0.3); }
        100% { box-shadow: 0 0 20px rgba(138, 43, 226, 0.6), 0 0 30px rgba(0, 191, 255, 0.4); }
    }
    
    .neon-text {
        text-shadow: 0 0 5px #8A2BE2, 0 0 10px #8A2BE2, 0 0 15px #8A2BE2;
        animation: textPulse 2s ease-in-out infinite alternate;
    }
    
    @keyframes textPulse {
        0% { text-shadow: 0 0 5px #8A2BE2, 0 0 10px #8A2BE2; }
        100% { text-shadow: 0 0 10px #8A2BE2, 0 0 20px #8A2BE2, 0 0 30px #00BFFF; }
    }
    
    .particle {
        position: absolute;
        background: rgba(138, 43, 226, 0.6);
        border-radius: 50%;
        filter: blur(5px);
        z-index: -1;
    }
    
    .glass-card {
        background: rgba(30, 30, 45, 0.5);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(138, 43, 226, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(138, 43, 226, 0.3);
        border: 1px solid rgba(138, 43, 226, 0.4);
    }
    
    /* Background animation */
    .bg-animation {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        overflow: hidden;
    }
    
    .bg-circle {
        position: absolute;
        border-radius: 50%;
        background: rgba(138, 43, 226, 0.1);
        animation: float 15s infinite ease-in-out;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 10, 20, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #8A2BE2, #00BFFF);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #9b50e0, #33ccff);
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="bg-animation">
    <div class="bg-circle" style="width: 300px; height: 300px; top: 10%; left: 10%; animation-delay: 0s;"></div>
    <div class="bg-circle" style="width: 200px; height: 200px; top: 70%; left: 80%; animation-delay: 2s;"></div>
    <div class="bg-circle" style="width: 250px; height: 250px; top: 30%; left: 75%; animation-delay: 4s;"></div>
    <div class="bg-circle" style="width: 150px; height: 150px; top: 60%; left: 15%; animation-delay: 6s;"></div>
    <div class="bg-circle" style="width: 100px; height: 100px; top: 20%; left: 50%; animation-delay: 8s;"></div>
</div>
""", unsafe_allow_html=True)


HAND_COLORS = {"Left": (0, 191, 255), "Right": (138, 43, 226)}
JOINT_COLOR = {"Straight": (0, 255, 160), "Bent": (255, 80, 80)}
VIOLET = (180, 70, 255)


DEFAULT_STRAIGHT_THRESH = 160
DEFAULT_THUMB_THRESH = 140
DEFAULT_SMOOTH_ALPHA = 0.6
DEFAULT_GESTURE_HISTORY = 10
DEFAULT_GESTURE_CONFIRM = 6
DEFAULT_DIST_OK_RATIO = 0.18

MODE_NORMAL = 0
MODE_GESTURE = 1
MODE_ANGLE = 2

GESTURE_PATTERNS = {
    "Fist": {"Thumb":"Bent","Index":"Bent","Middle":"Bent","Ring":"Bent","Pinky":"Bent"},
    "Open Hand": {"Thumb":"Straight","Index":"Straight","Middle":"Straight","Ring":"Straight","Pinky":"Straight"},
    "Peace ✌️": {"Index":"Straight","Middle":"Straight","Ring":"Bent","Pinky":"Bent","Thumb":"Bent"},
    "Thumbs Up 👍": {"Thumb":"Straight","Index":"Bent","Middle":"Bent","Ring":"Bent","Pinky":"Bent"},
    "Pointing ☝️": {"Index":"Straight","Thumb":"Bent","Middle":"Bent","Ring":"Bent","Pinky":"Bent"},
    "Okay 👌": {"Thumb":"Bent","Index":"Bent","Middle":"Straight","Ring":"Straight","Pinky":"Straight"},
    "Rock 🤘": {"Index":"Straight","Pinky":"Straight","Thumb":"Bent","Middle":"Bent","Ring":"Bent"},
    "Call Me 🤙": {"Thumb":"Straight","Pinky":"Straight","Index":"Bent","Middle":"Bent","Ring":"Bent"},
}


@st.cache_resource
def load_mediapipe_models():
    mp_pose = mp.solutions.pose
    mp_hands = mp.solutions.hands
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6, max_num_hands=2)
    drawing_utils = mp.solutions.drawing_utils
    return pose, hands, drawing_utils, mp_pose


def calculate_angle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(np.degrees(radians))
    return 360 - angle if angle > 180 else angle

def finger_state(finger_name, angle, thumb_thresh, straight_thresh):
    thresh = thumb_thresh if finger_name == "Thumb" else straight_thresh
    return "Straight" if angle > thresh else "Bent"

def smooth_position(key, x, y, positions, alpha=0.6):
    if key in positions:
        prev_x, prev_y = positions[key]
        x = int(alpha * x + (1 - alpha) * prev_x)
        y = int(alpha * y + (1 - alpha) * prev_y)
    positions[key] = (x, y)
    return x, y

def calculate_palm_center(landmarks):
    indices = [0, 1, 5, 9, 13, 17]
    x = int(np.mean([landmarks[i][0] for i in indices]))
    y = int(np.mean([landmarks[i][1] for i in indices]))
    return x, y

def normalized_dist(a, b, reference):
    d = math.hypot(a[0]-b[0], a[1]-b[1])
    return d / (reference + 1e-6)

def color_by_angle(angle):
    if -45 <= angle <= 45:
        return (0, 255, 160)
    elif 45 < angle <= 135 or -135 <= angle < -45:
        return (255, 180, 0)
    else:
        return (255, 80, 80)

def recognize_by_pattern(finger_states):
    for name, pattern in GESTURE_PATTERNS.items():
        if all(finger_states.get(f, "") == state for f, state in pattern.items()):
            return name
    return ""

def draw_gesture_label(image, palm_x, palm_y, gesture, confidence_count, gesture_history):
    overlay = image.copy()
    x1, y1 = palm_x - 110, palm_y - 80
    x2, y2 = palm_x + 110, palm_y - 20
    
    
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (30, 30, 40), -1)
    cv2.rectangle(overlay, (x1, y1), (x2, y2), VIOLET, 2)
    cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
    
    
    cv2.putText(image, gesture, (palm_x - 100, palm_y - 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
    
    
    bar_total_w = (x2 - x1) - 20
    bar_h = 8
    bar_x = x1 + 10
    bar_y = y2 - 15
    fill_w = int((confidence_count / gesture_history) * bar_total_w)
    
    
    cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_total_w, bar_y + bar_h), (50, 50, 60), -1)
    
    for i in range(fill_w):
        color_ratio = i / bar_total_w
        color = (
            int(138 + color_ratio * 117),
            int(43 + color_ratio * 212),
            int(226 - color_ratio * 66)
        )
        cv2.rectangle(image, (bar_x + i, bar_y), (bar_x + i + 1, bar_y + bar_h), color, -1)
    
    
    cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_total_w, bar_y + bar_h), (100, 100, 120), 1)

def draw_finger_skeleton(image, landmarks, mcp, pip, tip, state):
    
    for i in range(10):
        alpha = i / 10
        x1 = int(landmarks[mcp][0] * (1 - alpha) + landmarks[pip][0] * alpha)
        y1 = int(landmarks[mcp][1] * (1 - alpha) + landmarks[pip][1] * alpha)
        x2 = int(landmarks[mcp][0] * (1 - (alpha + 0.1)) + landmarks[pip][0] * (alpha + 0.1))
        y2 = int(landmarks[mcp][1] * (1 - (alpha + 0.1)) + landmarks[pip][1] * (alpha + 0.1))
        cv2.line(image, (x1, y1), (x2, y2), JOINT_COLOR[state], 3)
        
        x1 = int(landmarks[pip][0] * (1 - alpha) + landmarks[tip][0] * alpha)
        y1 = int(landmarks[pip][1] * (1 - alpha) + landmarks[tip][1] * alpha)
        x2 = int(landmarks[pip][0] * (1 - (alpha + 0.1)) + landmarks[tip][0] * (alpha + 0.1))
        y2 = int(landmarks[pip][1] * (1 - (alpha + 0.1)) + landmarks[tip][1] * (alpha + 0.1))
        cv2.line(image, (x1, y1), (x2, y2), JOINT_COLOR[state], 3)
    
    
    for p in (mcp, pip, tip):
        cv2.circle(image, tuple(landmarks[p]), 7, (30, 30, 40), -1)
        cv2.circle(image, tuple(landmarks[p]), 7, JOINT_COLOR[state], 2)

def draw_finger_label(image, tip_x, tip_y, hand_label, finger, state, hand_color):
    line1_pos = (tip_x + 12, tip_y - 30)
    line2_pos = (tip_x + 12, tip_y - 10)
    
    
    cv2.line(image, (tip_x, tip_y), (line1_pos[0] - 5, line1_pos[1] - 5), hand_color, 2)
    
    
    text_bg_size = cv2.getTextSize(f"{hand_label} {finger}", cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    cv2.rectangle(image, (line1_pos[0] - 5, line1_pos[1] - text_bg_size[1] - 5), 
                 (line1_pos[0] + text_bg_size[0] + 5, line2_pos[1] + 5), (30, 30, 40), -1)
    cv2.rectangle(image, (line1_pos[0] - 5, line1_pos[1] - text_bg_size[1] - 5), 
                 (line1_pos[0] + text_bg_size[0] + 5, line2_pos[1] + 5), hand_color, 1)
    
    
    cv2.putText(image, f"{hand_label} {finger}", line1_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, JOINT_COLOR[state], 2)
    cv2.putText(image, f"{state}", line2_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, JOINT_COLOR[state], 2)

def draw_arc(image, center, tip, color):
    dx, dy = tip[0] - center[0], tip[1] - center[1]
    angle = math.degrees(math.atan2(dy, dx))
    radius = max(10, int(math.hypot(dx, dy) * 0.45))
    start_angle = int(angle - 22)
    end_angle = int(angle + 22)
    cv2.ellipse(image, center, (radius, radius), 0, start_angle, end_angle, color, 3)

class HandGestureProcessor(VideoProcessorBase):
    def __init__(self):
        self.mode = MODE_NORMAL
        self.straight_thresh = DEFAULT_STRAIGHT_THRESH
        self.thumb_thresh = DEFAULT_THUMB_THRESH
        self.smooth_alpha = DEFAULT_SMOOTH_ALPHA
        self.gesture_history = DEFAULT_GESTURE_HISTORY
        self.gesture_confirm = DEFAULT_GESTURE_CONFIRM
        self.dist_ok_ratio = DEFAULT_DIST_OK_RATIO
        self.show_skeleton = True
        self.show_angles = True
        self.show_fps = True
        
        self.pose, self.hands, self.drawing_utils, self.mp_pose = load_mediapipe_models()
        self.smoothed_positions = {}
        self.gesture_histories = {"Left": deque(maxlen=self.gesture_history), "Right": deque(maxlen=self.gesture_history)}
        self.prev_time = 0
        self.current_fps = 0
        self.current_gestures = {"Left": "", "Right": ""}
    
    def update_params(self, mode, straight_thresh, thumb_thresh, smooth_alpha, 
                     gesture_history, gesture_confirm, dist_ok_ratio,
                     show_skeleton, show_angles, show_fps):
        self.mode = mode
        self.straight_thresh = straight_thresh
        self.thumb_thresh = thumb_thresh
        self.smooth_alpha = smooth_alpha
        self.gesture_history = gesture_history
        self.gesture_confirm = gesture_confirm
        self.dist_ok_ratio = dist_ok_ratio
        self.show_skeleton = show_skeleton
        self.show_angles = show_angles
        self.show_fps = show_fps
        
        
        for hand in self.gesture_histories:
            old_deque = self.gesture_histories[hand]
            new_deque = deque(old_deque, maxlen=gesture_history)
            self.gesture_histories[hand] = new_deque
    
    def process_hand(self, image, hand_landmarks, hand_label):
        h, w, _ = image.shape
        hand_color = HAND_COLORS.get(hand_label, (200,200,200))
        landmarks = [[int(lm.x * w), int(lm.y * h)] for lm in hand_landmarks.landmark]
        palm_x, palm_y = calculate_palm_center(landmarks)
        palm_x, palm_y = smooth_position(f"{hand_label}_palm", palm_x, palm_y, self.smoothed_positions, self.smooth_alpha)
        ref_spread = math.hypot(landmarks[5][0]-landmarks[17][0], landmarks[5][1]-landmarks[17][1])
        
        finger_joints = {
            "Thumb": (2, 3, 4),
            "Index": (5, 6, 8),
            "Middle": (9, 10, 12),
            "Ring": (13, 14, 16),
            "Pinky": (17, 18, 20)
        }
        
        finger_states = {}
        tip_positions = {}
        
        for finger, (mcp, pip, tip) in finger_joints.items():
            angle = calculate_angle(landmarks[mcp], landmarks[pip], landmarks[tip])
            state = finger_state(finger, angle, self.thumb_thresh, self.straight_thresh)
            finger_states[finger] = state
            tip_x, tip_y = smooth_position(f"{hand_label}_{finger}", landmarks[tip][0], landmarks[tip][1], 
                                          self.smoothed_positions, self.smooth_alpha)
            tip_positions[finger] = (tip_x, tip_y)
        
        if self.mode == MODE_NORMAL and self.show_skeleton:
            for finger, (mcp, pip, tip) in finger_joints.items():
                draw_finger_skeleton(image, landmarks, mcp, pip, tip, finger_states[finger])
                tip_x, tip_y = tip_positions[finger]
                draw_finger_label(image, tip_x, tip_y, hand_label, finger, finger_states[finger], hand_color)
        
        elif self.mode == MODE_ANGLE and self.show_angles:
            for finger in finger_joints:
                tip = tip_positions[finger]
                dx = tip[0] - palm_x; dy = tip[1] - palm_y
                finger_angle = np.degrees(np.arctan2(dy, dx))
                angle_color = color_by_angle(finger_angle)
                cv2.line(image, (palm_x, palm_y), (tip[0], tip[1]), angle_color, 3)
                draw_arc(image, (palm_x, palm_y), (tip[0], tip[1]), angle_color)
                cv2.putText(image, f"{finger_angle:.0f}°", (tip[0] - 15, tip[1] - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
        
        elif self.mode == MODE_GESTURE:
            candidate = recognize_by_pattern(finger_states)
            
            
            if candidate == "Okay 👌":
                thumb_tip = tip_positions["Thumb"]
                index_tip = tip_positions["Index"]
                if normalized_dist(thumb_tip, index_tip, ref_spread) >= self.dist_ok_ratio:
                    candidate = ""
            
            if candidate == "Thumbs Up 👍":
                thumb_tip = tip_positions["Thumb"]
                dy = palm_y - thumb_tip[1]
                if dy < ref_spread * 0.15:
                    candidate = ""
            
            hist = self.gesture_histories[hand_label]
            hist.append(candidate)
            
            if len(hist) > 0:
                most_common, count = Counter(hist).most_common(1)[0]
            else:
                most_common, count = "", 0
            
            if most_common != "" and count >= self.gesture_confirm:
                draw_gesture_label(image, palm_x, palm_y, most_common, count, self.gesture_history)
                self.current_gestures[hand_label] = most_common
            else:
                self.current_gestures[hand_label] = ""
                if candidate:
                    alpha_overlay = image.copy()
                    cv2.putText(alpha_overlay, candidate, (palm_x - 80, palm_y - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (220,220,220), 2, cv2.LINE_AA)
                    cv2.addWeighted(alpha_overlay, 0.25, image, 0.75, 0, image)
        
        wrist = landmarks[0]
        wrist_x, wrist_y = smooth_position(f"{hand_label}_wrist", wrist[0], wrist[1], 
                                          self.smoothed_positions, self.smooth_alpha)
        
        if self.mode != MODE_ANGLE:
            
            text_size = cv2.getTextSize(f"{hand_label} Hand", cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(image, (wrist_x - 35, wrist_y - 40), 
                         (wrist_x + text_size[0] + 5, wrist_y - 10), (30, 30, 40), -1)
            cv2.rectangle(image, (wrist_x - 35, wrist_y - 40), 
                         (wrist_x + text_size[0] + 5, wrist_y - 10), hand_color, 1)
            cv2.putText(image, f"{hand_label} Hand", (wrist_x - 30, wrist_y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, hand_color, 2, cv2.LINE_AA)
    
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        
        
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (img.shape[1], img.shape[0]), (10, 10, 30), -1)
        cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)
        
        
        curr_time = time.time()
        if self.prev_time:
            self.current_fps = 1 / (curr_time - self.prev_time)
        self.prev_time = curr_time
        
        
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        
        pose_results = self.pose.process(image_rgb)
        hand_results = self.hands.process(image_rgb)
        
        image_rgb.flags.writeable = True
        img = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        
        if pose_results.pose_landmarks:
            self.drawing_utils.draw_landmarks(
                img, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        
        if hand_results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                hand_label = hand_results.multi_handedness[idx].classification[0].label
                self.process_hand(img, hand_landmarks, hand_label)
        
        
        if self.show_fps:
            cv2.putText(img, f"FPS: {int(self.current_fps)}", (img.shape[1] - 150, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 200), 2)
        
        
        mode_text = "Normal" if self.mode == MODE_NORMAL else "Gesture" if self.mode == MODE_GESTURE else "Angle"
        cv2.putText(img, f"Mode: {mode_text}", (15, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 70, 255), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def about_page():
    st.markdown('<h1 class="main-header">About Neural HandSense AI</h1>', unsafe_allow_html=True)
    
    
    st.markdown('<p class="sub-header">Developer</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="dev-card floating">
            <div style="width: 140px; height: 140px; border-radius: 50%; background: linear-gradient(135deg, #8A2BE2, #00BFFF); margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 3rem; color: white;">DK</span>
            </div>
            <h2 style="color: white; margin-bottom: 0.5rem; font-family: 'Orbitron', sans-serif;">Dibyendu  Karmahapatra</h2>
            <p style="color: #a0a0a0; margin-bottom: 1.5rem; font-size: 1.1rem;">AIML and Deep Learning Engineer</p>
            <div style="display: flex; justify-content: center; flex-wrap: wrap;">
                <a href="https://www.linkedin.com/in/dibyendu-karmahapatra-17d2004/" class="social-badge">💼 LinkedIn</a>
                <a href="https://github.com/Dibyendu17122003" class="social-badge">🐙 GitHub</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="project-card">
            <h3 style="color: white; margin-bottom: 1.5rem; font-family: 'Orbitron', sans-serif;">About the Developer</h3>
            <p style="color: #cccccc; line-height: 1.6; font-size: 1.05rem;">
                Dibyendu Karmahapatra is an experienced AI/ML and Deep Learning Engineer with expertise in 
                computer vision, natural language processing, and neural networks. With a passion for 
                creating innovative solutions that bridge the gap between cutting-edge research and 
                real-world applications, he specializes in developing intelligent systems that can 
                perceive and interpret human gestures and behaviors.
            </p>
            <p style="color: #cccccc; line-height: 1.6; font-size: 1.05rem;">
                His work focuses on creating intuitive human-computer interfaces that leverage the 
                latest advancements in artificial intelligence to make technology more accessible 
                and responsive to human needs.
            </p>
            <div style="display: flex; flex-wrap: wrap; margin-top: 1.5rem;">
                <span class="tech-pill">Computer Vision</span>
                <span class="tech-pill">Deep Learning</span>
                <span class="tech-pill">Data Science</span>
                <span class="tech-pill">Neural Networks</span>
                <span class="tech-pill">AI Research</span>
                <span class="tech-pill">Gesture Recognition</span>
                <span class="tech-pill">Human-Computer Interaction</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    
    st.markdown('<p class="sub-header">Project Details</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-card">
        <h3 style="color: white; margin-bottom: 1.5rem; font-family: 'Orbitron', sans-serif;">Neural HandSense AI</h3>
        <p style="color: #cccccc; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
            Real-time AI-powered hand gesture recognition system using computer vision and deep learning.
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;">
            <span class="stat-badge">MediaPipe</span>
            <span class="stat-badge">OpenCV</span>
            <span class="stat-badge">Streamlit</span>
            <span class="stat-badge">Real-time</span>
            <span class="stat-badge">AI</span>
            <span class="stat-badge">Computer Vision</span>
        </div>
        <p style="color: #cccccc; line-height: 1.6; font-size: 1.05rem;">
            This project demonstrates advanced hand gesture recognition capabilities using MediaPipe 
            for hand tracking and OpenCV for image processing. The system can detect and classify 
            various hand gestures in real-time, providing an intuitive interface for human-computer 
            interaction.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    
    st.markdown('<p class="sub-header">Key Features</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #8A2BE2; margin-bottom: 1rem; font-family: 'Orbitron', sans-serif;">🎯 Real-time Detection</h3>
            <p style="color: #cccccc;">
                Processes video stream in real-time with high accuracy and low latency.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #8A2BE2; margin-bottom: 1rem; font-family: 'Orbitron', sans-serif;">🤖 Multiple Gestures</h3>
            <p style="color: #cccccc;">
                Recognizes 8+ different hand gestures with confidence-based validation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #8A2BE2; margin-bottom: 1rem; font-family: 'Orbitron', sans-serif;">🎨 Interactive UI</h3>
            <p style="color: #cccccc;">
                Modern, responsive interface with real-time feedback and visualization.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="sub-header">Technology Stack</p>', unsafe_allow_html=True)
    
    tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
    
    with tech_col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h4 style="color: #00BFFF; margin-bottom: 0.5rem;">Python</h4>
            <p style="color: #cccccc; font-size: 0.9rem;">Backend Logic</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h4 style="color: #00BFFF; margin-bottom: 0.5rem;">MediaPipe</h4>
            <p style="color: #cccccc; font-size: 0.9rem;">Hand Tracking</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h4 style="color: #00BFFF; margin-bottom: 0.5rem;">OpenCV</h4>
            <p style="color: #cccccc; font-size: 0.9rem;">Image Processing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_col4:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h4 style="color: #00BFFF; margin-bottom: 0.5rem;">Streamlit</h4>
            <p style="color: #cccccc; font-size: 0.9rem;">Web Interface</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8A2BE2; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px rgba(138, 43, 226, 0.5);">NEURAL HANDSENSE AI</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown('<p class="sub-header" style="font-size: 1.2rem;">Navigation</p>', unsafe_allow_html=True)
    page = st.sidebar.radio("", ["Hand Gesture Recognition", "About"], label_visibility="collapsed")
    
    if page == "Hand Gesture Recognition":
        st.markdown('<h1 class="main-header">Neural HandSense AI</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #a0a0a0; margin-top: -1rem; margin-bottom: 2rem; font-size: 1.1rem;">Advanced hand gesture recognition with real-time AI analysis</p>', unsafe_allow_html=True)
        
       
        if 'processor' not in st.session_state:
            st.session_state.processor = HandGestureProcessor()
        
        if 'mode' not in st.session_state:
            st.session_state.mode = MODE_NORMAL
        
        
        st.sidebar.markdown('<p class="sub-header" style="font-size: 1.2rem;">Settings</p>', unsafe_allow_html=True)
        
        
        mode_options = ["Normal", "Gesture", "Angle"]
        mode_index = st.sidebar.selectbox(
            "Detection Mode",
            options=[0, 1, 2],
            format_func=lambda x: mode_options[x],
            index=st.session_state.mode
        )
        
        
        tab1, tab2, tab3 = st.sidebar.tabs(["Thresholds", "Gesture", "Display"])
        
        with tab1:
            st.markdown('<p class="metric-label">Threshold Settings</p>', unsafe_allow_html=True)
            straight_thresh = st.slider("Straight Finger Threshold", 120, 200, DEFAULT_STRAIGHT_THRESH)
            thumb_thresh = st.slider("Thumb Threshold", 120, 200, DEFAULT_THUMB_THRESH)
            smooth_alpha = st.slider("Smoothing Alpha", 0.1, 0.9, DEFAULT_SMOOTH_ALPHA, 0.1)
        
        with tab2:
            st.markdown('<p class="metric-label">Gesture Settings</p>', unsafe_allow_html=True)
            gesture_history = st.slider("Gesture History Size", 5, 20, DEFAULT_GESTURE_HISTORY)
            gesture_confirm = st.slider("Gesture Confirmation Threshold", 3, 10, DEFAULT_GESTURE_CONFIRM)
            dist_ok_ratio = st.slider("Okay Gesture Distance Ratio", 0.1, 0.3, DEFAULT_DIST_OK_RATIO, 0.01)
        
        with tab3:
            st.markdown('<p class="metric-label">Display Options</p>', unsafe_allow_html=True)
            show_skeleton = st.checkbox("Show Skeleton", value=True)
            show_angles = st.checkbox("Show Angles", value=True)
            show_fps = st.checkbox("Show FPS Counter", value=True)
        
        
        with st.sidebar.expander("Help & Instructions"):
            st.markdown("""
            <div class="help-text">
            <p><strong>Modes:</strong></p>
            <ul>
                <li><strong>Normal</strong>: Shows finger skeleton with Straight/Bent labels</li>
                <li><strong>Gesture</strong>: Recognizes hand gestures with stabilization</li>
                <li><strong>Angle</strong>: Shows fingertip angles from palm center</li>
            </ul>
            <p><strong>Recognized Gestures:</strong></p>
            <ul>
                <li>Fist, Open Hand, Peace ✌️, Thumbs Up 👍</li>
                <li>Pointing ☝️, Okay 👌, Rock 🤘, Call Me 🤙</li>
            </ul>
            <p><strong>Tips:</strong></p>
            <ul>
                <li>Ensure good lighting for best results</li>
                <li>Keep your hand visible and well-positioned</li>
                <li>Adjust thresholds if detection is inaccurate</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        
        st.session_state.processor.update_params(
            mode_index, straight_thresh, thumb_thresh, smooth_alpha,
            gesture_history, gesture_confirm, dist_ok_ratio,
            show_skeleton, show_angles, show_fps
        )
        st.session_state.mode = mode_index
        
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            
            ctx = webrtc_streamer(
                key="hand-gesture",
                video_processor_factory=HandGestureProcessor,
                rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
                media_stream_constraints={"video": True, "audio": False},
            )
            
            if ctx.video_processor:
                
                ctx.video_processor.update_params(
                    mode_index, straight_thresh, thumb_thresh, smooth_alpha,
                    gesture_history, gesture_confirm, dist_ok_ratio,
                    show_skeleton, show_angles, show_fps
                )
        
        with col2:
            
            st.markdown('<p class="sub-header">Detected Gestures</p>', unsafe_allow_html=True)
            
            if ctx.video_processor:
                left_gesture = ctx.video_processor.current_gestures["Left"]
                right_gesture = ctx.video_processor.current_gestures["Right"]
                fps = ctx.video_processor.current_fps
                
                
                if left_gesture:
                    st.markdown(f'<div class="gesture-card glowing"><h3>👈 Left Hand: {left_gesture}</h3></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="gesture-card"><h3>👈 Left Hand: No gesture detected</h3></div>', unsafe_allow_html=True)
                
                
                if right_gesture:
                    st.markdown(f'<div class="gesture-card glowing"><h3>👉 Right Hand: {right_gesture}</h3></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="gesture-card"><h3>👉 Right Hand: No gesture detected</h3></div>', unsafe_allow_html=True)
                

                st.markdown('<p class="sub-header">Performance Metrics</p>', unsafe_allow_html=True)
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.markdown('<p class="metric-label">FPS</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="metric-value">{int(fps) if fps else 0}</p>', unsafe_allow_html=True)
                
                with metric_col2:
                    st.markdown('<p class="metric-label">Mode</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="metric-value">{mode_options[mode_index]}</p>', unsafe_allow_html=True)
                
                with metric_col3:
                    st.markdown('<p class="metric-label">Hands</p>', unsafe_allow_html=True)
                    hands_detected = sum(1 for g in [left_gesture, right_gesture] if g != "")
                    st.markdown(f'<p class="metric-value">{hands_detected}/2</p>', unsafe_allow_html=True)
                
                
                if mode_index == MODE_GESTURE and ctx.video_processor.gesture_histories:
                    st.markdown('<p class="sub-header">Confidence Levels</p>', unsafe_allow_html=True)
                    
                    for hand in ["Left", "Right"]:
                        hist = ctx.video_processor.gesture_histories[hand]
                        if hist:
                            most_common, count = Counter(hist).most_common(1)[0]
                            confidence = count / gesture_history
                            
                            col_conf_text, col_conf_bar = st.columns([1, 2])
                            with col_conf_text:
                                st.markdown(f'<p class="metric-label">{hand} Hand</p>', unsafe_allow_html=True)
                            with col_conf_bar:
                                st.progress(confidence)
            
            else:
                st.info("Camera feed will appear here once started")
                
                
                st.markdown('<p class="sub-header">Performance Metrics</p>', unsafe_allow_html=True)
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.markdown('<p class="metric-label">FPS</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="metric-value">0</p>', unsafe_allow_html=True)
                
                with metric_col2:
                    st.markdown('<p class="metric-label">Mode</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="metric-value">{mode_options[mode_index]}</p>', unsafe_allow_html=True)
                
                with metric_col3:
                    st.markdown('<p class="metric-label">Hands</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="metric-value">0/2</p>', unsafe_allow_html=True)
    
    else:
        about_page()

if __name__ == "__main__":
    main()