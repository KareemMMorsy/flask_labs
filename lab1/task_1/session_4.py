from flask import Flask, render_template, redirect, url_for


app = Flask(__name__)
students = [{"id":1, "name":"Ahmed"}, {"id":2, "name":"Mohamed"}, {"id":3, "name":"Youssef"}]

@app.route("/")
def home_page():
    # global students # for modification

    # return {"id": 1, "name":"Ahmed"}
    # return "<h1>Home Page</h1>"
    return render_template("index.html", students_data=students)
@app.route("/search/<int:id>")
def search(id):
    for student in students:
        if student["id"] == id:
            found=True
            return render_template("search.html", student=student , found=found)
        else:
            print('noooooooooooooooooooooooooooooooooooooooo')



if __name__ == "__main__":
    # print(app.url_map)
    app.run(debug=True, port=5000)