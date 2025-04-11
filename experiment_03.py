import telebot
import random
import requests
import config
import tasks
from difflib import SequenceMatcher

# Токен Telegram бота
BOT_TOKEN = config.token


class MedicalExamBot:
    def __init__(self, tasks):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.tasks = tasks
        self.user_sessions = {}

        @self.bot.message_handler(commands=['start'])
        def start_exam(message):
            user_id = message.from_user.id
            self.user_sessions[user_id] = {
                'selected_tasks': random.sample(self.tasks, 5),
                'current_task_index': 0,
                'current_question_index': 0,
                'answers': [],
                'correct_answers': 0
            }
            self.send_next_question(message)

        @self.bot.message_handler(func=lambda message: True)
        def handle_answer(message):
            self.process_student_answer(message)

    def send_next_question(self, message):
        user_id = message.from_user.id
        session = self.user_sessions.get(user_id)
        
        if session and session['current_task_index'] < len(session['selected_tasks']):
            task = session['selected_tasks'][session['current_task_index']]
            case_text = task['case']
            current_question_index = session['current_question_index']

            if current_question_index < len(task['questions']):
                question = task['questions'][current_question_index]
                self.bot.send_message(user_id, f"Текст задачи:\n{case_text}")
                self.bot.send_message(user_id, f"Задача {session['current_task_index'] + 1}, Вопрос {current_question_index + 1}:\n{question}")
            else:
                session['current_task_index'] += 1
                session['current_question_index'] = 0
                self.send_next_question(message)
        else:
            self.calculate_final_grade(message)

    def process_student_answer(self, message):
        user_id = message.from_user.id
        session = self.user_sessions.get(user_id)
        
        if session:
            task = session['selected_tasks'][session['current_task_index']]
            current_question_index = session['current_question_index']
            correct_answer = task['answers'][current_question_index]
            student_answer = message.text

            similarity = self.check_answer_similarity(student_answer, correct_answer)
            if similarity >= 0.6:
                session['answers'].append(True)
                session['correct_answers'] += 1
                self.bot.send_message(user_id, "Верно! ✅")
            else:
                session['answers'].append(False)
                self.bot.send_message(user_id, f"Неверно! ❌\nПравильный ответ: {correct_answer}")

            session['current_question_index'] += 1
            if session['current_question_index'] >= len(task['questions']):
                session['current_task_index'] += 1
                session['current_question_index'] = 0

            self.send_next_question(message)
        else:
            self.bot.send_message(user_id, "Ваша сессия была сброшена. Нажмите /start для начала.")

    def check_answer_similarity(self, student_answer, correct_answer):
        # Используем SequenceMatcher для определения схожести строк
        similarity = SequenceMatcher(None, student_answer.lower(), correct_answer.lower()).ratio()
        return similarity

    def calculate_final_grade(self, message):
        user_id = message.from_user.id
        session = self.user_sessions.get(user_id)
        
        if session:
            total_questions = sum(len(task['questions']) for task in session['selected_tasks'])
            correct_answers = session['correct_answers']
            score = (correct_answers / total_questions) * 100

            self.bot.send_message(user_id, f"Экзамен завершён! 🎉\nВы ответили правильно на {correct_answers} из {total_questions} вопросов.\nВаш результат: {score:.2f}%")
            del self.user_sessions[user_id]
    
    def run(self):
        self.bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    exam_tasks = tasks.medical_tasks
    bot = MedicalExamBot(exam_tasks)
    bot.run()