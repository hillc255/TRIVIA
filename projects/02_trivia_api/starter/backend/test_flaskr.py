import os
import unittest 
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format('postgres','picasso0', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

################################################################
#tests client request and evaluate response

    def test_given_behavior(self):
        """Test _____________ """
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)

################################################################
#test '/categories' GET

    #success
    def test_get_categories(self):
      res = self.client().get('/categories')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['categories'])
      self.assertTrue(len('categories'))

    #error
    def test_404_total_categories_not_equals_seven(self):
      res = self.client().get('/categories/7')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Resource Not found')

################################################################
#test '/questions' GET

    #success
    def test_get_questions(self):
      res = self.client().get('/questions')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])
      self.assertTrue(len('categories'))

    #error  
    def test_405_sent_requesting_invalid_number_questions(self):
      res = self.client().get('/questions/10000')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 405)
      self.assertEqual(data['success'], False)

################################################################
#test '/questions/<int:id>' DELETE

    #success 
    # def test_delete_question(self):
    #   id = 11
    #   res = self.client().delete('/questions/id')
    #   data = json.loads(res.data)

    #   question = Question.query.filter(Question.id == id).one_or_none()

    #   self.assertEqual(res.status_code, 200)
    #   self.assertEqual(data['success'], True)

    #error  
    def test_404_sent_requesting_invalid_number_questions(self):
      id = 11
      res = self.client().delete('/questions/id')
      data = json.loads(res.data)

      question = Question.query.filter(Question.id == id).all()

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)

################################################################
#test '/questions/add' POST

    # success
    def test_add_question(self):
          
      data = {
        'question':'New Question',
        'answer':'New Answer',
        'category':'2',
        'difficulty':'1'
      }
          
      res = self.client().post('/questions/add', 
      data=json.dumps(data),
      content_type='application/json')

      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      json_res = json.loads(res.get_data(as_text=True))

    # error
    def test_404_invalid_category_payload(self):
              
      data = {
        'question':'New Question',
        'answer':'New Answer',
        'category':'10',
        'difficulty':'1'
      }
          
      res = self.client().post('/questions/add', 
      data=json.dumps(data),
      content_type='application/json')

      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 422)
      json_res = json.loads(res.get_data(as_text=False))

################################################################
# test '/search' POST

    # success
    def test_search_question(self):
          
      data = {
        'searchTerm':'title',
      }

      res = self.client().post('/search', 
      data=json.dumps(data),
      content_type='application/json')

      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      json_res = json.loads(res.get_data(as_text=True))

    # error
    def test_422_search_results_unprocesssable(self):

      data = {
        'searchTerm':'wxyz',
      }

      res = self.client().post('/search', 
      data=json.dumps(data),
      content_type='application/json')

      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 422)
      json_res = json.loads(res.get_data(as_text=False))

################################################################
# test /categories/<int:id>/questions' GET

    # success
    def test_get_questions_by_categories(self):
      res = self.client().get('/categories/<int:id>/questions')

      # id = 6

      # data = json.loads(res.data)
      # self.assertEqual(res.status_code, 200)
      # self.assertEqual(data['success'], True)
      # self.assertTrue(data['questions'])
      # self.assertTrue(len('categories'))

    #error  
    # def test_405_invalid_categories(self):
    #   res = self.client().get('/questions/10000')
    #   data = json.loads(res.data)
    #   self.assertEqual(res.status_code, 405)
    #   self.assertEqual(data['success'], False)

################################################################

print("hello first")

# Make the tests conveniently executable
if __name__ == "__main__":
  print("hello second")
  unittest.main()