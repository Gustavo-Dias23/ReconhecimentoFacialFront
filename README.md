# Sistema Web de Login Facial e Análise de Perfil de Investidor

Aplicação web que utiliza reconhecimento facial em tempo real para autenticação de usuários. Após o login, o sistema apresenta um quiz para determinar o perfil de investidor do usuário, sugerindo os tipos de investimento mais adequados.

## Participantes do grupo
| Nome                   | RM       |
| ---------------------- | -------- |
| Leonardo Moreira Valério | RM550988 |
| Breno Silva            | RM97864  |
| Enrico Marquez         | RM99325  |
| Joel Barros            | RM550378 |
| Gustavo Dias           | RM550820 |

## Funcionalidades

* **Cadastro Facial via Web:** Coleta amostras do rosto do usuário através da webcam para criar um registro de autenticação.
* **Login com Reconhecimento Facial:** Valida a identidade do usuário em tempo real, comparando o rosto na câmera com os registros no banco de dados.
* **Quiz de Perfil de Investidor:** Após o login, o usuário responde a um questionário de 3 perguntas para identificar seu perfil (Conservador, Moderado ou Arrojado).
* **Recomendação de Investimentos:** Com base no resultado do quiz, o sistema sugere as categorias de investimento mais alinhadas ao perfil do usuário.
* **Interface Web Intuitiva:** Toda a interação é feita através de uma interface web simples e direta, construída com Flask.

## Requisitos

* Python 3.7+
* Bibliotecas Python:
    ```bash
    pip install opencv-python dlib numpy Flask
    ```
* Arquivos de modelos Dlib:
    * `shape_predictor_5_face_landmarks.dat`
    * `dlib_face_recognition_resnet_model_v1.dat`

> ⚠️ Ambos os arquivos de modelo devem estar na mesma pasta do script `app.py`.

## Uso

1.  **Executar o servidor web:**
    No terminal, navegue até a pasta do projeto e execute o comando:
    ```bash
    python app.py
    ```

2.  **Acessar a aplicação:**
    Abra seu navegador e acesse o endereço `http://127.0.0.1:5000`.

3.  **Cadastrar um rosto:**
    * Na página inicial, clique em "Cadastre-se".
    * Digite seu nome e clique em "Iniciar Captura".
    * Posicione seu rosto em frente à câmera na página de captura. O sistema coletará 5 amostras e te redirecionará para a página de login.

4.  **Fazer Login:**
    * Na página de login, posicione seu rosto em frente à câmera.
    * Ao ser reconhecido, você verá uma mensagem de boas-vindas e será redirecionado para o quiz.

5.  **Responder ao Quiz:**
    * Responda às 3 perguntas para descobrir seu perfil de investidor e ver as recomendações.

## Estrutura do Projeto