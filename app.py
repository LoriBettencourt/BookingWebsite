#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
# from sqlalchemy.dialects import postgresql

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

from models import db, Venue, Artist, Show
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# # TODO: connect to a local postgresql database
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime




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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []

    venues = Venue.query.order_by(Venue.name).all()
    city_state = Venue.query.distinct(Venue.city, Venue.state).order_by(Venue.state, Venue.city).all()

    for place in city_state:
        venue_list = []
        for venue in venues:
            if venue.city == place.city and venue.state == place.state:
                show_count = len(
                    [num_shows for num_shows in venue.shows if num_shows.show_date_time > datetime.now()])
                venue_list.append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': show_count
                })
        data.append({
            'city': place.city,
            'state': place.state,
            'venues': venue_list
        })

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    search_on = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%') |
        Venue.city.ilike(f'%{search_term}%') |
        Venue.state.ilike(f'%{search_term}%')).all()
    response = {
        'count': len(search_on),
        'data': []
    }

    for search in search_on:
        venue = {}
        venue['id'] = search.id
        venue['name'] = search.name
        venue['num_upcoming_shows'] = len(
            [num_shows for num_shows in search.shows if num_shows.show_date_time > datetime.now()])
        response['data'].append(venue)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    data = {}
    venue_data = Venue.query.get(venue_id)

    data['id'] = venue_data.id
    data['name'] = venue_data.name
    data['genres'] = venue_data.genres
    data['address'] = venue_data.address
    data['city'] = venue_data.city
    data['state'] = venue_data.state
    data['phone'] = venue_data.phone
    data['website'] = venue_data.website_link
    data['facebook_link'] = venue_data.facebook_link
    data['seeking_talent'] = venue_data.looking_for_talent
    data['seeking_description'] = venue_data.description
    data['image_link'] = venue_data.image_link

    artist_data = venue_data.shows

    past_show_list = []
    future_show_list = []
    for ind_artist in artist_data:
        show_time = ind_artist.show_date_time
        artist_info = {
            'artist_id': ind_artist.artist.id,
            'artist_name': ind_artist.artist.name,
            'artist_image_link': ind_artist.artist.image_link,
            'start_time': str(show_time)
        }
        if show_time < datetime.now():
            past_show_list.append(artist_info)
        else:
            future_show_list.append(artist_info)

    data['past_shows'] = past_show_list
    data['past_shows_count'] = len(past_show_list)

    data['upcoming_shows'] = future_show_list
    data['upcoming_shows_count'] = len(future_show_list)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    form = VenueForm(request.form)

    if form.validate():  
        try:
            venue = Venue(
                # left side of equation is name from the class
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                looking_for_talent=form.seeking_talent.data,
                description=form.seeking_description.data
            )
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')

        # TODO: on unsuccessful db insert, flash an error instead.
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' +
                request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        finally:
            db.session.close()
        
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')

    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + str(venue_id) + ' was successfully deleted!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              str(venue_id) + ' could not be deleted.')
    finally:
        db.session.close()
    if error:
        return render_template('pages/venues.html')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.with_entities(
        Artist.id, Artist.name).order_by(Artist.name).all()

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    search_on = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        'count': len(search_on),
        'data': []
    }

    for search in search_on:
        artist = {}
        artist['id'] = search.id
        artist['name'] = search.name
        artist['num_upcoming_shows'] = len(
            [num_shows for num_shows in search.shows if num_shows.show_date_time > datetime.now()])
        response['data'].append(artist)

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    data = {}
    artist_data = Artist.query.get(artist_id)
  
    data['id'] = artist_data.id
    data['name'] = artist_data.name
    data['genres'] = artist_data.genres
    data['city'] = artist_data.city
    data['state'] = artist_data.state
    data['phone'] = artist_data.phone
    data['website'] = artist_data.website_link
    data['facebook_link'] = artist_data.facebook_link
    data['seeking_venue'] = artist_data.seeking_venue
    data['seeking_description'] = artist_data.seeking_description
    data['image_link'] = artist_data.image_link

    venue_data = artist_data.shows

    past_show_list = []
    future_show_list = []

    for ind_venue in venue_data:
        show_time = ind_venue.show_date_time
        venue_info = {
            'venue_id': ind_venue.venue.id,
            'venue_name': ind_venue.venue.name,
            'venue_image_link': ind_venue.venue.image_link,
            'start_time': str(show_time)
        }
        if show_time < datetime.now():
            past_show_list.append(venue_info)
        else:
            future_show_list.append(venue_info)

    data['past_shows'] = past_show_list
    data['past_shows_count'] = len(past_show_list)

    data['upcoming_shows'] = future_show_list
    data['upcoming_shows_count'] = len(future_show_list)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error  = False
    form = ArtistForm(request.form)
    try:
        artist = Artist.query.get(artist_id)
        artist.name=form.name.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.image_link=form.image_link.data
        artist.genres=form.genres.data
        artist.website_link=form.website_link.data
        artist.facebook_link=form.facebook_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc.info())
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # TODO: populate form with values from venue with ID <venue_id>

    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.looking_for_talent
    form.seeking_description.data = venue.description
    form.image_link.data = venue.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    error = False
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.website_link = form.website_link.data
        venue.looking_for_talent = form.seeking_talent.data
        venue.description = form.seeking_description.data
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    form = ArtistForm(request.form)

    if form.validate():
        try:
            artist = Artist(
                # left side of equation is name from the class
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                website_link=form.website_link.data,
                facebook_link=form.facebook_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(artist)
            db.session.commit()

            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' +
                request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')

    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = []
    show_data = Show.query.all()
    for show in show_data:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.show_date_time)
        })

    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    form = ShowForm(request.form)

    try:
        show = Show(
            # left side of equation is name from the class
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            show_date_time=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
