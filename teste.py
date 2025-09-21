import cv2, dlib, numpy as np, pickle, os, time

PREDICTOR = "shape_predictor_5_face_landmarks.dat"
RECOG = "dlib_face_recognition_resnet_model_v1.dat"
DB_FILE = "db.pkl"
THRESH = 0.6
SAMPLES = 5

db = pickle.load(open(DB_FILE,"rb")) if os.path.exists(DB_FILE) else {}
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(PREDICTOR)
rec = dlib.face_recognition_model_v1(RECOG)

cap = cv2.VideoCapture(0)
validando, ultimo = False, 0
cooldown = 3

print("[E]=Cadastrar  [V]=Validar ON/OFF  [D]=Deletar  [Q]=Sair")

def coletar_amostras(nome):
    print(f"[INFO] Coletando {SAMPLES} amostras para {nome}...")
    amostras = []
    while len(amostras) < SAMPLES:
        ok, frame = cap.read()
        if not ok: continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector(rgb, 1)
        for r in rects:
            shape = sp(rgb, r)
            chip = dlib.get_face_chip(rgb, shape)
            vec = np.array(rec.compute_face_descriptor(chip), dtype=np.float32)
            amostras.append(vec)
            print(f"  Amostra {len(amostras)}/{SAMPLES}")
            time.sleep(0.5)
        cv2.imshow("Coletando", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return None
    cv2.destroyWindow("Coletando")
    return np.mean(amostras, axis=0)

def apagar_registro():
    if not db:
        print("[INFO] Nenhum rosto cadastrado.")
        return
    print("\n[Registros atuais]")
    for i, nome in enumerate(db.keys(), 1):
        print(f"{i}. {nome}")
    alvo = input("Digite o NOME exato que deseja apagar: ").strip()
    if alvo in db:
        db.pop(alvo)
        pickle.dump(db, open(DB_FILE, "wb"))
        print(f"[INFO] Registro de '{alvo}' removido com sucesso.")
    else:
        print("[ERRO] Nome não encontrado.")

while True:
    ok, frame = cap.read()
    if not ok: break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rects = detector(rgb, 1)

    display_frame = frame.copy()
    if validando and rects:
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for r in rects:
            center_x = (r.left() + r.right()) // 2
            center_y = (r.top() + r.bottom()) // 2
            radius = int(max((r.right() - r.left()) // 2, (r.bottom() - r.top()) // 2) * 1.5)
            cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        mask = cv2.GaussianBlur(mask, (51, 51), 0)  # suaviza borda
        mask = mask.astype(float)/255.0
        display_frame = (frame * mask[:, :, np.newaxis] + cv2.GaussianBlur(frame, (35,35), 0) * (1-mask[:, :, np.newaxis])).astype(np.uint8)

    for r in rects:
        shape = sp(rgb, r)
        chip = dlib.get_face_chip(rgb, shape)
        vec = np.array(rec.compute_face_descriptor(chip), dtype=np.float32)

        nome = "Desconhecido"
        if validando and db:
            dist_min = 999
            for n, v in db.items():
                d = np.linalg.norm(vec - v)
                if d < dist_min:
                    nome, dist_min = n, d
            if dist_min > THRESH:
                nome = "Desconhecido"

            if nome != "Desconhecido" and time.time()-ultimo > cooldown:
                print(f"[INFO] {nome} reconhecido!")
                ultimo = time.time()

            cv2.putText(display_frame, nome, (r.left(), r.top()-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("Faces", display_frame)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'): break
    if k == ord('v'): validando = not validando
    if k == ord('e'):
        nome_input = input("Nome: ").strip()
        if nome_input:
            media = coletar_amostras(nome_input)
            if media is not None:
                db[nome_input] = media
                pickle.dump(db, open(DB_FILE,"wb"))
                print("✅ Salvo:", nome_input)
    if k == ord('d'):
        apagar_registro()

cap.release()
cv2.destroyAllWindows()
