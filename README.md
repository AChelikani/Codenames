# Codenames
The board game, Codenames, but online!

## Dev setup
Clone this repo and ensure you have pip3 and virtualenv installed.

```bash
$ git clone https://github.com/AChelikani/Codenames.git
$ pip3 --version
> pip 9.0.1 from /usr/lib/python3.6/site-packages (python 3.6) # (or similar)
$ virtualenv --version
> 15.1.0 # (or similar)
$ ./setup.sh
```

Now every time you want to work on the project, go to your project directory and run `source bin/activate`.

Install all the requirements with `pip install -r requirements.txt`.

Make sure to freeze any extra requirements you add in `requirements.txt`.


## Execution
Run `python app.py` to start the Flask server on port 5000.

To enable debugging and hot-reloading run `FLASK_DEBUG=1 python app.py`.

Visit `http://localhost:5000` to view route listings

### Todos
- [ ] Finish basic game classes and logic
- [ ] Create Flask API boilerplate for serving game and updating game state
- [ ] Create frontend for game
- [ ] Add sockets so multiple players can connect to same URL and see updates to game state
- [ ] Add home page with game creation and joining
