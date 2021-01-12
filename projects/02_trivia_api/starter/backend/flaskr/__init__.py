import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import func
import random
import re

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_categories(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    categories = [category.format() for category in selection]
    current_categories = categories[start:end]
    return current_categories

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    @TODO: Done
    Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Test home page is working
    @app.route('/')
    def hello():
        return jsonify({
          'success': True,
          'message': 'Home page'
        }), 200

    '''
    @TODO: Done
    Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PUT, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

        # Test cors is working
        # @app.route('/test_cors')
        # @cross_origin()
        # def get_messages():
        #   return 'CORS IS WORKING'

    '''
    @TODO - Done:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():

        categories = Category.query.all()
        formatted_categories = {}

        count_categories = 0

        for category in categories:
            formatted_categories[category.id] = category.type
            count_categories += 1

        return jsonify({
          'success': True,
          'categories': formatted_categories,
          'total_categories': count_categories
        }), 200

    '''
    @TODO - Done:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the
    screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(
          Question.category, Question.id).group_by(
            Question.category, Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.all()

        formatted_categories = {
          category.id: category.type for category in categories
        }

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'current_category': None,
          'categories': formatted_categories
        })

    '''
    @TODO - Done:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question
    will be removed.  This removal will persist in the database and when
    you refresh the page.
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
              'success': True,
              'deleted': id,
              'questions': current_questions,
              'total_questions': len(Question.query.all())
            }), 200

        except Exception:
            abort(422)

    '''
    @TODO - Done:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end
    of the last page of the questions list in the "List" tab.
    '''
    @app.route('/questions/add', methods=['POST'])
    def add_question():

        try:
            data = {
              'question': request.get_json()['question'],
              'answer': request.get_json()['answer'],
              'category': request.get_json()['category'],
              'difficulty': request.get_json()['difficulty']
            }

            if not ('question' in data and 'answer' in data and
                    'category' in data and 'difficulty' in data
                    ):
                abort(422)

            data_category = int(data['category'])
            data_difficulty = int(data['difficulty'])

            if not (1 <= data_category <= 6) and (1 <= data_difficulty <= 4):
                abort(422)

            question = Question(**data)
            question.insert()

            return jsonify({
              'success': True
            }), 200

        except Exception:
            abort(422)

    '''
    @TODO - Done:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/search', methods=['POST'])
    def search_question():
        data = request.get_json()
        if data.get('searchTerm') is not None:
            search_term = data.get('searchTerm')

            try:
                result = Question.query.filter(
                  Question.question.ilike(f'%{search_term}%')).all()

                if len(result) == 0:
                    abort(404)

                formatted_questions = [
                    question.format() for question in result]

                return jsonify({
                  'success': True,
                  'questions': formatted_questions,
                  'total_questions': len(formatted_questions),
                  'current_category': None
                }), 200

            except Exception:
                abort(422)

    '''
    @TODO - Done:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()

        if (category is None):
            abort(404)

        result = Question.query.filter_by(category=id).all()

        if len(result) == 0:
            abort(404)

        formatted_questions = [question.format() for question in result]
        current_questions = paginate_questions(request, result)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(current_questions),
          'current_category': id
        }), 200

    '''
    @TODO - Done:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/play', methods=['POST'])
    def play_quiz():
        # data from previous question by category
        data = request.get_json()
        previous_questions = data.get('previous_questions', None)
        quiz_category = data.get('quiz_category')

        try:
            if not quiz_category:
                abort(422)

            # specific quiz_category is not selected
            if (quiz_category["type"]) == "click":
                selected = Question.query.filter(Question.id.notin_(
                  previous_questions)).order_by(func.random()).limit(1).all()

            else:
                # quiz_category is specified
                selected = Question.query.filter(
                  Question.category == quiz_category["id"]).filter(
                    Question.id.notin_(previous_questions)).order_by(
                      func.random()).limit(1).all()

            # if a question is returned - format it
            if len(selected) != 0:
                selected_question = [
                    question.format() for question in selected]

                # remove brackets from question
                question = selected_question[0]

                result = {
                  'success': True,
                  'question': question
                }
            else:
                result = {
                  'success': True
                }
            return jsonify(result)

        except Exception:
            abort(422)

    '''
    @TODO - Done
    Create error handlers for all expected errors including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "Resource Not Found"
          }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
          }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
          }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
          "success": False,
          "error": 405,
          "message": "Method Not Allowed"
          }), 405

    return app
