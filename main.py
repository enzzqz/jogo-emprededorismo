from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

# Lista de palavras para o jogo da Forca
hangman_words = ["python", "flask", "html", "javascript", "developer"]

# Variáveis globais para o estado do jogo
hangman_word = ""
hangman_word_display = ""
hangman_attempts = 0
hangman_used_letters = []

current_question = None
current_answers = None
current_correct_answer = None

# HTML com CSS e JavaScript
html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jogos Divertidos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #282c34;
            color: white;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        h1, h2 {
            margin-bottom: 20px;
        }
        .game-container {
            margin: 20px;
        }
        .buttons {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }
        .buttons button {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        /* Estilos dos botões do Pedra, Papel e Tesoura */
        #pedra { background-color: #d9534f; }
        #papel { background-color: #5bc0de; }
        #tesoura { background-color: #5cb85c; }
        /* Estilos dos botões do Adivinhe o Número */
        .button-1 { background-color: #f0ad4e; }
        .button-2 { background-color: #5bc0de; }
        .button-3 { background-color: #5cb85c; }
        .button-4 { background-color: #d9534f; }
        .button-5 { background-color: #f0ad4e; }
        .button-6 { background-color: #5bc0de; }
        .button-7 { background-color: #5cb85c; }
        .button-8 { background-color: #d9534f; }
        .button-9 { background-color: #f0ad4e; }
        .button-10 { background-color: #5bc0de; }
        /* Estilos dos botões do Quiz */
        .quiz-option {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .quiz-option-a { background-color: #d9534f; }
        .quiz-option-b { background-color: #5bc0de; }
        .quiz-option-c { background-color: #5cb85c; }
        .quiz-option-d { background-color: #f0ad4e; }
        /* Estilos dos botões do Forca */
        .hangman-letter {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .hangman-letter:hover {
            background-color: #333;
        }
        .result-box, .hangman-message {
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #fff;
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.1);
        }
    </style>
    <script>
        let hangmanWord = "";
        let hangmanWordDisplay = "";
        let hangmanAttempts = 0;
        let hangmanUsedLetters = [];
        let currentQuestion = "";
        let currentAnswers = {};
        let currentCorrectAnswer = "";

        function playRPS(choice) {
            fetch('/play_rps', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ choice: choice })
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('result').innerHTML = 
                    `<div class="result-box">
                        <p>Você escolheu: ${result.user_choice}</p>
                        <p>Computador escolheu: ${result.computer_choice}</p>
                        <p>Resultado: ${result.result}</p>
                    </div>`;

                updateScoreboard(result.result);
                updateHistory(result.user_choice, result.computer_choice, result.result);
            });
        }

        function updateScoreboard(result) {
            let wins = parseInt(document.getElementById('scoreboard').children[0].innerText.split(': ')[1]);
            let losses = parseInt(document.getElementById('scoreboard').children[1].innerText.split(': ')[1]);
            let ties = parseInt(document.getElementById('scoreboard').children[2].innerText.split(': ')[1]);

            if (result === "você ganhou") {
                wins++;
            } else if (result === "você perdeu") {
                losses++;
            } else if (result === "empate") {
                ties++;
            }

            document.getElementById('scoreboard').innerHTML = 
                `<div>Vitórias: ${wins}</div>
                 <div>Derrotas: ${losses}</div>
                 <div>Empates: ${ties}</div>`;
        }

        function updateHistory(userChoice, computerChoice, result) {
            let history = document.getElementById('history').innerHTML;
            history = `<ul>
                        <li>Você: ${userChoice}, Computador: ${computerChoice}, Resultado: ${result}</li>
                        ${history}
                    </ul>`;
            document.getElementById('history').innerHTML = history;
        }

        function guessNumberGame(guess) {
            fetch('/guess_number', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ guess: guess })
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('guess-result').innerHTML = 
                    `<div class="result-box">${result.message}</div>`;
            });
        }

        function startQuiz() {
            fetch('/start_quiz')
            .then(response => response.json())
            .then(data => {
                currentQuestion = data.question;
                currentAnswers = data.answers;
                currentCorrectAnswer = data.correct_answer;
                document.getElementById('quiz-question').innerText = currentQuestion;
                document.querySelector('.quiz-option-a').innerText = currentAnswers.A;
                document.querySelector('.quiz-option-b').innerText = currentAnswers.B;
                document.querySelector('.quiz-option-c').innerText = currentAnswers.C;
                document.querySelector('.quiz-option-d').innerText = currentAnswers.D;
            });
        }

        function answerQuiz(answer) {
            fetch('/answer_quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answer: answer })
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('quiz-result').innerHTML = 
                    `<div class="result-box">${result.message}</div>`;
            });
        }

        function startHangman() {
            fetch('/start_hangman')
            .then(response => response.json())
            .then(data => {
                hangmanWord = data.word;
                hangmanWordDisplay = "_".repeat(hangmanWord.length);
                hangmanAttempts = 6;
                hangmanUsedLetters = [];
                updateHangmanDisplay();
            });
        }

        function guessHangman(letter) {
            fetch('/guess_hangman', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ letter: letter })
            })
            .then(response => response.json())
            .then(result => {
                hangmanWordDisplay = result.word_display;
                hangmanAttempts = result.attempts;
                hangmanUsedLetters = result.used_letters;
                document.getElementById('hangman-display').innerText = hangmanWordDisplay;
                document.getElementById('hangman-attempts').innerText = "Tentativas restantes: " + hangmanAttempts;
                document.getElementById('hangman-used-letters').innerText = "Letras usadas: " + hangmanUsedLetters.join(", ");
                document.getElementById('hangman-message').innerText = result.message;

                if (result.game_over) {
                    document.getElementById('hangman-message').innerHTML += "<br><button onclick='startHangman()'>Jogar Novamente</button>";
                }
            });
        }

        function updateHangmanDisplay() {
            document.getElementById('hangman-display').innerText = hangmanWordDisplay;
            document.getElementById('hangman-attempts').innerText = "Tentativas restantes: " + hangmanAttempts;
            document.getElementById('hangman-used-letters').innerText = "Letras usadas: " + hangmanUsedLetters.join(", ");
            document.getElementById('hangman-message').innerText = "";
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Jogos Divertidos</h1>
        <div class="game-container">
            <h2>Pedra, Papel e Tesoura</h2>
            <div class="buttons">
                <button id="pedra" onclick="playRPS('pedra')">Pedra</button>
                <button id="papel" onclick="playRPS('papel')">Papel</button>
                <button id="tesoura" onclick="playRPS('tesoura')">Tesoura</button>
            </div>
            <div id="result"></div>
            <div id="scoreboard" class="scoreboard">
                <div>Vitórias: 0</div>
                <div>Derrotas: 0</div>
                <div>Empates: 0</div>
            </div>
            <div id="history" class="history"></div>
        </div>

        <div class="game-container">
            <h2>Adivinhe o Número</h2>
            <div class="buttons">
                <button class="button-1" onclick="guessNumberGame(1)">1</button>
                <button class="button-2" onclick="guessNumberGame(2)">2</button>
                <button class="button-3" onclick="guessNumberGame(3)">3</button>
                <button class="button-4" onclick="guessNumberGame(4)">4</button>
                <button class="button-5" onclick="guessNumberGame(5)">5</button>
                <button class="button-6" onclick="guessNumberGame(6)">6</button>
                <button class="button-7" onclick="guessNumberGame(7)">7</button>
                <button class="button-8" onclick="guessNumberGame(8)">8</button>
                <button class="button-9" onclick="guessNumberGame(9)">9</button>
                <button class="button-10" onclick="guessNumberGame(10)">10</button>
            </div>
            <div id="guess-result"></div>
        </div>

        <div class="game-container">
            <h2>Quiz</h2>
            <button onclick="startQuiz()">Começar Quiz</button>
            <div id="quiz-question"></div>
            <div class="buttons">
                <button class="quiz-option quiz-option-a" onclick="answerQuiz('A')">Opção A</button>
                <button class="quiz-option quiz-option-b" onclick="answerQuiz('B')">Opção B</button>
                <button class="quiz-option quiz-option-c" onclick="answerQuiz('C')">Opção C</button>
                <button class="quiz-option quiz-option-d" onclick="answerQuiz('D')">Opção D</button>
            </div>
            <div id="quiz-result"></div>
        </div>

        <div class="game-container">
            <h2>Forca</h2>
            <button onclick="startHangman()">Começar Forca</button>
            <div id="hangman-display"></div>
            <div id="hangman-attempts"></div>
            <div id="hangman-used-letters"></div>
            <div id="hangman-message" class="hangman-message"></div>
            <div class="buttons">
                <button class="hangman-letter" onclick="guessHangman('A')">A</button>
                <button class="hangman-letter" onclick="guessHangman('B')">B</button>
                <button class="hangman-letter" onclick="guessHangman('C')">C</button>
                <button class="hangman-letter" onclick="guessHangman('D')">D</button>
                <button class="hangman-letter" onclick="guessHangman('E')">E</button>
                <button class="hangman-letter" onclick="guessHangman('F')">F</button>
                <button class="hangman-letter" onclick="guessHangman('G')">G</button>
                <button class="hangman-letter" onclick="guessHangman('H')">H</button>
                <button class="hangman-letter" onclick="guessHangman('I')">I</button>
                <button class="hangman-letter" onclick="guessHangman('J')">J</button>
                <button class="hangman-letter" onclick="guessHangman('K')">K</button>
                <button class="hangman-letter" onclick="guessHangman('L')">L</button>
                <button class="hangman-letter" onclick="guessHangman('M')">M</button>
                <button class="hangman-letter" onclick="guessHangman('N')">N</button>
                <button class="hangman-letter" onclick="guessHangman('O')">O</button>
                <button class="hangman-letter" onclick="guessHangman('P')">P</button>
                <button class="hangman-letter" onclick="guessHangman('Q')">Q</button>
                <button class="hangman-letter" onclick="guessHangman('R')">R</button>
                <button class="hangman-letter" onclick="guessHangman('S')">S</button>
                <button class="hangman-letter" onclick="guessHangman('T')">T</button>
                <button class="hangman-letter" onclick="guessHangman('U')">U</button>
                <button class="hangman-letter" onclick="guessHangman('V')">V</button>
                <button class="hangman-letter" onclick="guessHangman('W')">W</button>
                <button class="hangman-letter" onclick="guessHangman('X')">X</button>
                <button class="hangman-letter" onclick="guessHangman('Y')">Y</button>
                <button class="hangman-letter" onclick="guessHangman('Z')">Z</button>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_content)

@app.route('/play_rps', methods=['POST'])
def play_rps():
    data = request.json
    user_choice = data.get('choice')
    choices = ["pedra", "papel", "tesoura"]
    computer_choice = random.choice(choices)

    if user_choice == computer_choice:
        result = "empate"
    elif (user_choice == "pedra" and computer_choice == "tesoura") or \
         (user_choice == "papel" and computer_choice == "pedra") or \
         (user_choice == "tesoura" and computer_choice == "papel"):
        result = "você ganhou"
    else:
        result = "você perdeu"

    return jsonify({"user_choice": user_choice, "computer_choice": computer_choice, "result": result})

@app.route('/guess_number', methods=['POST'])
def guess_number():
    global number_to_guess
    data = request.json
    guess = int(data.get('guess'))
    if guess == number_to_guess:
        message = "Parabéns! Você acertou o número."
        number_to_guess = random.randint(1, 10)  # Novo número para a próxima tentativa
    elif guess < number_to_guess:
        message = "O número é maior!"
    else:
        message = "O número é menor!"

    return jsonify({"message": message})

@app.route('/start_quiz', methods=['GET'])
def start_quiz():
    global current_question, current_answers, current_correct_answer
    questions = [
        {"question": "Qual é a capital da França?", "answers": {"A": "Paris", "B": "Londres", "C": "Berlim", "D": "Madri"}, "correct_answer": "A"},
        {"question": "Qual é a cor do céu em um dia claro?", "answers": {"A": "Verde", "B": "Amarelo", "C": "Azul", "D": "Vermelho"}, "correct_answer": "C"},
        {"question": "Quem escreveu 'Dom Quixote'?", "answers": {"A": "Miguel de Cervantes", "B": "Gabriel García Márquez", "C": "Jorge Luis Borges", "D": "Pablo Neruda"}, "correct_answer": "A"},
    ]
    current_question = random.choice(questions)
    current_answers = current_question["answers"]
    current_correct_answer = current_question["correct_answer"]

    return jsonify({"question": current_question["question"], "answers": current_answers})

@app.route('/answer_quiz', methods=['POST'])
def answer_quiz():
    data = request.json
    user_answer = data.get('answer')
    if user_answer == current_correct_answer:
        message = "Resposta correta!"
    else:
        message = "Resposta errada! A resposta correta era " + current_answers[current_correct_answer]

    return jsonify({"message": message})

@app.route('/start_hangman', methods=['GET'])
def start_hangman():
    global hangman_word, hangman_word_display, hangman_attempts, hangman_used_letters
    words = ["programacao", "desenvolvimento", "flask", "python", "jogo"]
    hangman_word = random.choice(words)
    hangman_word_display = "_" * len(hangman_word)
    hangman_attempts = 6
    hangman_used_letters = []

    return jsonify({"word_display": hangman_word_display, "attempts": hangman_attempts})

@app.route('/guess_hangman', methods=['POST'])
def guess_hangman():
    data = request.json
    letter = data.get('letter').lower()
    if letter in hangman_used_letters:
        return jsonify({"message": "Letra já utilizada", "word_display": hangman_word_display, "attempts": hangman_attempts, "game_over": False})

    hangman_used_letters.append(letter)

    if letter in hangman_word:
        hangman_word_display = "".join([letter if hangman_word[i] == letter else hangman_word_display[i] for i in range(len(hangman_word))])
        if "_" not in hangman_word_display:
            return jsonify({"message": "Parabéns! Você ganhou!", "word_display": hangman_word_display, "attempts": hangman_attempts, "game_over": True})
    else:
        hangman_attempts -= 1
        if hangman_attempts <= 0:
            return jsonify({"message": "Game Over! A palavra era " + hangman_word, "word_display": hangman_word_display, "attempts": hangman_attempts, "game_over": True})

    return jsonify({"message": "", "word_display": hangman_word_display, "attempts": hangman_attempts, "game_over": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
