from flask import Flask,render_template, request, make_response, redirect, url_for,session
import requests
from datetime import datetime
from pytz import timezone

app=Flask(__name__)
app.secret_key='abcd'

base_url='http://127.0.0.1:8000'

@app.route('/')
def home():
	if 'family' in session:
		familyID = session['family']
		response = requests.get(base_url+'/family/' + familyID)
		familyDetails = response.json()
		response = requests.get(base_url+'/memberList/' + familyID)
		memberList = response.json()
		return render_template('family_home.html', familyDetails=familyDetails, memberList=memberList)
	elif 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		return render_template('member_home.html', memberDetails=memberDetails)
	else:
		return render_template('login.html')

@app.route('/familyReg', methods=['POST','GET'])
def familyReg():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		requests.post(base_url+'/family', data=userInput)
	return redirect(url_for('home'))

@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		response = requests.post(base_url+'/login', data=userInput)
		loginID = response.json()
		if userInput['cat'] == 'family':
			if loginID != '':
				session['family'] = loginID
		elif userInput['cat'] == 'member':
			if loginID != '':
				session['member'] = loginID
		return redirect(url_for('home'))

@app.route('/logout')
def logout():
	if 'family' in session:
		session.pop('family', None)
	elif 'member' in session:
		session.pop('member', None)
	return redirect(url_for('home'))

@app.route('/familyProfile')
def familyProfile():
	if 'family' in session:
		familyID = session['family']
		response = requests.get(base_url+'/family/' + familyID)
		familyDetails = response.json()
		return render_template('family_profile.html', familyDetails=familyDetails)
	else:
		return redirect(url_for('home'))

@app.route('/addMember', methods=['GET','POST'])
def addMember():
	if 'family' in session:
		if request.method=='POST':
			userInput=request.form.to_dict()
			userInput['familyID'] = session['family']
			userImg = request.files['photo']
			files = {'photo' : (userImg.filename, userImg, userImg.content_type)}
			response = requests.post(base_url + '/member', data=userInput, files=files)
	return redirect(url_for('home'))

@app.route('/familyMemberProfile/<memberID>')
def familyMemberProfile(memberID):
	if 'family' in session:
		familyID = session['family']
		response = requests.get(base_url+'/family/' + familyID)
		familyDetails = response.json()
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		return render_template('family_member_profile.html', familyDetails=familyDetails, memberDetails=memberDetails)
	else:
		return redirect(url_for('home'))

@app.route('/memberProfile')
def memberProfile():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		return render_template('member_profile.html', memberDetails=memberDetails)
	else:
		return redirect(url_for('home'))

@app.route('/indFixedExpense')
def indFixedExpense():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/memberExpense/' + memberID + '/fixed')
		indFixedExpense = response.json()
		return render_template('ind_fixed_expense.html', memberDetails=memberDetails, indFixedExpense=indFixedExpense)
	else:
		return redirect(url_for('home'))

@app.route('/indFixedExpenseReg', methods=['POST','GET'])
def indFixedExpenseReg():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['memberID'] = session['member']
			requests.post(base_url+'/indFixedExpense', data=userInput)
			return redirect(url_for('indFixedExpense'))
	else:
		return redirect(url_for('home'))

@app.route('/indSpecialExpense')
def indSpecialExpense():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/memberExpense/' + memberID + '/special')
		indSpecialExpense = response.json()
		x = datetime.now(timezone("Asia/Kolkata"))
		currentDate = x.strftime('%d/%m/%Y')
		return render_template('ind_special_expense.html', memberDetails=memberDetails, indSpecialExpense=indSpecialExpense, currentDate=currentDate)
	else:
		return redirect(url_for('home'))

@app.route('/indSpecialExpenseReg', methods=['POST','GET'])
def indSpecialExpenseReg():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['memberID'] = session['member']
			requests.post(base_url+'/indSpecialExpense', data=userInput)
			return redirect(url_for('indSpecialExpense'))
	else:
		return redirect(url_for('home'))

@app.route('/indOtherExpense')
def indOtherExpense():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/memberExpense/' + memberID + '/others')
		indOtherExpense = response.json()
		return render_template('ind_other_expense.html', memberDetails=memberDetails, indOtherExpense=indOtherExpense)
	else:
		return redirect(url_for('home'))

@app.route('/memberFamilyInfo')
def memberFamilyInfo():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/memberList/' + memberDetails['familyID'])
		memberList = response.json()
		response = requests.get(base_url+'/family/' + memberDetails['familyID'])
		familyDetails = response.json()
		response = requests.get(base_url+'/familyExpense/' + memberDetails['familyID'] + '/all')
		famExpense = response.json()
		return render_template('member_family_info.html', memberDetails=memberDetails, memberList=memberList, familyDetails=familyDetails, famExpense=famExpense)
	else:
		return redirect(url_for('home'))

@app.route('/familyMemberDetails/<memberID>')
def familyMemberDetails(memberID):
	if 'member' in session:
		response = requests.get(base_url+'/member/' + memberID)
		familyMemberDetails = response.json()
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		return render_template('family_member_details.html', memberDetails=memberDetails, familyMemberDetails=familyMemberDetails)
	else:
		return redirect(url_for('home'))

@app.route('/famFixedExpense')
def famFixedExpense():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/familyExpense/' + memberDetails['familyID'] + '/fixed')
		famFixedExpense = response.json()
		return render_template('fam_fixed_expense.html', memberDetails=memberDetails, famFixedExpense=famFixedExpense)
	else:
		return redirect(url_for('home'))

@app.route('/famFixedExpenseReg', methods=['POST','GET'])
def famFixedExpenseReg():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['memberID'] = session['member']
			requests.post(base_url+'/famFixedExpense', data=userInput)
			return redirect(url_for('famFixedExpense'))
	else:
		return redirect(url_for('home'))

@app.route('/famSpecialExpense')
def famSpecialExpense():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/familyExpense/' + memberDetails['familyID'] + '/special')
		famSpecialExpense = response.json()
		return render_template('fam_special_expense.html', memberDetails=memberDetails, famSpecialExpense=famSpecialExpense)
	else:
		return redirect(url_for('home'))

@app.route('/famSpecialExpenseReg', methods=['POST','GET'])
def famSpecialExpenseReg():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['memberID'] = session['member']
			requests.post(base_url+'/famSpecialExpense', data=userInput)
			return redirect(url_for('famSpecialExpense'))
	else:
		return redirect(url_for('home'))

@app.route('/famOtherExpense')
def famOtherExpense():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/familyExpense/' + memberDetails['familyID'] + '/others')
		famOtherExpense = response.json()
		return render_template('fam_other_expense.html', memberDetails=memberDetails, famOtherExpense=famOtherExpense)
	else:
		return redirect(url_for('home'))

@app.route('/memberAccounts')
def memberAccounts():
	if 'member' in session:
		memberID = session['member']
		response = requests.get(base_url+'/member/' + memberID)
		memberDetails = response.json()
		response = requests.get(base_url+'/memberList/' + memberDetails['familyID'])
		memberList = response.json()
		response = requests.get(base_url+'/transaction/' + memberID)
		transactionList = response.json()
		x = datetime.now(timezone("Asia/Kolkata"))
		currentDate = x.strftime('%d/%m/%Y')
		currentTime = x.strftime('%X')
		return render_template('member_accounts.html', memberID=memberID, memberDetails=memberDetails, memberList=memberList, transactionList=transactionList, currentDate=currentDate)
	else:
		return redirect(url_for('home'))

@app.route('/incomeTransaction', methods=['POST','GET'])
def incomeTransaction():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			memberID = session['member']
			requests.post(base_url+'/transaction/' + memberID, data=userInput)
			return redirect(url_for('memberAccounts'))
	else:
		return redirect(url_for('home'))

@app.route('/addIndOtherExpense', methods=['POST','GET'])
def addIndOtherExpense():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			memberID = session['member']
			requests.post(base_url+'/transaction/' + memberID, data=userInput)
			return redirect(url_for('indOtherExpense'))
	else:
		return redirect(url_for('home'))

@app.route('/addFamOtherExpense', methods=['POST','GET'])
def addFamOtherExpense():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			memberID = session['member']
			requests.post(base_url+'/transaction/' + memberID, data=userInput)
			return redirect(url_for('famOtherExpense'))
	else:
		return redirect(url_for('home'))

@app.route('/payIndSpecialExpense', methods=['POST','GET'])
def payIndSpecialExpense():
	if 'member' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			memberID = session['member']
			requests.post(base_url+'/transaction/' + memberID, data=userInput)
			return redirect(url_for('indSpecialExpense'))
	else:
		return redirect(url_for('home'))

if __name__=='__main__':
	app.run(debug=True, host='0.0.0.0')