from app import app, db
from app.models import User, Destination, Routes, Cost, Accomodation, AdditionalPhotos


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'AdditionalPhotos': AdditionalPhotos, 'Destination': Destination, 'Routes': Routes, 'Cost': Cost, 'Accomodation': Accomodation}