from flask import Flask, render_template, redirect, url_for, request
import email_system 

app = Flask(__name__)

@app.route('/')
def index():
    # Render index.html
    return render_template('index.html')


@app.route('/authenticate')
def authenticate():
    # Call authenticate() after rendering index.html
    auth_result = email_system.authenticate()
    if auth_result:
        email, password, server = auth_result
        # Render 'authenticated.html' and pass authentication info
        return render_template('authenticated.html', email=email, password=password, server=server)
    else:
        # If authentication fails, redirect to the index route
        return redirect(url_for('index'))

@app.route('/menu')
def menu():
    # Print request args for debugging
    print(request.args)
    
    # Get parameters from request.args
    email = request.args.get('email')
    password = request.args.get('password')
    server = request.args.get('server')
    
    # Call main() function from email_system module
    email_system.main(email, password, server)
    # return "Main function executed successfully!" 
    return redirect(url_for('index'))   


if __name__ == "__main__":
    app.run(debug=True)
