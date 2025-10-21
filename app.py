import cv2
import dlib
import numpy as np
import pickle
import os
import time
from flask import Flask, render_template, Response, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui' 

# --- PONTO DE ATENÇÃO 1: ÍNDICE DA CÂMERA ---
# Se a câmera não ligar, tente mudar o número 0 para 1, 2, ou -1.
# Ex: cap = cv2.VideoCapture(1)
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Não foi possível abrir a webcam.")
except Exception as e:
    print(f"Erro ao acessar a câmera: {e}")
    # Você pode querer lidar com isso de forma mais elegante
    # em uma aplicação real. Por enquanto, vamos imprimir o erro.
    cap = None # Garante que 'cap' existe mesmo que falhe

# --- CONFIGURAÇÕES DO MODELO DE RECONHECIMENTO FACIAL ---
PREDICTOR = "shape_predictor_5_face_landmarks.dat"
RECOG = "dlib_face_recognition_resnet_model_v1.dat"
DB_FILE = "db.pkl"
THRESH = 0.6
SAMPLES = 5

db = pickle.load(open(DB_FILE, "rb")) if os.path.exists(DB_FILE) else {}
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(PREDICTOR)
rec = dlib.face_recognition_model_v1(RECOG)


# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def index():
    """Página de login."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de cadastro. GET para mostrar o form, POST para processar o nome."""
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            return render_template('register.html', error="O nome é obrigatório.")
        if name in db:
            return render_template('register.html', error=f"O nome '{name}' já existe.")
        
        # Guarda o nome na sessão e redireciona para a página de captura
        session['register_name'] = name
        return redirect(url_for('capture'))

    return render_template('register.html')

@app.route('/capture')
def capture():
    """Página que efetivamente mostra o vídeo para cadastro."""
    if 'register_name' not in session:
        return redirect(url_for('register'))
    return render_template('capture.html', name=session['register_name'])

@app.route('/quiz')
def quiz():
    """Página do quiz. Redireciona para o login se o usuário não estiver logado."""
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('quiz.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Processa as respostas do quiz e define o perfil de investimento."""
    if 'user' not in session:
        return redirect(url_for('index'))

    score = int(request.form['q1']) + int(request.form['q2']) + int(request.form['q3'])

    if score <= 4:
        profile = "Conservador"
        description = "Você prefere segurança e baixo risco. Investimentos recomendados: Renda Fixa (Tesouro Direto, CDBs)."
    elif score <= 7:
        profile = "Moderado"
        description = "Você busca um equilíbrio entre segurança e rentabilidade. Investimentos recomendados: Fundos Multimercado, Fundos Imobiliários."
    else:
        profile = "Arrojado"
        description = "Você está disposto a correr mais riscos em busca de maiores retornos. Investimentos recomendados: Ações, Fundos de Ações, Criptomoedas."

    return render_template('result.html', profile=profile, description=description)

def generate_frames(mode='login'):
    """Gera frames da câmera para o streaming de vídeo."""
    global db
    amostras = []
    
    # Recupera o nome para o modo de registro a partir da sessão
    user_name_to_register = session.get('register_name') if mode == 'register' else None
    
    if not cap or not cap.isOpened():
        print("Câmera não está disponível.")
        return # Encerra a função se a câmera não estiver acessível

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector(rgb, 1)

        for r in rects:
            shape = sp(rgb, r)
            chip = dlib.get_face_chip(rgb, shape)
            vec = np.array(rec.compute_face_descriptor(chip), dtype=np.float32)

            if mode == 'login' and db:
                nome = "Desconhecido"
                dist_min = 999
                for n, v in db.items():
                    d = np.linalg.norm(vec - v)
                    if d < dist_min:
                        nome, dist_min = n, d
                if dist_min <= THRESH:
                    cv2.putText(frame, f"Bem-vindo, {nome}!", (r.left(), r.top() - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    if 'user' not in session or session['user'] != nome:
                         session['user'] = nome # Loga o usuário
                else:
                    cv2.putText(frame, "Desconhecido", (r.left(), r.top() - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            elif mode == 'register' and user_name_to_register and len(amostras) < SAMPLES:
                amostras.append(vec)
                status_text = f"Amostra {len(amostras)}/{SAMPLES}"
                cv2.putText(frame, status_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                time.sleep(0.5) # Pausa para o usuário se mover um pouco
                
                if len(amostras) == SAMPLES:
                    media = np.mean(amostras, axis=0)
                    db[user_name_to_register] = media
                    with open(DB_FILE, "wb") as f:
                        pickle.dump(db, f)
                    print(f"Usuário '{user_name_to_register}' cadastrado!")
                    session.pop('register_name', None) # Limpa o nome da sessão
                    mode = 'done' # Para de coletar

            cv2.rectangle(frame, (r.left(), r.top()), (r.right(), r.bottom()), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'--frame\r\n')

@app.route('/video_feed_login')
def video_feed_login():
    return Response(generate_frames(mode='login'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_register')
def video_feed_register():
    return Response(generate_frames(mode='register'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_login_status')
def check_login_status():
    """Rota para o JS verificar se o login foi bem-sucedido."""
    if 'user' in session:
        return {'logged_in': True, 'user': session['user']}
    return {'logged_in': False}

if __name__ == "__main__":
    app.run(debug=True)