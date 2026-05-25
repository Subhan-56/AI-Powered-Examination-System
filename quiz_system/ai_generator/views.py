from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from exams.models import Exam
from questions.models import Question
import re

# ============================================================
# AI MCQ GENERATOR FUNCTION
# ============================================================
def generate_mcqs_with_ai(topic, num_questions=5):
    """
    Hugging Face T5 model se MCQs generate karta hai
    """
    try:
        from transformers import pipeline
        
        # T5 model load karo
        generator = pipeline(
            'text2text-generation',
            model='mrm8488/t5-base-finetuned-question-generation-ap'
        )
        
        questions = []
        
        # Har question ke liye generate karo
        for i in range(num_questions):
            prompt = f"generate question: {topic} concept {i+1}"
            
            result = generator(
                prompt,
                max_length=100,
                num_beams=4,
                early_stopping=True
            )
            
            question_text = result[0]['generated_text']
            
            # MCQ format mein banao
            mcq = {
                'text': question_text,
                'option_a': f'Option A related to {topic}',
                'option_b': f'Option B related to {topic}',
                'option_c': f'Option C related to {topic}',
                'option_d': f'None of the above',
                'correct_answer': 'A',
                'topic': topic
            }
            questions.append(mcq)
        
        return questions, None
        
    except Exception as e:
        return [], str(e)


# ============================================================
# SIMPLE AI GENERATOR (Backup - No Heavy Model Needed)
# ============================================================
def generate_mcqs_simple(topic, num_questions=5):
    import random

    # Topic ko words mein toddo
    topic_words = topic.strip().split()
    topic_title = topic.strip().title()

    # Real MCQ templates — short aur clean
    all_templates = [
        {
            'text': f'What is {topic_title}?',
            'option_a': f'A core concept in computer science',
            'option_b': f'A type of database',
            'option_c': f'A networking protocol',
            'option_d': f'A hardware component',
            'correct_answer': 'A',
        },
        {
            'text': f'Which of the following best defines {topic_title}?',
            'option_a': f'A software testing method',
            'option_b': f'A fundamental programming concept',
            'option_c': f'A type of algorithm only',
            'option_d': f'A cloud service',
            'correct_answer': 'B',
        },
        {
            'text': f'What is the primary use of {topic_title}?',
            'option_a': f'To manage network connections',
            'option_b': f'To design hardware circuits',
            'option_c': f'To improve code quality and efficiency',
            'option_d': f'To monitor system performance',
            'correct_answer': 'C',
        },
        {
            'text': f'Which category does {topic_title} belong to?',
            'option_a': f'Hardware Engineering',
            'option_b': f'Network Administration',
            'option_c': f'Civil Engineering',
            'option_d': f'Software Engineering',
            'correct_answer': 'D',
        },
        {
            'text': f'Who primarily works with {topic_title}?',
            'option_a': f'Software Developers',
            'option_b': f'Mechanical Engineers',
            'option_c': f'Architects',
            'option_d': f'Electricians',
            'correct_answer': 'A',
        },
        {
            'text': f'What is a major benefit of using {topic_title}?',
            'option_a': f'Increases hardware cost',
            'option_b': f'Makes code more complex',
            'option_c': f'Reduces development time',
            'option_d': f'Slows down the system',
            'correct_answer': 'C',
        },
        {
            'text': f'Which tool is used to practice {topic_title}?',
            'option_a': f'Multimeter',
            'option_b': f'VS Code or PyCharm',
            'option_c': f'Network Scanner',
            'option_d': f'Oscilloscope',
            'correct_answer': 'B',
        },
        {
            'text': f'When was {topic_title} first introduced in computing?',
            'option_a': f'In the early days of programming',
            'option_b': f'After the internet was invented',
            'option_c': f'Only in the last 5 years',
            'option_d': f'It has not been introduced yet',
            'correct_answer': 'A',
        },
        {
            'text': f'Which of the following is NOT related to {topic_title}?',
            'option_a': f'Programming logic',
            'option_b': f'Code structure',
            'option_c': f'Building construction',
            'option_d': f'Software design',
            'correct_answer': 'C',
        },
        {
            'text': f'What skill is needed to understand {topic_title}?',
            'option_a': f'Basic programming knowledge',
            'option_b': f'Advanced mathematics only',
            'option_c': f'Network engineering degree',
            'option_d': f'Hardware assembly skills',
            'correct_answer': 'A',
        },
        {
            'text': f'How does {topic_title} help in software development?',
            'option_a': f'It has no role in development',
            'option_b': f'It only works in theory',
            'option_c': f'It replaces all other concepts',
            'option_d': f'It makes development faster and cleaner',
            'correct_answer': 'D',
        },
        {
            'text': f'Which language is commonly used with {topic_title}?',
            'option_a': f'Assembly language only',
            'option_b': f'Python, Java, or C++',
            'option_c': f'HTML only',
            'option_d': f'SQL only',
            'correct_answer': 'B',
        },
    ]

    random.shuffle(all_templates)
    selected = all_templates[:num_questions]

    for q in selected:
     q['topic'] = topic 

    return selected, None


# ============================================================
# MAIN VIEW — AI Question Generation Page
# ============================================================
@login_required
def generate_questions(request, exam_id):
    if not request.user.is_teacher():
        messages.error(request, 'Access denied!')
        return redirect('teacher_dashboard')
    
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        if len(topic) > 50:
            topic = topic[:50]
        num_questions = int(request.POST.get('num_questions', 5))
        use_ai = request.POST.get('use_ai', 'simple')
        
        if not topic:
            messages.error(request, 'Please enter a topic!')
            return render(request, 'ai_generator/generate.html', {'exam': exam})
        
        # Generate questions
        if use_ai == 'advanced':
            questions, error = generate_mcqs_with_ai(topic, num_questions)
        else:
            questions, error = generate_mcqs_simple(topic, num_questions)
        
        if error:
            messages.error(request, f'Error: {error}')
            return render(request, 'ai_generator/generate.html', {'exam': exam})
        
        # Session mein save karo review ke liye
        request.session['ai_questions'] = questions
        request.session['ai_exam_id'] = exam_id
        request.session['ai_topic'] = topic
        
        messages.success(request, f'{len(questions)} questions generated! Review them below.')
        return redirect('review_questions', exam_id=exam_id)
    
    return render(request, 'ai_generator/generate.html', {'exam': exam})


# ============================================================
# REVIEW VIEW — Teacher Reviews AI Questions
# ============================================================
@login_required
def review_questions(request, exam_id):
    if not request.user.is_teacher():
        messages.error(request, 'Access denied!')
        return redirect('teacher_dashboard')
    
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    questions = request.session.get('ai_questions', [])
    
    if not questions:
        messages.warning(request, 'No AI questions found. Generate first!')
        return redirect('generate_questions', exam_id=exam_id)
    
    # Add index to each question
    for i, q in enumerate(questions):
        q['index'] = i
    
    return render(request, 'ai_generator/review.html', {
        'exam': exam,
        'questions': questions
    })


# ============================================================
# APPROVE VIEW — Save Approved Questions
# ============================================================
@login_required
def approve_questions(request, exam_id):
    if not request.user.is_teacher():
        messages.error(request, 'Access denied!')
        return redirect('teacher_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    questions = request.session.get('ai_questions', [])

    if request.method == 'POST':
        approved_count = 0

        for i in range(len(questions)):
            checkbox_value = request.POST.get(f'approve_{i}')
            if checkbox_value:
                text = request.POST.get(f'text_{i}', '').strip()
                option_a = request.POST.get(f'option_a_{i}', '').strip()
                option_b = request.POST.get(f'option_b_{i}', '').strip()
                option_c = request.POST.get(f'option_c_{i}', '').strip()
                option_d = request.POST.get(f'option_d_{i}', '').strip()
                correct = request.POST.get(f'correct_{i}', 'A').strip()

                if text and option_a and option_b and option_c and option_d:
                    Question.objects.create(
                        exam=exam,
                        text=text,
                        option_a=option_a,
                        option_b=option_b,
                        option_c=option_c,
                        option_d=option_d,
                        correct_answer=correct,
                        topic=questions[i].get('topic', ''),
                        is_ai_generated=True,
                        is_approved=True,
                        marks=1
                    )
                    approved_count += 1

        # Total marks update karo
        exam.total_marks = sum(
            q.marks for q in exam.questions.filter(is_approved=True)
        )
        exam.save()

        # Session clear karo
        if 'ai_questions' in request.session:
            del request.session['ai_questions']

        messages.success(
            request,
            f'{approved_count} questions approved and added to exam!'
        )
        return redirect('add_question', exam_id=exam_id)

    return redirect('review_questions', exam_id=exam_id)

