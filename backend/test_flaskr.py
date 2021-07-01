import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://zyadyasser:zyesl@localhost:5432/trivia"
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    def tearDown(self):
        pass

    #Test for the quizz game if the data was valid
    def test_for_quiz(self):
        #Sending a valid request
        res = self.client().post('/quiz',json={
            'previous_questions': [2],
            'quiz_category': {'type': 'Entertainment', 'id': '5'}
            })
        #Loading the data from the response
        data = json.loads(res.data)
        #Checking if the response was success
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        #Checking if the question is returned and meets the specification which are 
        #being from the same category and not from last questions
        self.assertNotEqual(data['question']['id'], 2)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 5)

    #Testing quiz endpoint if it recives empty request
    def test_for_empty_quiz(self):
        #Sending the empty request and loading the data from the request
        res = self.client().post('/play', json={})
        data = json.loads(res.data)
        #Checking if the reponse if failed and the error 
        #is as expected
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
    
    #Test for loading all the questions paginated
    def test_for_loading_questions(self):
        #Sending request to get all questions and loading data from response
        res = self.client().get('/questions')
        data = json.loads(res.data)
        #Checking if the response is success
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        #Checking if all the data needed is returned
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    #Test for deleting a question
    def test_for_deleting_question(self):
        #Sending requist to delete existing question 
        # and loading data from response
        res = self.client().delete('/questions/19')
        data = json.loads(res.data)
        #Checking if the response is success and the total number of questions is returned
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])

    #Test for deleting question that does not exist
    def test_for_deleting_invalid_question(self):
        #Sending request with non existing id
        res = self.client().delete('/questions/864')
        data = json.loads(res.data)
        #Checking if the response state is false
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    #Test for getting question filtered by category
    def test_for_category_questions(self):
        #Sending request to get questions of category 3 
        # and loading data from response
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
        #Checking if the response state is success
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        #Checking to see if all data is returned
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])

    #Test for category with non existing id
    def test_for_invalid_category_id(self):
        #Sending request with invalid id and loading data
        res = self.client().get('/categories/78/questions')
        data = json.loads(res.data)
        #Checking if the response is flase
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
    
    #Testing the search with valid input
    def test_for_searching(self):
        #Sending the request and loading the data
        res = self.client().post('/questions/search',json={
            'searchTerm': 'movie'
            })
        data = json.loads(res.data)
        #Checking if the response is true
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #checking if the right results is returned
        self.assertEqual(len(data['questions']), 1)
    
    #Test searching with empty search
    def test_for_empty_search(self):
        #sending request with empty body and loading data
        res = self.client().post('/questions/search',json={
            'searchTerm': ''
            })
        data = json.loads(res.data)
        #Checking if the response is false
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    #Test Creating new question
    def test_for_creating_question(self):
        #Sending request with valid data
        res = self.client().post('/questions', json={
            'question': 'what is the color of the sky',
            'answer': 'the sky dont have one color',
            'difficulty': 4,
            'category': '6'
        })
        data = json.loads(res.data)
        #Checking if the response is true
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #Checking if the total number of new questions is returned
        self.assertTrue(data['total_questions'])
    
    #Tset creating question with empty body
    def test_for_creating_empty_question(self):
        #Sending the empty question body and loading response data
        res = self.client().post('/questions', json={
            'question': '',
            'answer': '',
            'difficulty': 4,
            'category': '6'
        })
        data = json.loads(res.data)
        #Checking if the response is false
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()