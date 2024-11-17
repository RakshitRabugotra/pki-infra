from app import app

"""
Pages
"""


@app.route("/health")
def health():
    return { "group": "RA", "status": "ok"}, 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # RA server running on port 5000
