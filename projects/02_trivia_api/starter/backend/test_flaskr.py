import os
import unittest 
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
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
    TODO - Done
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_given_home_page_behavior(self):
        """Test Home page GET success"""
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)
        json_res = json.loads(res.get_data(as_text=True))
        self.assertEqual('Home page', json_res['message'])

    def test_404_home_page_not_found(self):
        """Test Home page GET error"""
        res = self.client().get('/home')
        self.assertEqual(res.status_code, 404)
        json_res = json.loads(res.get_data(as_text=False))
        self.assertEqual('Resource Not Found', json_res['message'])


    def test_get_categories(self):
      """Test '/categories' GET success"""
      res = self.client().get('/categories')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['categories'])
      self.assertTrue(data['total_categories'])

    def test_404_total_categories_not_equals_seven(self):
      """Test '/categories' GET error"""
      res = self.client().get('/categories/7')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Resource Not Found')


    def test_get_questions(self):
      """Test '/questions' GET success"""
      res = self.client().get('/questions')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])
      self.assertTrue(data['total_questions'])
      self.assertTrue('current_categories', None)
      self.assertTrue(data['categories'])

    def test_405_sent_requesting_invalid_number_questions(self):
      """Test '/questions' GET error"""
      res = self.client().get('/questions/10000')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 405)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Method Not Allowed')

 
    def test_delete_question(self):
      """Test '/questions/<int:id>' DELETE success"""

      #insert question to delete
      self.test_add_question()

      #get id from object of inserted question to be deleted
      selected = Question.query.order_by(desc(Question.id)).limit(1)
      selected_id = [id.format() for id in selected]
      dict = selected_id[0]
      delete_id = dict['id']      

      #pass parameter into url
      param = {'id' : delete_id}
      res = self.client().delete('/questions/{id}'.format(**param))
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)

    def test_404_sent_requesting_invalid_number_questions(self):
      """Test '/questions/<int:id>' DELETE error"""  
      res = self.client().delete('/questions/0')
      data = json.loads(res.data)    
      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Resource Not Found')


    def test_add_question(self):
      """Test /questions/add' POST success"""         
      data = {
        'question':'Test Question',
        'answer':'Test Answer',
        'category':'2',
        'difficulty':'1'
      }         
      res = self.client().post('/questions/add', 
      data=json.dumps(data),
      content_type='application/json')
      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      json_res = json.loads(res.get_data(as_text=True))

    def test_422_invalid_category_payload(self):
      """Test /questions/add' POST error"""         
      data = {
        'question':'Test Question',
        'answer':'Test Answer',
        'category':'10',
        'difficulty':'1'
      }     
      res = self.client().post('/questions/add', 
      data=json.dumps(data),
      content_type='application/json')
      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 422)
      json_res = json.loads(res.get_data(as_text=False))


    def test_search_question(self):
      """Test '/search' POST success"""          
      data = {'searchTerm':'title'}
      res = self.client().post('/search', 
      data=json.dumps(data),
      content_type='application/json')
      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      json_res = json.loads(res.get_data(as_text=True))

    def test_404_search_results_unprocesssable(self):
      """Test '/search' POST error"""
      data = {'searchTerm':'wxyz'}
      res = self.client().post('/search', 
      data=json.dumps(data),
      content_type='application/json')
      self.data = json.loads(res.data)
      self.assertEqual(res.status_code, 404)
      json_res = json.loads(res.get_data(as_text=False))


    def test_get_questions_by_category(self):
      """Test '/categories/<int:id>/questions' GET success"""
      res = self.client().get('/categories/6/questions')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])
      self.assertTrue(data['current_category'], 6)
  
    def test_404_invalid_categories(self):
      """Test '/categories/<int:id>/questions' GET error"""
      res = self.client().get('/categories/1000/questions')
      data = json.loads(res.data)
      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Resource Not Found')


    def test_post_play_quiz(self):
      """Test '/play', POST success""" 
      data = {'previous_questions': '2', 'quiz_category': {'id':'1','type':'Science'}}
      res = self.client().post('/play', 
      data=json.dumps(data),
      content_type='application/json')
      self.assertEqual(res.status_code, 200)
      json_res = json.loads(res.get_data(as_text=True))

    def test_422_invalid_play_quiz(self):
      """Test '/play', POST error""" 
      data = {'previous_questions': '2', 'quiz_category': {}}
      res = self.client().post('/play', 
      data=json.dumps(data),
      content_type='application/json')
      self.assertEqual(res.status_code, 422)
      json_res = json.loads(res.get_data(as_text=False))

# Make the tests conveniently executable
if __name__ == "__main__":
  unittest.main()