# Codenames
The board game, Codenames, but online!

## Dev setup
Clone this repo.

Install `virtualenv` with `pip install virtualenv`.

Go to your parent directory and run `virtualenv Codenames`

Now every time you want to work on the project, go to your project directory and run `source bin/activate`.

Install all the requirements with `pip install -r requirements.txt`.

Make sure to freeze any extra requirements you add in `requirements.txt`.


## Execution
Run `python app.py` to start the Flask server on port 5000.

Visit `http://localhost:5000` to view route listings

### Todos
- [ ] Finish basic game classes and logic
- [ ] Create Flask API boilerplate for serving game and updating game state
- [ ] Create frontend for game
- [ ] Add sockets so multiple players can connect to same URL and see updates to game state
- [ ] Add home page with game creation and joining
