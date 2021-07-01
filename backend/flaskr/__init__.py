import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    page_questions = questions[start:end]

    return page_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  

  CORS(app,resources={'/':{'origins':'*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, DELETE')
    return response
  
  #Endpoint to handel providing questions for the quiz game
  @app.route('/quiz', methods=['POST'])
  def quiz_questions():

    #Getting the data of previous question and category
    form = request.get_json()
    last_questions = form.get('previous_questions',None)
    category = form.get('quiz_category',None)

    #Checking for errors
    if (category is None) or (last_questions is None):
      abort(400)

    #Getting questions of all categories or a single category
    if (category['id'] == 0):
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=category['id']).all()

    #Making sure questions are not repeated
    next_question = random.choice(questions)
    while next_question.id in last_questions:
      next_question = random.choice(questions)

    #Returning the results
    formated_question = next_question.format()
    return jsonify({
            'success': True,
            'question': formated_question
        }), 200

  #Endpoint to get all questions paginated
  @app.route('/questions')
  def get_paginated_questions():
    try:
      #Getting all questions paginated
      questions = paginate_questions(request,Question.query.all())   
      #Returning the results     
      return jsonify({
            'success': True,
            'total_questions': len(Question.query.all()),
            'categories': {categ.id:categ.type for categ in Category.query.all()},
            'questions': questions
        }), 200
    except:
      abort(404)
    
  #Endpoint to delete question wuth its id
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      #Getting the question and deleting it
      Question.query.get(id).delete()
      #Returning the new number of total questions
      return jsonify({
        'success': True,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422)
  
  #endpoint to search for questions that include the search term
  @app.route('/questions/search', methods=['POST'])
  def search_in_questions():
    try:
      #Getting the search term and checking if it is null
      form = request.get_json()
      searchFor = form.get('searchTerm',None)
      if(not searchFor):
        abort(400)
      #Getting the questions and paginating them.
      questions = Question.query.filter(Question.question.ilike(f'%{searchFor}%'))
      page_questions = paginate_questions(request, questions)
      #returning the results
      return jsonify({
        'questions': page_questions,
        'success': True,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(400)
  
  #Endpoint to return all categories
  @app.route('/categories')
  def get_categories():
    try:
      return jsonify({
          'categories': {categ.id:categ.type for categ in Category.query.all()},
          'success': True
      }), 200
    except Exception:
      abort(500)
  
  #Endpoint to get questions in a specific category
  @app.route('/categories/<int:id>/questions')
  def category_questions(id):
    try:
      #Getting the category and checking for errors
      category = Category.query.filter_by(id=id).one_or_none()
      if(not category):
        abort(404)
      ##Getting the questions in the category
      questions = Question.query.filter_by(category=id)
      page_questions = paginate_questions(request,questions)
      #Returning results
      return jsonify({
          'questions': page_questions,
          'success': True,
          'total_questions': len(Question.query.all()),
          'current_category': category.type
        })
    except:
      abort(404)

  #Endpoint to create a new question
  @app.route('/questions', methods=['POST'])
  def create_new_question():

    try:
      #getting the question form and making sure it is not empty
      form = request.get_json()
      if (not form.get('question',None)or not form.get('answer',None)):
        abort(405)
      
      #Inserting the question
      Question(
        question=form.get('question'),
        answer=form.get('answer'),
        category=form.get('category'),
        difficulty=form.get('difficulty')
      ).insert()
      #Rturning the new total number of questions
      return jsonify({
        'success': True,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(405)
  
  #Creating error handlers for expected errors
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'error': 404,
      'success': False,
      'message': 'Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        'error': 422,
        'success': False,
        'message': 'Unprocessable'
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'error': 500,
      'success': False,
      'message': 'Internal Server Error'
    }), 500

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'error': 405,
      'success': False,
      'message': 'Method Not Allowed'
    }), 405

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'error': 400,
      'success': False,
      'message': 'Bad Request'
    }), 400

  return app
