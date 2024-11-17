from app import app

"""
Pages
"""
@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # CA server running on port 5001
