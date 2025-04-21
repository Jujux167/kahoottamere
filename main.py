import os
from tkinter import Button, Label, Tk, Entry, StringVar, Text, Frame, Listbox, Scrollbar, Canvas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import json
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from termcolor import colored
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class GUI:
    def __init__(self, driver):
        self.root = Tk()
        self.root.title("KahootAssist")
        self.root.resizable(False, False)
        self.root.geometry('800x600')
        self.root.configure(bg='#23272A')

        self.driver = driver
        self.kahoot_url = StringVar(value="https://kahoot.it/")
        self.ollama_model = StringVar(value="Qwen2.5:7b")
        self.prompt_template = StringVar(
            value="Réponds à la question suivante en choisissant la bonne réponse parmi les options. Question: {question} Options: {options}, tu n'ecrira uniquement la reponse seule dans ta réponse")
        self.prompt_template_multiple = StringVar(
            value="Pour la question suivante, donne toutes les réponses correctes séparées par '/'. Question: {question} Options: {options}, tu n'ecrira uniquement les reponses séparées par des / dans ta réponse")
        self.auto_answer_on = False
        self.highlight_on = False
        self.current_question_data = None
        self.correct_answer = ""
        self.question_type = None

        self.ollama_label = Label(self.root, text="Ollama Model:", bg="#23272A", fg="#ffffff", font=('Helvetica', '10'))
        self.ollama_entry = Entry(self.root, textvariable=self.ollama_model, bg="#2C2F33", fg="#ffffff", width=20, bd=1,
                                    font=('Helvetica', '10'))
        self.prompt_label = Label(self.root, text="Prompt Template:", bg="#23272A", fg="#ffffff",
                                        font=('Helvetica', '10'))
        self.prompt_text = Text(self.root, bg="#2C2F33", fg="#ffffff", width=50, height=3, bd=1, font=('Helvetica', '10'))
        self.prompt_text.insert("1.0", self.prompt_template.get())

        # Auto Answer Toggle Button
        self.auto_answer_frame = Frame(self.root, bg="#23272A")
        self.auto_answer_label = Label(self.auto_answer_frame, text="Auto Answer:", bg="#23272A", fg="#ffffff",
                                            font=('Helvetica', '10'))
        self.auto_answer_toggle_state = StringVar(value="OFF")
        self.auto_answer_button = Button(self.auto_answer_frame, textvariable=self.auto_answer_toggle_state,
                                            command=self.toggle_auto_answer_ui, bg="red", fg="white", width=8,
                                            font=('Helvetica', '10', "bold"))

        # Highlight Answer Toggle Button
        self.highlight_frame = Frame(self.root, bg="#23272A")
        self.highlight_label = Label(self.highlight_frame, text="Highlight Answer:", bg="#23272A", fg="#ffffff",
                                         font=('Helvetica', '10'))
        self.highlight_toggle_state = StringVar(value="OFF")
        self.highlight_button = Button(self.highlight_frame, textvariable=self.highlight_toggle_state,
                                            command=self.toggle_highlight_ui, bg="red", fg="white", width=8,
                                            font=('Helvetica', '10', "bold"))

        # Multiple Answer Indicator
        self.multiple_answer_frame = Frame(self.root, bg="#23272A")
        self.multiple_answer_label = Label(self.multiple_answer_frame, text="Multiple Answers:", bg="#23272A",
                                                 fg="#ffffff", font=('Helvetica', '10'))
        self.multiple_answer_indicator = Canvas(self.multiple_answer_frame, width=20, height=20, bg="red", bd=0,
                                                    highlightthickness=0)

        # Ollama Question Input
        self.ollama_question_label = Label(self.root, text="Ask Ollama:", bg="#23272A", fg="#ffffff",
                                                font=('Helvetica', '10'))
        self.ollama_question_entry = Entry(self.root, bg="#2C2F33", fg="#ffffff", width=40, bd=1, font=('Helvetica', '10'))
        self.ollama_response_text = Text(self.root, bg="#2C2F33", fg="#ffffff", width=50, height=3, bd=1,
                                            font=('Helvetica', '10'), state="disabled")
        self.send_ollama_button = Button(self.root, text="Send", command=self.send_custom_ollama_query, bg="#a2d417",
                                            highlightthickness=2, bd=0, height=1, width=8, font=('Helvetica', '10', "bold"))
        self.send_answers_button = Button(self.root, text="Envoyer", command=self.send_kahoot_answers, bg="#a2d417",
                                            highlightthickness=2, bd=0, height=1, width=8, font=('Helvetica', '10', "bold")) #new send button

        # Possible Answers Display
        self.answers_frame = Frame(self.root, bg="#2C2F33", bd=2, relief="groove")
        self.answers_label = Label(self.answers_frame, text="Possible Answers (Scraped):", bg="#2C2F33", fg="#ffffff",
                                        font=('Helvetica', '10', 'bold'))
        self.answers_scrollbar = Scrollbar(self.answers_frame)
        self.answers_listbox = Listbox(self.answers_frame, bg="#36393F", fg="#ffffff",
                                            yscrollcommand=self.answers_scrollbar.set, font=('Helvetica', '10'))
        self.answers_scrollbar.config(command=self.answers_listbox.yview)

        self.good_answer_frame = Frame(self.root, bg="#2C2F33", bd=2, relief="groove")
        self.good_answer_label = Label(self.good_answer_frame, text="Good Answer:", bg="#2C2F33", fg="#ffffff",
                                         font=('Helvetica', '10', 'bold'))
        self.good_answer_text = Text(self.good_answer_frame, bg="#36393F", fg="#ffffff", height=2,
                                        font=('Helvetica', '10'), state="disabled")

        # Sent Prompt Display
        self.prompt_display_frame = Frame(self.root, bg="#2C2F33", bd=2, relief="groove")
        self.prompt_display_label = Label(self.prompt_display_frame, text="Prompt Sent to Ollama:", bg="#2C2F33",
                                             fg="#ffffff", font=('Helvetica', '10', 'bold'))
        self.prompt_display_text = Text(self.prompt_display_frame, bg="#36393F", fg="#ffffff", height=5,
                                            font=('Helvetica', '10'), state="disabled")

        self.btn_quit = Button(self.root, text="Quitter", command=self.root.destroy, bg="#23272A",
                                    activebackground="#23272A", bd=0)

        self.setup_ui()
        self.open_kahoot_direct()
        self.root.after(1000, self.monitor_kahoot)

    def setup_ui(self):
        self.ollama_label.place(x=20, y=20)
        self.ollama_entry.place(x=150, y=20)
        self.prompt_label.place(x=20, y=60)
        self.prompt_text.place(x=150, y=60)

        self.auto_answer_frame.place(x=20, y=180)
        self.auto_answer_label.pack(side="left")
        self.auto_answer_button.pack(side="left", padx=5)

        self.highlight_frame.place(x=300, y=180)
        self.highlight_label.pack(side="left")
        self.highlight_button.pack(side="left", padx=5)

        self.multiple_answer_frame.place(x=450, y=180)
        self.multiple_answer_label.pack(side="left")
        self.multiple_answer_indicator.pack(side="left", padx=5)

        self.ollama_question_label.place(x=20, y=230)
        self.ollama_question_entry.place(x=150, y=230)
        self.send_ollama_button.place(x=450, y=225)
        self.ollama_response_text.place(x=20, y=270, width=560, height=60)
        self.send_answers_button.place(x=450, y=500) # Placed the send button

        self.answers_frame.place(x=600, y=20, width=180, height=300)
        self.answers_label.pack(pady=5)
        self.answers_listbox.pack(side="left", fill="y", expand=True)
        self.answers_scrollbar.pack(side="right", fill="y")

        self.good_answer_frame.place(x=600, y=340, width=180, height=80)
        self.good_answer_label.pack(pady=5)
        self.good_answer_text.pack(fill="both", expand=True)

        self.prompt_display_frame.place(x=20, y=340, width=560, height=150)
        self.prompt_display_label.pack(pady=5)
        self.prompt_display_text.pack(fill="both", expand=True)

        self.btn_quit.place(x=700, y=560)

    def open_kahoot_direct(self):
        url = self.kahoot_url.get()
        try:
            self.driver.get(url)
        except Exception as e:
            print(f"Error opening URL: {e}")

    def toggle_auto_answer_ui(self):
        self.auto_answer_on = not self.auto_answer_on
        state = "ON" if self.auto_answer_on else "OFF"
        color = "green" if self.auto_answer_on else "red"
        self.auto_answer_toggle_state.set(state)
        self.auto_answer_button.config(bg=color)
        print(f"Auto answer {state}")

    def toggle_highlight_ui(self):
        self.highlight_on = not self.highlight_on
        state = "ON" if self.highlight_on else "OFF"
        color = "green" if self.highlight_on else "red"
        self.highlight_toggle_state.set(state)
        self.highlight_button.config(bg=color)
        print(f"Highlight {state}")

    def update_kahoot_info(self):
        if self.running:
            data = self.get_kahoot_data()
            if data:
                if data["screen_type"] == "question":
                    self.question_label.config(text=f"Question: {data['question']}")
                    if len(data['options']) == len(self.answer_buttons):
                        for i, option_text in enumerate(data['options']):
                            self.answer_buttons[i].config(text=option_text)
                    else:
                        print(colored("Number of options doesn't match number of buttons!", "yellow"))
                elif data["screen_type"] == "time_up":
                    self.question_label.config(text="Time's Up!")
                    for button in self.answer_buttons:
                        button.config(text="")
                elif data["screen_type"] == "unknown":
                    self.question_label.config(text="Waiting for Kahoot! data...")
                    for button in self.answer_buttons:
                        button.config(text="")
                else:
                    print(colored(f"Unknown screen type: {data['screen_type']}", "yellow"))
            else:
                self.question_label.config(text="Error fetching Kahoot! data.")
                for button in self.answer_buttons:
                    button.config(text="")

        self.root.after(1000, self.update_kahoot_info)

    def send_to_ollama(self, prompt):
        model = self.ollama_model.get()
        url = "http://localhost:11434/api/generate"
        payload = {
            "prompt": prompt,
            "model": model,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json().get('response', '').strip()
            return result
        except requests.exceptions.RequestException as e:
            error_message = f"Ollama API error: {e}"
            if response is not None:
                error_message += f" - Status Code: {response.status_code}, Text: {response.text}"
            print(colored(error_message, "red"))
            return None

    def update_ollama_response(self, response):
        self.ollama_response_text.config(state="normal")
        self.ollama_response_text.delete("1.0", "end")
        self.ollama_response_text.insert("1.0", response)
        self.ollama_response_text.config(state="disabled")

    def update_sent_prompt_display(self, prompt):
        self.prompt_display_text.config(state="normal")
        self.prompt_display_text.delete("1.0", "end")
        self.prompt_display_text.insert("1.0", prompt)
        self.prompt_display_text.config(state="disabled")

    def send_custom_ollama_query(self):
        question = self.ollama_question_entry.get()
        if question:
            response = self.send_to_ollama(question)
            if response:
                self.update_ollama_response(response)
        self.ollama_question_entry.delete(0, "end")

    def process_ollama_response(self, response, options, elements):
        if response:
            print(colored(f"Ollama Response (Auto): {response}", "green"))
            best_match_index = -1
            max_similarity = 0
            for i, option in enumerate(options):
                similarity = self.calculate_similarity(response.lower(), option.lower())
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_index = i

            if best_match_index != -1:
                self.correct_answer = options[best_match_index]
                self.update_good_answer(self.correct_answer)
                print(colored(f"Best match (Auto): {options[best_match_index]} (similarity: {max_similarity:.2f})",
                              "cyan"))
                if self.highlight_on:
                    for i, element in enumerate(elements):
                        if i == best_match_index:
                            self.driver.execute_script("arguments[0].style.backgroundColor = 'green';", element)
                        else:
                            self.driver.execute_script("arguments[0].style.backgroundColor = 'red';", element)
                else:
                    for i, element in enumerate(elements):
                        self.driver.execute_script("arguments[0].style.backgroundColor = '';", element)

                if self.auto_answer_on and elements and len(elements) > best_match_index:
                    try:
                        elements[best_match_index].click()
                        print(colored(f"Clicked answer (Auto): {options[best_match_index]}", "blue"))
                    except Exception as e:
                        print(colored(f"Error clicking answer (Auto): {e}", "red"))
            else:
                self.correct_answer = "No match found"
                self.update_good_answer("No match found")
                print(colored("Could not find a suitable answer in Ollama's response (Auto).", "yellow"))

    def calculate_similarity(self, str1, str2):
        set1 = set(str1.split())
        set2 = set(str2.split())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        if not union:
            return 0
        return len(intersection) / len(union)

    def get_kahoot_data(self):
        try:
            question_element = self.driver.find_element(By.CSS_SELECTOR, '[data-functional-selector="block-title"]')
            question = question_element.text.strip() if question_element else None

            option_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                        '.quiz-choices__Row-sc-1ddvqeu-1 button[data-functional-selector^="answer-"]')
            options = []
            clickable_elements = []
            for element in option_elements:
                try:
                    text_element = element.find_element(By.CSS_SELECTOR,
                                                        'div[data-functional-selector^="question-choice-text-"] p')
                    options.append(text_element.text.strip())
                    clickable_elements.append(element)
                except:
                    try:
                        text_element = element.find_element(By.CSS_SELECTOR,
                                                                        '.centered-floated-text__ChoiceText-sc-wq1dlx-6')
                        options.append(text_element.text.strip())
                        clickable_elements.append(element)
                    except:
                        print(colored("Could not find text in an answer button.", "yellow"))
            self.question_type = "multiple choice"  # set question type
            return {
                "question": question,
                "options": options,
                "elements": clickable_elements
            }
        except Exception as e:
            print(f"Error in get_kahoot_data: {e}")
            return None

    def monitor_kahoot(self):
        if self.driver.current_url.startswith("https://kahoot.it/gameblock"):
            try:
                # Check for the "Select all that apply" button.
                send_button_present = False
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR,
                                                              'button[data-functional-selector="send-answers-button"]')
                    send_button_present = True
                except NoSuchElementException:
                    pass  # No send button, so it's a single-choice question.

                question_element = self.driver.find_element(By.CSS_SELECTOR, '[data-functional-selector="block-title"]')
                if question_element:
                    current_data = self.get_kahoot_data()
                    if current_data and current_data != self.current_question_data:
                        self.current_question_data = current_data
                        question = current_data["question"]
                        options = current_data["options"]
                        print(f"Possible Answers (Scraped): {options}")
                        self.update_possible_answers_listbox(options)
                        if send_button_present:
                            prompt = self.prompt_template_multiple.get().format(question=question,
                                                                                  options=", ".join(options))
                            self.multiple_answer_indicator.config(bg="green")
                        else:
                            prompt = self.prompt_template.get().format(question=question, options=", ".join(options))
                            self.multiple_answer_indicator.config(bg="red")
                        print(f"Prompt sent to Ollama (Auto): {prompt}")
                        self.update_sent_prompt_display(prompt)
                        ollama_response = self.send_to_ollama(prompt)

                        if ollama_response is None:
                            print("Waiting for Ollama response...")
                            while ollama_response is None:
                                time.sleep(0.1)
                                ollama_response = self.send_to_ollama(prompt)
                        if send_button_present:  # Handle multiple choice questions
                            print("Handling multiple choice question...")
                            # Ask Ollama for the number of answers and which ones.
                            prompt_multi = f"For the following question and options, provide your answer.  If there are multiple answers, provide them as a comma separated list. Question: {question} Options: {options}."
                            ollama_response_multi = self.send_to_ollama(prompt_multi)
                            if ollama_response_multi:
                                print(f"Ollama Response (Multi): {ollama_response_multi}")
                                self.update_ollama_response(ollama_response_multi)  # show response
                                answers_to_click = [ans.strip() for ans in
                                                    ollama_response_multi.split(',')]  # get list of answers
                                elements = current_data["elements"]
                                # Find and click the corresponding answer elements.
                                clicked_count = 0;
                                for i, option_text in enumerate(options):
                                    if any(self.calculate_similarity(ans.lower(), option_text.lower()) > 0.8 for ans in
                                           answers_to_click):
                                        try:
                                            elements[i].click()
                                            print(colored(f"Clicked answer (Multi): {option_text}", "blue"))
                                            clicked_count += 1
                                        except Exception as e:
                                            print(colored(f"Error clicking answer (Multi): {e}", "red"))
                                if clicked_count > 0:
                                    try:
                                        self.send_kahoot_answers() # Call the function to send answers
                                        print(colored("Clicked the Send Answers button.", "blue"))
                                    except Exception as e:
                                        print(colored(f"Error clicking send button: {e}", "red"))
                                else:
                                    print(colored("No matching answers found to click.", "yellow"))
                        else:
                            self.process_ollama_response(ollama_response, options, current_data["elements"])
                    elif self.highlight_on and current_data and not self.auto_answer_on:
                        elements = current_data["elements"]
                        ollama_response = self.send_to_ollama(self.prompt_template.get().format(
                            question=self.current_question_data["question"],
                            options=", ".join(self.current_question_data["options"])
                        ))
                        if ollama_response:
                            best_match_index = -1
                            max_similarity = 0
                            for i, option in enumerate(self.current_question_data["options"]):
                                similarity = self.calculate_similarity(ollama_response.lower(), option.lower())
                                if similarity > max_similarity:
                                    max_similarity = similarity
                                    best_match_index = i
                            if best_match_index != -1 and len(elements) > best_match_index:
                                self.correct_answer = self.current_question_data["options"][best_match_index]
                                self.update_good_answer(self.correct_answer)
                                for i, element in enumerate(elements):
                                    if i != best_match_index:
                                        self.driver.execute_script("arguments[0].style.backgroundColor = 'red';",
                                                                    element)
                                    else:
                                        self.driver.execute_script(
                                            "arguments[0].style.backgroundColor = 'green';",
                                            element)
                            else:
                                self.update_good_answer("No match found")
                                for element in elements:
                                    self.driver.execute_script("arguments[0].style.backgroundColor = '';", element)
            except Exception as e:
                print(f"Error in monitor_kahoot: {e}")
                pass

        self.root.after(1000, self.monitor_kahoot)

    def update_possible_answers_listbox(self, answers):
        self.answers_listbox.delete(0, "end")
        for answer in answers:
            self.answers_listbox.insert("end", answer)

    def update_good_answer(self, answer):
        self.good_answer_text.config(state="normal")
        self.good_answer_text.delete("1.0", "end")
        self.good_answer_text.insert("1.0", answer)
        self.good_answer_text.config(state="disabled")

    def update_sent_prompt_display(self, prompt):
        self.prompt_display_text.config(state="normal")
        self.prompt_display_text.delete("1.0", "end")
        self.prompt_display_text.insert("1.0", prompt)
        self.prompt_display_text.config(state="disabled")

    def send_kahoot_answers(self):
        print("send_kahoot_answers: Function called")  # Debug: Fonction appelée
        try:
            send_button = self.driver.find_element(By.CSS_SELECTOR,
                                                   'button[data-functional-selector="send-answers-button"]')
            print(
                f"send_kahoot_answers: Send button found - Enabled: {send_button.is_enabled()}")  # Debug: Bouton trouvé
            if send_button.is_enabled():
                send_button.click()
                print("send_kahoot_answers: Send button clicked")  # Debug: Bouton cliqué
            else:
                print("send_kahoot_answers: Send button is disabled")  # Debug: Bouton désactivé
        except Exception as e:
            print(f"send_kahoot_answers: Error - {e}")  # Debug: Erreur


if __name__ == "__main__":
    options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    gui = GUI(driver)
    gui.root.mainloop()

    driver.quit()

