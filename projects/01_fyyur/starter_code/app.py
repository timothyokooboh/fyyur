#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
from datetime import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from sqlalchemy import or_, func, desc
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models import db, Venue, Show, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def get_past_shows(model, instance_id):
  past_shows = []

  if(model == 'venue'):
    shows = Show.query.filter(Show.venue_id == instance_id, Show.start_time < datetime.today()).all()

    for show in shows:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })

  elif(model == 'artist'):
    shows = Show.query.filter(Show.artist_id == instance_id, Show.start_time < datetime.today()).all()

    for show in shows:
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
      })
  return past_shows

def get_upcoming_shows(model, instance_id):
  upcoming_shows = []

  if(model == 'venue'):
    shows = Show.query.filter(Show.venue_id == instance_id, Show.start_time >= datetime.today()).all()

    for show in shows:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })

  elif(model == 'artist'):
    shows = Show.query.filter(Show.artist_id == instance_id, Show.start_time >= datetime.today()).all()
    for show in shows:
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
      })
  return upcoming_shows

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  venues = Venue.query.order_by(desc(Venue.id)).limit(10)

  def hasItem(arr, key1, key2, comparison):
    for index, item in enumerate(arr):
      if(item[key1].lower() == comparison[key1].lower() and item[key2].lower() == comparison[key2].lower()):
        return index, True
    return False

  for venue in venues:
    if (len(data) == 0 or hasItem(data, 'city', 'state', venue) == False):
      data.append({
        'city': venue.city,
        'state': venue.state,
        'venues': [
          {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(get_upcoming_shows('venue', venue.id))
          }
        ]
      })
    else:
      index, is_present = hasItem(data, 'city', 'state', venue)
      data[index]['venues'].append({'id': venue.id, 'name': venue.name})
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = { 'count': 0, 'data': [] }

  data = Venue.query.filter(
    or_(Venue.name.ilike('%' + request.form['search_term'] + '%'), 
      Venue.city.ilike('%' + request.form['search_term'] + '%'),
      Venue.state.ilike('%' + request.form['search_term'] + '%'),
      func.concat(Venue.city, ', ', Venue.state).ilike('%' + request.form['search_term'] + '%')
    )
  ).all()

  response['count'] = len(data)

  for result in data:
    response['data'].append({
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': len(get_upcoming_shows('venue', result.id))
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  genres = venue.genres[1:-1].split(',')

  data = {}
  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = genres
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website_link  
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link
  data['past_shows'] = get_past_shows('venue', venue_id)
  data['upcoming_shows'] = get_upcoming_shows('venue', venue_id)
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False

  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.', 'danger')
      return redirect(url_for('create_venue_form'))
    flash('Venue ' + request.form['name'] + ' was successfully listed!', 'info')
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('Venue could not be deleted.', 'danger')
      return { 'message': 'error' }

    flash('Venue was successfully deleted.', 'info')
    return { 'message': 'success' }
    


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name).order_by(desc(Artist.id)).limit(10)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = { 'count': 0, 'data': [] }

  data = Artist.query.filter(
    or_(
      Artist.name.ilike('%' + request.form['search_term'] + '%'),
      Artist.city.ilike('%' + request.form['search_term'] + '%'),
      Artist.state.ilike('%' + request.form['search_term'] + '%'),
      func.concat(Artist.city, ', ', Artist.state).ilike('%' + request.form['search_term'] + '%')
    )
  ).all()

  response['count'] = len(data)

  for result in data:
    response['data'].append({
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': len(get_upcoming_shows('artist', result.id))
    })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  genres = artist.genres[1:-1].split(',')
  
  data = {}
  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website_link
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist.seeking_venue
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
  data['past_shows'] = get_past_shows('artist', artist_id)
  data['upcoming_shows'] = get_upcoming_shows('artist', artist_id)
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist.genres = artist.genres[1:-1].split(',')
  
  form = ArtistForm(obj=artist)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  error = False
  try:
    form = ArtistForm(request.form)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.', 'danger')
      return redirect(url_for('edit_artist', artist_id=artist_id))
    flash('Artist ' + request.form['name'] + ' was successfully updated!', 'info')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  venue.genres = venue.genres[1:-1].split(',')
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  error = False

  try:
    form = VenueForm(request.form)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.', 'danger')
      return redirect(url_for('edit_venue', venue_id=venue_id))
    flash('Venue ' + request.form['name'] + ' was successfully updated!', 'info')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  error = False

  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    if(error):
      flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.', 'danger')
      return redirect(url_for('create_artist_form'))

    flash('Artist ' + request.form['name'] + ' was successfully listed!', 'info')
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.order_by(desc(Show.id)).all()
  
  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  error = False

  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if(error):
      flash('An error occurred. Show could not be listed.', 'danger')
      return redirect(url_for('create_shows'))
    flash('Show was successfully listed!', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
