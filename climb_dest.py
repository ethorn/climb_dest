from app import create_app, db
from app.models import User, Destination, Routes, Cost, Accomodation, AdditionalPhotos

# The code in __init__.py is run whenever you import anything from the package. That includes importing other modules in that package.
# Like all modules, the code is run just once, and entered into sys.modules under the package name.

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'AdditionalPhotos': AdditionalPhotos, 'Destination': Destination,
            'Routes': Routes, 'Cost': Cost, 'Accomodation': Accomodation}
