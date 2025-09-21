# Face Recognition Python

Sistema de reconhecimento facial em tempo real com cadastro, validação e gerenciamento de rostos usando Python, OpenCV e Dlib.

## Funcionalidades

* **Cadastro de rostos:** Coleta múltiplas amostras faciais de um usuário e cria um vetor médio para reconhecimento.
* **Validação em tempo real:** Detecta rostos na câmera e identifica usuários cadastrados.
* **Gestão de registros:** Permite apagar rostos cadastrados.
* **Interface simples:** Controle via teclado com feedback no terminal.
* **Efeito de foco:** Durante a validação, o rosto detectado permanece nítido enquanto o restante do frame é suavizado.
* **Indicador de FPS:** Mostra a taxa de frames por segundo no vídeo.

## Requisitos

* Python 3.7+
* Bibliotecas Python:

```bash
pip install opencv-python dlib numpy
```

* Arquivos de modelos Dlib:

  * `shape_predictor_5_face_landmarks.dat`
  * `dlib_face_recognition_resnet_model_v1.dat`

> ⚠️ Ambos os arquivos devem estar na mesma pasta do script ou fornecer o caminho correto.

## Uso

1. **Executar o script:**

```bash
python main.py
```

2. **Comandos no teclado:**

   * `[E]` – Cadastrar novo rosto
   * `[V]` – Ativar/Desativar validação em tempo real
   * `[D]` – Deletar um registro existente
   * `[Q]` – Sair do programa

3. **Cadastro de rosto:**
   Pressione `E` e digite o nome do usuário. O sistema coletará 5 amostras e armazenará no arquivo `db.pkl`.

4. **Validação de rosto:**
   Ative a validação com `V`. O sistema exibirá o nome do usuário reconhecido e aplicará um efeito de desfoque no restante da imagem.

5. **Deletar registro:**
   Pressione `D`, escolha o nome exato do usuário e confirme para remover do banco de dados.

## Estrutura do Projeto

```
├── main.py                 # Script principal
├── db.pkl                  # Banco de dados de rostos (gerado automaticamente)
├── shape_predictor_5_face_landmarks.dat
├── dlib_face_recognition_resnet_model_v1.dat
└── README.md
```

## Configurações

* `THRESH`: Distância máxima para considerar um rosto como conhecido (padrão: 0.6)
* `SAMPLES`: Número de amostras coletadas por usuário (padrão: 5)
* `cooldown`: Intervalo de tempo em segundos entre reconhecimentos do mesmo rosto

## Observações

* Recomenda-se boa iluminação para melhorar a detecção e reconhecimento.
* O arquivo `db.pkl` armazena os vetores faciais, não as imagens.
* Para parar a coleta de amostras antes do final, pressione `q`.

## Nota Ética sobre Uso de Dados Faciais

Este projeto envolve o uso de dados faciais, que são informações sensíveis e pessoais. Reforçamos a importância do uso **responsável e ético** deste sistema:

* Os rostos cadastrados devem pertencer apenas a pessoas que deram consentimento explícito para coleta e armazenamento de seus dados.
* Os dados faciais devem ser usados **apenas para fins de estudo, pesquisa ou controle de acesso autorizado**, nunca para vigilância sem autorização.
* O arquivo `db.pkl` contém apenas vetores faciais e **não armazena imagens completas**, mas ainda assim deve ser protegido e tratado com confidencialidade.
* O desenvolvedor e os usuários deste sistema **devem respeitar leis de privacidade e regulamentações locais**, incluindo LGPD, GDPR ou legislações equivalentes.

O uso indevido deste sistema para invadir a privacidade de terceiros ou coletar dados sem consentimento é estritamente proibido.
