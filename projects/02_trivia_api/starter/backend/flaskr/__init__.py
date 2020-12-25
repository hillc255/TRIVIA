import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_categories(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  categories = [category.format() for category in selection]
  current_categories = categories[start:end]
  return current_categories

  print(item_to_be_checked)

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

  print(item_to_be_checked)

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  # Test home page is working
  # @app.route('/')
  # def hello():
  #   return jsonify({
  #     'success': True
  #   })

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

  #Test cors is working
  # @app.route('/test_cors')
  # @cross_origin()
  # def get_messages():
  #   return 'CORS IS WORKING'

  '''
  @TODO - ui ok: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  #revised based on 
  #https://knowledge.udacity.com/questions/280959#284132

  @app.route('/categories', methods=['GET']) 
  def get_categories():

    categories = Category.query.all()  
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type
    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(categories)
    })  

    #Test categories endpoint
    #curl http://127.0.0.1:5000/categories
    #curl -X GET http://127.0.0.1:5000/categories
    #curl -X GET http://127.0.0.1:5000/categories?page=1000

  '''
  @TODO - ui ok: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
  
    #query all questions, group by category, id then paginate the questions
    selection = Question.query.order_by(Question.category, Question.id).group_by(Question.category, Question.id).all()
    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
      abort(404)

    #query all the categories
    categories = Category.query.all()

    #format the category items
    formatted_categories = {
      category.id: category.type for category in categories
    }

    if len(current_questions) == 0:
      abort(404)

    #return list of questions ordered by categories and id
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': None,
      'categories': formatted_categories
    }), 200

    #Test questions endpoint
    #curl http://127.0.0.1:5000/questions
    #curl -X GET http://127.0.0.1:5000/questions
    #might not work  - curl -X GET http://127.0.0.1:5000/questions/?page/=1
    #http://127.0.0.1:5000/questions?page=3

  '''
  @TODO - ui ok: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
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

    except:
      abort(422)

    #Test delete endpoint
    #curl -X DELETE http://127.0.0.1:5000/questions/26

  '''
  @TODO - ok: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
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

      #if not data.question:
        #abort(422)
      #if not data.answer:
        #abort(422)

      if data:  
        question = Question(**data)
        question.insert()

        return jsonify({
          'success': True 
        }), 200

    except:
      abort(422)
      
  
#Test add new question
# curl --header "Content-Type: application/json" --request POST --data '{"question":"Test question","answer":"Test answer","category":"1","difficulty":4}' http://127.0.0.1:5000/questions/add
# curl --header "Content-Type: application/json" --request POST --data '{"question":"Test question6","answer":"Test answer6","category":"6","difficulty":6}' http://localhost:3000/questions/add
 
  '''
  @TODO - ok: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
               
    #get searchterm
    data = request.get_json()
    if data.get('searchterm') is not None:
      search_term = data.get('searchterm')
    
      #check search parameter is passed into function
      print('This is searchterm: %s' % search_term)

      try:
        result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    
        #check search result with search_term
        print('This is result: %s' % result)

        formatted_questions = [question.format() for question in result]
        print('This is formatted_questions: %s' % result)

        if len(result) == 0:
          abort(404)

        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(formatted_questions),
          'current_category': None
        })

      except:
        abort(422)

  #test endpoint
  # curl -X POST -H "Content-Type: application/json" -d '{"searchterm":"title"}' http://127.0.0.1:5000/questions/search
  '''
  @TODO - ok: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def get_questions_by_category(id):
        
    print('This is category_id: %s' % id)
    
    #get the category id
    category = Category.query.filter_by(id=id).one_or_none()

    #Test category parameter is passed into function
    print('This is category: %s' % category)

    if (category is None):
      abort(404)

    #get all questions with the category
    result = Question.query.filter_by(category=id).all()

    if len(result) == 0:
      abort(404)

    #get all formatted questions
    formatted_questions = [question.format() for question in result]
    
    print('This is formatted_questions: %s' % result)
    
    #paginate results
    current_questions=paginate_questions(request, result)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': id
    }), 200
    
    #Test selected cateories endpoints
    #curl -X GET http://127.0.0.1:5000/categories/2/questions
    #http://127.0.0.1:5000/categories/2/questions

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  #snippet found here:  https://knowledge.udacity.com/questions/234306
  
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    
    #data from previous question by category
    data = request.get_json()
    previous_questions = data.get('previous_questions', [])
    print('This is previous_questions: %s' % previous_questions)

    #quiz_category = data.get('quiz_category', None)
    quiz_category = data.get('quiz_category')
    print('This is quiz_category: %s' % quiz_category)

    if not quiz_category:
      abort(422)

    result = Question.query.filter(Question.category == quiz_category).filter(
      Question.id.notin_(previous_questions)).order_by(func.random()).limit(1).all()
    
    print('This is random question object: %s' % result)

    #get all formatted question
    formatted_question = [question.format() for question in result]

    if result:       
      return jsonify({
        'success': True,
        'question': formatted_question
      })
    else:
      return jsonify({
        'success': False
      })
  
    
    #Test random question endpoints
    #curl --header "Content-Type: application/json" --request POST --data '{"previous_question": [16,17,18,19,25,27], "quiz_category": "2"}' http://127.0.0.1:5000/quizzes
    #http://127.0.0.1:5000/quizzes
  
  '''
  @TODO - ok: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Resource Not found"
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

    