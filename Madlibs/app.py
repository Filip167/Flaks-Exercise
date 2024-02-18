from flask import Flask, request, render_template
from stories import story

app = Flask(__name__)

@app.route('/home', methods=['GET'])
def home():
    prompts = story.prompts
    return render_template('home.html', prompts=prompts)

@app.route('/story', methods=['POST'])
def show_story():
    answers = {prompt: request.form[prompt] for prompt in story.prompts}
    story_text = story.generate(answers)
    return render_template('story.html', story = story_text)
