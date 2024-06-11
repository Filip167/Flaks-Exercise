# app.py
"""Flask app for Cupcakes"""

from flask import Flask, jsonify, request
from models import db, connect_db, Cupcake

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)

@app.route('/api/cupcakes', methods=['GET'])
def list_cupcakes():
    """Get data about all cupcakes."""
    cupcakes = Cupcake.query.all()
    serialized = [serialize_cupcake(c) for c in cupcakes]
    return jsonify(cupcakes=serialized)

@app.route('/api/cupcakes/<int:cupcake_id>', methods=['GET'])
def get_cupcake(cupcake_id):
    """Get data about a single cupcake."""
    cupcake = Cupcake.query.get_or_404(cupcake_id)
    return jsonify(cupcake=serialize_cupcake(cupcake))

@app.route('/api/cupcakes', methods=['POST'])
def create_cupcake():
    """Create a new cupcake."""
    data = request.json
    new_cupcake = Cupcake(
        flavor=data['flavor'],
        size=data['size'],
        rating=data['rating'],
        image=data.get('image', "https://tinyurl.com/demo-cupcake")
    )
    db.session.add(new_cupcake)
    db.session.commit()
    return jsonify(cupcake=serialize_cupcake(new_cupcake)), 201

def serialize_cupcake(cupcake):
    """Serialize a cupcake SQLAlchemy obj to dictionary."""
    return {
        "id": cupcake.id,
        "flavor": cupcake.flavor,
        "size": cupcake.size,
        "rating": cupcake.rating,
        "image": cupcake.image
    }
#################################################

@app.route('/api/cupcakes/<int:cupcake_id>', methods=['PATCH'])
def update_cupcake(cupcake_id):
    """Update a cupcake."""
    cupcake = Cupcake.query.get_or_404(cupcake_id)
    data = request.json

    cupcake.flavor = data.get('flavor', cupcake.flavor)
    cupcake.size = data.get('size', cupcake.size)
    cupcake.rating = data.get('rating', cupcake.rating)
    cupcake.image = data.get('image', cupcake.image)

    db.session.commit()
    return jsonify(cupcake=serialize_cupcake(cupcake))

@app.route('/api/cupcakes/<int:cupcake_id>', methods=['DELETE'])
def delete_cupcake(cupcake_id):
    """Delete a cupcake."""
    cupcake = Cupcake.query.get_or_404(cupcake_id)
    db.session.delete(cupcake)
    db.session.commit()
    return jsonify(message="Deleted")


######################

# URLs to test
# http://127.0.0.1:5000/api/cupcakes
# http://127.0.0.1:5000/api/cupcakes/1
# http://127.0.0.1:5000/api/cupcakes


