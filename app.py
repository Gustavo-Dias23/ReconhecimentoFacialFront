import cv2
import dlib
import numpy as np
import pickle
import os
import time
from flask import Flask, render_template, Response, request, redirect, url_for, session

# --- CONFIGURAÇÕES GLOBAIS ---
# Se a câmera não funcionar, mude este número para 1, 2 ou -1
CAMERA_INDEX = 0

# Limite de reconhecimento. Valores maiores são MENOS exigentes.
# Se o login falha, tente aumentar para 0.62 ou 0.65.
RECOGNITION_THRESHOLD = 0.6

PREDICTOR_PATH = "shape_predictor_5_face_landmarks.dat"
RECOG_MODEL_PATH = "dlib_face_recognition_resnet_model_v1.dat"
DB_FILE = "db.pkl"
SAMPLES_TO_COLLECT = 5

# --- INICIALIZAÇÃO DA APLICAÇÃO E MODELOS ---
app = Flask(__name__)
app.secret_key = 'chave_secreta_para_a_sessao'

# Carrega a base de dados de rostos
db = pickle.load(open(DB_FILE, "rb")) if os.path.exists(DB_FILE) else {}

# Carrega os modelos do Dlib
try:
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(PREDICTOR_PATH)
    rec = dlib.face_recognition_model_v1(RECOG_MODEL_PATH)
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar os modelos do Dlib. Verifique os arquivos .dat: {e}")
    detector = sp = rec = None

# Inicializa a câmera de forma global e segura
cap = None
def initialize_camera():
    global cap
    if cap is None:
        try:
            cap = cv2.VideoCapture(CAMERA_INDEX)
            if not cap.isOpened():
                raise IOError(f"Não foi possível abrir a câmera no índice {CAMERA_INDEX}.")
            print("Câmera inicializada com sucesso.")
        except Exception as e:
            print(f"ERRO AO INICIALIZAR CÂMERA: {e}")
            cap = None

initialize_camera()

# --- ROTAS PRINCIPAIS ---
@app.route('/')
def index():
    session.pop('user', None)  # Limpa a sessão ao ir para a página de login
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/capture', methods=['POST'])
def start_capture():
    name = request.form.get('name')
    if not name:
        return render_template('register.html', error="O nome é obrigatório.")
    if name in db:
        return render_template('register.html', error=f"O nome '{name}' já existe.")
    
    session['register_name'] = name
    return render_template('capture.html', name=name)

@app.route('/quiz')
def quiz():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('quiz.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    # ... (lógica do quiz, sem alterações)
    if 'user' not in session: return redirect(url_for('index'))
    score = sum(int(request.form.get(q, 0)) for q in ['q1', 'q2', 'q3'])
    if score <= 4: profile, desc = "Conservador", "Renda Fixa (Tesouro Direto, CDBs)."
    elif score <= 7: profile, desc = "Moderado", "Fundos Multimercado, Fundos Imobiliários."
    else: profile, desc = "Arrojado", "Ações, Fundos de Ações, Criptomoedas."
    return render_template('result.html', profile=profile, description=desc)

# --- ROTAS DE VÍDEO E STATUS ---
def frame_generator(mode='login'):
    """Função central que gera os frames da câmera para login e registro."""
    global db
    if not cap or not cap.isOpened() or not detector:
        print("Gerador de frames não pode rodar: câmera ou modelos não inicializados.")
        return

    amostras = []
    register_name = session.get('register_name')

    while True:
        ok, frame = cap.read()
        if not ok: continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector(rgb, 1)

        for r in rects:
            shape = sp(rgb, r)
            chip = dlib.get_face_chip(rgb, shape)
            vec = np.array(rec.compute_face_descriptor(chip), dtype=np.float32)

            if mode == 'login' and 'user' not in session:
                nome, dist_min = "Desconhecido", 999
                for n, v in db.items():
                    d = np.linalg.norm(vec - v)
                    if d < dist_min: nome, dist_min = n, d
                
                print(f"[DIAGNÓSTICO] Rosto próximo: {nome}, Distância: {dist_min:.4f}, Limite: {RECOGNITION_THRESHOLD}")

                if dist_min <= RECOGNITION_THRESHOLD:
                    session['user'] = nome
                    print(f"SUCESSO: Usuário '{nome}' autenticado.")
                else:
                    cv2.putText(frame, "Desconhecido", (r.left(), r.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            elif mode == 'register' and register_name and len(amostras) < SAMPLES_TO_COLLECT:
                amostras.append(vec)
                status_text = f"Amostra {len(amostras)}/{SAMPLES_TO_COLLECT}"
                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                time.sleep(0.5)

                if len(amostras) == SAMPLES_TO_COLLECT:
                    db[register_name] = np.mean(amostras, axis=0)
                    with open(DB_FILE, "wb") as f: pickle.dump(db, f)
                    session.pop('register_name', None)
                    print(f"SUCESSO: Usuário '{register_name}' cadastrado.")
            
            cv2.rectangle(frame, (r.left(), r.top()), (r.right(), r.bottom()), (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed_login')
def video_feed_login():
    return Response(frame_generator(mode='login'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_register')
def video_feed_register():
    return Response(frame_generator(mode='register'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_login_status')
def check_login_status():
    return {'logged_in': 'user' in session, 'user': session.get('user')}

if __name__ == "__main__":
    app.run(debug=True)