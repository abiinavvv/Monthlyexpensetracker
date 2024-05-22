from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse
from flask_cors import CORS
import werkzeug
from firebase import Firebase
from datetime import datetime, date
from pytz import timezone

x = datetime.now(timezone("Asia/Kolkata"))
time = x.strftime('%d/%m/%Y')
time = x.strftime('%X')

app = Flask(__name__)
api = Api(app)
CORS(app)

config = {
  "apiKey": "AIzaSyCwpZAGJgBRdYpuYxD7OhhJr991uQcEEKc",
  "authDomain": "database-9c6e7.firebaseapp.com",
  "databaseURL": "https://database-9c6e7-default-rtdb.firebaseio.com",
  "storageBucket": "database-9c6e7.appspot.com"
}

config_admin = {
  "apiKey": "AIzaSyCwpZAGJgBRdYpuYxD7OhhJr991uQcEEKc",
  "authDomain": "database-9c6e7.firebaseapp.com",
  "databaseURL": "https://database-9c6e7-default-rtdb.firebaseio.com",
  "storageBucket": "database-9c6e7.appspot.com"
}

firebase=Firebase(config)
db=firebase.database()
storage = firebase.storage()

firebase_admin=Firebase(config)
db_admin=firebase_admin.database()

childName = 'MonthlyExpenseTracker'

familyRegParser=reqparse.RequestParser()
familyRegParser.add_argument('name', type=str, required=True)
familyRegParser.add_argument('address', type=str, required=True)
familyRegParser.add_argument('city', type=str, required=True)
familyRegParser.add_argument('email', type=str, required=True)
familyRegParser.add_argument('password', type=str, required=True)

familyUpdateParser=reqparse.RequestParser()
familyUpdateParser.add_argument('name', type=str)
familyUpdateParser.add_argument('address', type=str)
familyUpdateParser.add_argument('city', type=str)
familyUpdateParser.add_argument('email', type=str)

memberRegParser=reqparse.RequestParser()
memberRegParser.add_argument('familyID', type=str, required=True)
memberRegParser.add_argument('name', type=str, required=True)
memberRegParser.add_argument('gender', type=str, required=True)
memberRegParser.add_argument('dob', type=str, required=True)
memberRegParser.add_argument('relation', type=str, required=True)
memberRegParser.add_argument('email', type=str, required=True)
memberRegParser.add_argument('mobileNumber', type=str, required=True)
memberRegParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files', required=True)

memberUpdateParser=reqparse.RequestParser()
memberUpdateParser.add_argument('name', type=str)
memberUpdateParser.add_argument('gender', type=str)
memberUpdateParser.add_argument('dob', type=str)
memberUpdateParser.add_argument('relation', type=str)
memberUpdateParser.add_argument('email', type=str)
memberUpdateParser.add_argument('mobileNumber', type=str)
memberUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

loginParser=reqparse.RequestParser()
loginParser.add_argument('cat', type=str, required=True)
loginParser.add_argument('username', type=str, required=True)
loginParser.add_argument('password', type=str, required=True)

indFixedExpenseRegParser=reqparse.RequestParser()
indFixedExpenseRegParser.add_argument('memberID', type=str)
indFixedExpenseRegParser.add_argument('name', type=str)
indFixedExpenseRegParser.add_argument('day', type=int)
indFixedExpenseRegParser.add_argument('amount', type=int)

indSpecialExpenseRegParser=reqparse.RequestParser()
indSpecialExpenseRegParser.add_argument('memberID', type=str)
indSpecialExpenseRegParser.add_argument('name', type=str)
indSpecialExpenseRegParser.add_argument('dueDate', type=str)
indSpecialExpenseRegParser.add_argument('amount', type=int)

famFixedExpenseRegParser=reqparse.RequestParser()
famFixedExpenseRegParser.add_argument('memberID', type=str)
famFixedExpenseRegParser.add_argument('name', type=str)
famFixedExpenseRegParser.add_argument('day', type=int)
famFixedExpenseRegParser.add_argument('amount', type=int)

famSpecialExpenseRegParser=reqparse.RequestParser()
famSpecialExpenseRegParser.add_argument('memberID', type=str)
famSpecialExpenseRegParser.add_argument('name', type=str)
famSpecialExpenseRegParser.add_argument('dueDate', type=str)
famSpecialExpenseRegParser.add_argument('amount', type=int)

transactionParser=reqparse.RequestParser()
transactionParser.add_argument('cat', type=str, required=True) #income, expense
transactionParser.add_argument('type', type=str, required=True) #income - normal; expense - transfer, family, ind
transactionParser.add_argument('expID', type=str, required=True)#nil, expID
transactionParser.add_argument('transDate', type=str, required=True)
transactionParser.add_argument('amount', type=int, required=True)
transactionParser.add_argument('name', type=str)

def memberBalanceAmount(memberID):
  memberList = db.child(childName).child('memberList').get().val()
  if memberList == None:
    memberList = {}
  if memberID in memberList:
    if not 'income' in memberList[memberID]:
      memberList[memberID]['income'] = 0
    if not 'transferIncome' in memberList[memberID]:
      memberList[memberID]['transferIncome'] = 0
    if not 'transferExpense' in memberList[memberID]:
      memberList[memberID]['transferExpense'] = 0
    if not 'expense' in memberList[memberID]:
      memberList[memberID]['expense'] = 0
    balanceAmount = (memberList[memberID]['income'] + memberList[memberID]['transferIncome']) - (memberList[memberID]['expense'] + memberList[memberID]['transferExpense'])
    return balanceAmount

def memberTransactions(transDict):
  transactionCnt = db.child(childName).child('transactionCnt').get().val()
  if transactionCnt == None:
    transactionCnt = 0
  transactionCnt += 1
  transID = 'TRANS' + str(transactionCnt + 100)
  db.child(childName).child('transactionCnt').set(transactionCnt)
  transactionList = db.child(childName).child('transactionList').get().val()
  if transactionList == None:
    transactionList = {}
  transactionList[transID] = transDict
  db.child(childName).child('transactionList').set(transactionList)

class FamilyReg(Resource):
  def post(self):
    args=familyRegParser.parse_args()
    familyCnt = db.child(childName).child('familyCnt').get().val()
    if familyCnt == None:
      familyCnt = 0
    familyCnt += 1
    familyID = 'FAM' + str(familyCnt + 100)
    db.child(childName).child('familyCnt').set(familyCnt)
    familyList = db.child(childName).child('familyList').get().val()
    if familyList == None:
      familyList = {}
    familyList[familyID] = args
    db.child(childName).child('familyList').set(familyList)
    return familyList

class FamilyUpdate(Resource):
  def get(self, familyID):
    familyList = db.child(childName).child('familyList').get().val()
    if familyList == None:
      familyList = {}
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not familyID in familyList:
      abort(400, message='family not found')
    else:
      income = 0
      expense = 0
      for i in memberList:
        if memberList[i]['familyID'] == familyID:
          if 'income' in memberList[i]:
            income = income + memberList[i]['income']
          if 'expense' in memberList[i]:
            expense = expense + memberList[i]['expense']
      balanceAmount = income - expense
      familyDetails = familyList[familyID]
      familyDetails['income'] = income
      familyDetails['expense'] = expense
      familyDetails['balanceAmount'] = balanceAmount
      return familyDetails

  def put(self, familyID):
    args=familyUpdateParser.parse_args()
    familyList = db.child(childName).child('familyList').get().val()
    if familyList == None:
      familyList = {}
    if not familyID in familyList:
      abort(400, message='family not found')
    if args['name']:
      familyList[familyID]['name'] = args['name']
    if args['address']:
      familyList[familyID]['address'] = args['address']
    if args['city']:
      familyList[familyID]['city'] = args['city']
    if args['email']:
      familyList[familyID]['email'] = args['email']
    db.child(childName).child('familyList').set(familyList)
    return familyList[familyID]

class MemberReg(Resource):
  def post(self):
    args=memberRegParser.parse_args()
    familyList = db.child(childName).child('familyList').get().val()
    if familyList == None:
      familyList = {}
    if not args['familyID'] in familyList:
      abort(400, message='family not found')
    memberCnt = db.child(childName).child('memberCnt').get().val()
    if memberCnt == None:
      memberCnt = 0
    memberCnt += 1
    memberID = 'MEM' + str(memberCnt + 100)
    db.child(childName).child('memberCnt').set(memberCnt)
    fname = memberID + '.jpg'
    f = args['photo']
    del args['photo']
    storage.child(childName).child('memberImage').child(fname).put(f)
    args['imgUrl'] = storage.child(childName).child('memberImage').child(fname).get_url(None)
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    memberList[memberID] = args
    db.child(childName).child('memberList').set(memberList)
    return memberList

class MemberUpdate(Resource):
  def get(self, memberID):
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    familyList = db.child(childName).child('familyList').get().val()
    if familyList == None:
      familyList = {}
    if not memberID in memberList:
      abort(400, message='member not found')
    memberDetails = memberList[memberID]
    memberDetails['familyDetails'] = familyList[memberDetails['familyID']]
    if not 'income' in memberDetails:
      memberDetails['income'] = 0
    if not 'transferIncome' in memberDetails:
      memberDetails['transferIncome'] = 0
    if not 'transferExpense' in memberDetails:
      memberDetails['transferExpense'] = 0
    if not 'expense' in memberDetails:
      memberDetails['expense'] = 0
    memberDetails['balanceAmount'] = memberBalanceAmount(memberID)
    return memberDetails

  def put(self, memberID):
    args=memberUpdateParser.parse_args()
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not memberID in memberList:
      abort(400, message='member not found')
    if args['name']:
      memberList[memberID]['name'] = args['name']
    if args['gender']:
      memberList[memberID]['gender'] = args['gender']
    if args['dob']:
      memberList[memberID]['dob'] = args['dob']
    if args['relation']:
      memberList[memberID]['relation'] = args['relation']
    if args['email']:
      memberList[memberID]['email'] = args['email']
    if args['mobileNumber']:
      memberList[memberID]['mobileNumber'] = args['mobileNumber']
    if args['photo']:
      fname  = memberID +'.jpg'
      storage.child(childName).child('memberImage').child(fname).put(args['photo'])
      memberList[memberID]['imgUrl']=storage.child(childName).child('memberImage').child(fname).get_url(None)
    db.child(childName).child('memberList').set(memberList)
    return memberList[memberID]

  def delete(self, memberID):
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not memberID in memberList:
      abort(400, message='member not found')
    else:
      del memberList[memberID]
      db.child(childName).child('memberList').set(memberList)
      return memberList

class MemberList(Resource):
  def get(self, familyID):
    familyList = db.child(childName).child('familyList').get().val()
    if familyList == None:
      familyList = {}
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not familyID in familyList:
      abort(400, message='family not found')
    tempMemberList = {}
    for i in memberList:
      if memberList[i]['familyID'] == familyID:
        tempMemberList[i] = memberList[i]
        tempMemberList[i]['balanceAmount'] = memberBalanceAmount(i)
    return tempMemberList

class Login(Resource):
  def post(self):
    args=loginParser.parse_args()
    loginID = ''
    if args['cat'] == 'family':
      familyList = db.child(childName).child('familyList').get().val()
      if familyList == None:
        familyList = {}
      for i in familyList:
        if familyList[i]['email'] == args['username'] and familyList[i]['password'] == args['password']:
          loginID = i
          break
    elif args['cat'] == 'member':
      memberList = db.child(childName).child('memberList').get().val()
      if memberList == None:
        memberList = {}
      for i in memberList:
        if memberList[i]['email'] == args['username'] and memberList[i]['mobileNumber'] == args['password']:
          loginID = i
          break
    else:
      abort(400, message='invalid category')
    return loginID

class IndFixedExpenseReg(Resource):
  def post(self):
    args=indFixedExpenseRegParser.parse_args()
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not args['memberID'] in memberList:
      abort(400, message='member not found')
    if args['day'] > 31 or args['day'] < 1:
      abort(400, message='day not in range')
    if args['amount'] <= 0:
      abort(400, message='amount should not be less than 0')
    expenseCnt = db.child(childName).child('expenseCnt').get().val()
    if expenseCnt == None:
      expenseCnt = 0
    expenseCnt += 1
    expID = 'EXP' + str(expenseCnt + 100)
    db.child(childName).child('expenseCnt').set(expenseCnt)
    indFixedExpense = db.child(childName).child('indFixedExpense').get().val()
    if indFixedExpense == None:
      indFixedExpense = {}
    indFixedExpense[expID] = args
    db.child(childName).child('indFixedExpense').set(indFixedExpense)
    return indFixedExpense

class IndSpecialExpenseReg(Resource):
  def post(self):
    args=indSpecialExpenseRegParser.parse_args()
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not args['memberID'] in memberList:
      abort(400, message='member not found')
    if args['amount'] <= 0:
      abort(400, message='amount should not be less than 0')
    expenseCnt = db.child(childName).child('expenseCnt').get().val()
    if expenseCnt == None:
      expenseCnt = 0
    expenseCnt += 1
    expID = 'EXP' + str(expenseCnt + 100)
    db.child(childName).child('expenseCnt').set(expenseCnt)
    indSpecialExpense = db.child(childName).child('indSpecialExpense').get().val()
    if indSpecialExpense == None:
      indSpecialExpense = {}
    indSpecialExpense[expID] = args
    db.child(childName).child('indSpecialExpense').set(indSpecialExpense)
    return indSpecialExpense

class MemberExpense(Resource):
  def get(self, memberID, cat):
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    indFixedExpense = db.child(childName).child('indFixedExpense').get().val()
    if indFixedExpense == None:
      indFixedExpense = {}
    indSpecialExpense = db.child(childName).child('indSpecialExpense').get().val()
    if indSpecialExpense == None:
      indSpecialExpense = {}
    transactionList = db.child(childName).child('transactionList').get().val()
    if transactionList == None:
      transactionList = {}
    if not memberID in memberList:
      abort(400, message='member not found')
    tempExpense = {}
    if cat == 'fixed':
      for i in indFixedExpense:
        if indFixedExpense[i]['memberID'] == memberID:
          tempExpense[i] = indFixedExpense[i]
    elif cat == 'special':
      tExpense = {}
      for i in indSpecialExpense:
        if indSpecialExpense[i]['memberID'] == memberID:
          tExpense[i] = indSpecialExpense[i]
          if not 'payStatus' in tExpense[i]:
            tExpense[i]['payStatus'] = 'not_paid'
          if tExpense[i]['payStatus'] == 'not_paid':
            currentDate = db.child(childName).child('currentDate').get().val()
            if currentDate == None:
              x = datetime.now(timezone("Asia/Kolkata"))
              d = x.strftime('%d/%m/%Y')
              currentDate = { 'mode' : 1, 'date' : d }
              db.child(childName).child('currentDate').set(currentDate)
            if currentDate['mode'] == 1:
              x = datetime.now(timezone("Asia/Kolkata"))
              presentDate = x.strftime('%d/%m/%Y')
            elif currentDate['mode'] == 0:
              presentDate = currentDate['date']
            dueDate = tExpense[i]['dueDate']
            cDate = date(int(presentDate.split('/')[2]),int(presentDate.split('/')[1]),int(presentDate.split('/')[0]))
            dDate = date(int(dueDate.split('/')[2]),int(dueDate.split('/')[1]),int(dueDate.split('/')[0]))
            dueDays = (dDate - cDate).days
            if dueDays > 0:
              tExpense[i]['dueStatus'] = str(dueDays) + ' days remaining'
            elif dueDays < 0:
              tExpense[i]['dueStatus'] = 'due date passed'
            elif dueDays == 0:
              tExpense[i]['dueStatus'] = 'due date today'
      idList = list(tExpense.keys())
      idList.reverse()
      for i in idList:
        tempExpense[i] = tExpense[i]
    elif cat == 'others':
      tempTransactionList = {}
      for i in transactionList:
        if transactionList[i]['type'] == 'individual' and transactionList[i]['expID'] == 'others' and transactionList[i]['memberID'] == memberID:
          tempTransactionList[i] = transactionList[i]
      idList = list(tempTransactionList.keys())
      idList.reverse()
      for i in idList:
        tempExpense[i] = tempTransactionList[i]
    else:
      abort(400, message='invalid category')
    return tempExpense

class FamFixedExpenseReg(Resource):
  def post(self):
    args=famFixedExpenseRegParser.parse_args()
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not args['memberID'] in memberList:
      abort(400, message='member not found')
    if args['day'] > 31 or args['day'] < 1:
      abort(400, message='day not in range')
    if args['amount'] <= 0:
      abort(400, message='amount should not be less than 0')
    expenseCnt = db.child(childName).child('expenseCnt').get().val()
    if expenseCnt == None:
      expenseCnt = 0
    expenseCnt += 1
    expID = 'EXP' + str(expenseCnt + 100)
    db.child(childName).child('expenseCnt').set(expenseCnt)
    famFixedExpense = db.child(childName).child('famFixedExpense').get().val()
    if famFixedExpense == None:
      famFixedExpense = {}
    famFixedExpense[expID] = args
    db.child(childName).child('famFixedExpense').set(famFixedExpense)
    return famFixedExpense

class FamSpecialExpenseReg(Resource):
  def post(self):
    args=famSpecialExpenseRegParser.parse_args()
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not args['memberID'] in memberList:
      abort(400, message='member not found')
    if args['amount'] <= 0:
      abort(400, message='amount should not be less than 0')
    expenseCnt = db.child(childName).child('expenseCnt').get().val()
    if expenseCnt == None:
      expenseCnt = 0
    expenseCnt += 1
    expID = 'EXP' + str(expenseCnt + 100)
    db.child(childName).child('expenseCnt').set(expenseCnt)
    famSpecialExpense = db.child(childName).child('famSpecialExpense').get().val()
    if famSpecialExpense == None:
      famSpecialExpense = {}
    famSpecialExpense[expID] = args
    db.child(childName).child('famSpecialExpense').set(famSpecialExpense)
    return famSpecialExpense

class FamilyExpense(Resource):
  def get(self, familyID, cat):
    familyList = db.child(childName).child('familyList').get().val()
    if familyList == None:
      familyList = {}
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    famFixedExpense = db.child(childName).child('famFixedExpense').get().val()
    if famFixedExpense == None:
      famFixedExpense = {}
    famSpecialExpense = db.child(childName).child('famSpecialExpense').get().val()
    if famSpecialExpense == None:
      famSpecialExpense = {}
    transactionList = db.child(childName).child('transactionList').get().val()
    if transactionList == None:
      transactionList = {}
    if not familyID in familyList:
      abort(400, message='family not found')
    tempExpense = {}
    if cat == 'fixed':
      for i in famFixedExpense:
        if memberList[famFixedExpense[i]['memberID']]['familyID'] == familyID:
          tempExpense[i] = famFixedExpense[i]
    elif cat == 'special':
      for i in famSpecialExpense:
        if memberList[famSpecialExpense[i]['memberID']]['familyID'] == familyID:
          tempExpense[i] = famSpecialExpense[i]
    elif cat == 'others':
      tempTransactionList = {}
      for i in transactionList:
        if transactionList[i]['type'] == 'family' and transactionList[i]['expID'] == 'others' and memberList[transactionList[i]['memberID']]['familyID'] == familyID:
          tempTransactionList[i] = transactionList[i]
      idList = list(tempTransactionList.keys())
      idList.reverse()
      for i in idList:
        tempExpense[i] = tempTransactionList[i]
    elif cat == 'all':
      tempTransactionList = {}
      for i in transactionList:
        if transactionList[i]['type'] == 'family' and memberList[transactionList[i]['memberID']]['familyID'] == familyID:
          tempTransactionList[i] = transactionList[i]
      idList = list(tempTransactionList.keys())
      idList.reverse()
      for i in idList:
        tempExpense[i] = tempTransactionList[i]
    else:
      abort(400, message='invalid category')
    for i in tempExpense:
      tempExpense[i]['memberDetails'] = memberList[tempExpense[i]['memberID']]
    return tempExpense

class Transaction(Resource):
  def post(self, memberID):
    args=transactionParser.parse_args()
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    if not memberID in memberList:
      abort(400, message='member not found')
    if args['amount'] <= 0:
      abort(400, message='amount should not be less than 0')
    if args['cat'] == 'income':
      if args['type'] == 'normal':
        if not 'income' in memberList[memberID]:
          memberList[memberID]['income'] = 0
        memberList[memberID]['income'] = memberList[memberID]['income'] + args['amount']
      else:
        abort(400, message='invalid type')
    elif args['cat'] == 'expense':
      if args['type'] == 'transfer':
        if not args['expID'] in memberList:
          abort(400, message='receipent not found')
        if memberList[memberID]['familyID'] != memberList[args['expID']]['familyID']:
          abort(400, message='cant transfer money to another family')
        balanceAmount = memberBalanceAmount(memberID)
        if balanceAmount < args['amount']:
          abort(400, message='insufficent balance')
        receipentDict = {
          'memberID'  : args['expID'],
          'cat'       : 'income',
          'type'      : 'transfer',
          'expID'     : memberID,
          'transDate' : args['transDate'],
          'amount'    : args['amount']
        }
        memberTransactions(receipentDict)
        if not 'transferIncome' in memberList[args['expID']]:
          memberList[args['expID']]['transferIncome'] = 0
        memberList[args['expID']]['transferIncome'] = memberList[args['expID']]['transferIncome'] + args['amount']
        if not 'transferExpense' in memberList[memberID]:
          memberList[memberID]['transferExpense'] = 0
        memberList[memberID]['transferExpense'] = memberList[memberID]['transferExpense'] + args['amount']
      elif args['type'] in ['individual', 'family']:
        if args['expID'] == 'others':
          if args['name']:
            if not 'expense' in memberList[memberID]:
              memberList[memberID]['expense'] = 0
            memberList[memberID]['expense'] = memberList[memberID]['expense'] + args['amount']
          else:
            abort(400, message='other expense description required')
        else:
          indSpecialExpense = db.child(childName).child('indSpecialExpense').get().val()
          if indSpecialExpense == None:
            indSpecialExpense = {}
          indFixedExpense = db.child(childName).child('indFixedExpense').get().val()
          if indFixedExpense == None:
            indFixedExpense = {}
          if args['expID'] in indSpecialExpense:
            indSpecialExpense[args['expID']]['paidAmount'] = args['amount']
            indSpecialExpense[args['expID']]['paidDate'] = args['transDate']
            indSpecialExpense[args['expID']]['payStatus'] = 'paid'
            if not 'expense' in memberList[memberID]:
              memberList[memberID]['expense'] = 0
            memberList[memberID]['expense'] = memberList[memberID]['expense'] + args['amount']
            db.child(childName).child('indSpecialExpense').set(indSpecialExpense)
      else:
        abort(400, message='invalid type')
    else:
      abort(400, message='invalid category')
    args['memberID'] = memberID
    memberTransactions(args)
    db.child(childName).child('memberList').set(memberList)

  def get(self, memberID):
    memberList = db.child(childName).child('memberList').get().val()
    if memberList == None:
      memberList = {}
    transactionList = db.child(childName).child('transactionList').get().val()
    if transactionList == None:
      transactionList = {}
    if not memberID in memberList:
      abort(400, message='member not found')
    tempTransactionList = {}
    for i in transactionList:
      if transactionList[i]['memberID'] == memberID:
        tempTransactionList[i] = transactionList[i]
    for i in tempTransactionList:
      if tempTransactionList[i]['type'] == 'transfer':
        tempTransactionList[i]['recepientDetails'] = memberList[tempTransactionList[i]['expID']]
      elif tempTransactionList[i]['type'] == 'individual':
        if tempTransactionList[i]['expID'] != 'others':
          indSpecialExpense = db.child(childName).child('indSpecialExpense').get().val()
          if indSpecialExpense == None:
            indSpecialExpense = {}
          indFixedExpense = db.child(childName).child('indFixedExpense').get().val()
          if indFixedExpense == None:
            indFixedExpense = {}
          if tempTransactionList[i]['expID'] in indSpecialExpense:
            tempTransactionList[i]['name'] = indSpecialExpense[tempTransactionList[i]['expID']]['name']
            tempTransactionList[i]['expenseType'] = 'special'
    idList = list(tempTransactionList.keys())
    idList.reverse()
    tTransactionList = {}
    for i in idList:
      tTransactionList[i] = tempTransactionList[i]
    return tTransactionList

api.add_resource(FamilyReg, '/family')
api.add_resource(FamilyUpdate, '/family/<familyID>')
api.add_resource(MemberReg, '/member')
api.add_resource(MemberUpdate, '/member/<memberID>')
api.add_resource(MemberList, '/memberList/<familyID>')
api.add_resource(Login, '/login')
api.add_resource(IndFixedExpenseReg, '/indFixedExpense')
api.add_resource(IndSpecialExpenseReg, '/indSpecialExpense')
api.add_resource(MemberExpense, '/memberExpense/<memberID>/<cat>')
api.add_resource(FamFixedExpenseReg, '/famFixedExpense')
api.add_resource(FamSpecialExpenseReg, '/famSpecialExpense')
api.add_resource(FamilyExpense, '/familyExpense/<familyID>/<cat>')
api.add_resource(Transaction, '/transaction/<memberID>')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8000)