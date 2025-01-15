from flask import Flask,redirect,url_for,render_template,request

app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def home():
    power = 2**25

    # Declare variables
    firstfigure     = None
    secondfigure    = None
    answer          = None
    if request.method == 'POST':
        print(request.form)
        firstfigure     = request.form['firstfigure']
        secondfigure    = request.form['secondfigure']

        firstfigure     = int(firstfigure)
        secondfigure    = int(secondfigure)
        answer          = firstfigure + secondfigure
        
    return render_template('index.html', power=power, firstfigure=firstfigure, secondfigure=secondfigure, answer=answer)

@app.route('/emma')
def emma():
    return render_template('emma.html')

@app.route('/nater')
def nater():
    return render_template('nater.html')

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)