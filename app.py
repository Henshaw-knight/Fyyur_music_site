#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os
from flask_migrate import Migrate
import datetime
from models import db, app, migrate, Venue, Artist, Show


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

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

time = datetime.datetime.now() 
current_time = time.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    try:
        data = []
        all_venues = Venue.query.all()
        distinct_venues = Venue.query.distinct(Venue.city,Venue.state).all()
        time = datetime.datetime.now() 
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        for each_venue in distinct_venues:
            detail = {}     
            detail['city'] = each_venue.city
            detail['state'] = each_venue.state

            venueList = []
            venue_info = Venue.query.filter_by(city=each_venue.city, state=each_venue.state).all()
            for info in venue_info:
                region = {}
                region['id'] = info.id
                region['name'] = info.name            
                region['num_upcoming_shows'] = len(Show.query.filter(Show.start_time > current_time).filter(
                    Show.venue_id == info.id).all())
                venueList.append(region)
            detail['venues'] = venueList           
            data.append(detail)
    except:
        flash('An error has occured')
        return render_template('errors/500.html')      
    finally:
        return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    try:
        search_term = request.form.get('search_term')
        formatted_search_term = f'%{search_term}%'
        venues = Venue.query.filter(Venue.name.ilike(formatted_search_term)).all()
        count = len(venues)
        data = []
        response = {}
        for venue in venues:
            venue_detail = {}
            venue_detail['id'] = venue.id
            venue_detail['name'] = venue.name

            upcoming_shows = []
            for show in venue.shows:
                if show.start_time > current_time:
                    upcoming_shows.append(show)
            venue_detail['num_upcoming_shows'] = len(upcoming_shows)
            data.append(venue_detail)
        response['count'] = count
        response['data'] = data
    except:
        flash('An error occured while fetching your search term')
        return render_template('errors/500.html')
    finally:
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        time = datetime.datetime.now() 
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        data = {}
        data['id'] = venue.id
        data['name'] = venue.name
        data['genres'] = venue.genres
        data['address'] = venue.address
        data['city'] = venue.city
        data['state'] = venue.state
        data['phone'] = venue.phone
        data['website'] = venue.website
        data['facebook_link'] = venue.facebook_link
        data['image_link'] = venue.image_link
        data['seeking_talent'] = venue.seeking_talent
        data['seeking_description'] = venue.seeking_description
        
        past_shows = []
        upcoming_shows = []
        for show in venue.shows:
            if show.start_time < current_time:
                pastEvent = {}            
                pastEvent['artist_id'] = show.artist_id
                pastEvent['artist_name'] = show.artist.name
                pastEvent['artist_image_link'] = show.artist.image_link
                pastEvent['start_time'] = show.start_time
                past_shows.append(pastEvent)
            else:
                upcomingEvent = {}
                upcomingEvent['artist_id'] = show.artist_id
                upcomingEvent['artist_name'] = show.artist.name
                upcomingEvent['artist_image_link'] = show.artist.image_link
                upcomingEvent['start_time'] = show.start_time
                upcoming_shows.append(upcomingEvent)
            data['past_shows'] = past_shows    
            data['upcoming_shows'] = upcoming_shows
            data['past_shows_count'] = len(past_shows)
            data['upcoming_shows_count'] = len(upcoming_shows)

    except:
        flash('An error has occured, venue ID not found')
        return render_template('errors/404.html')
    finally:
        return render_template('pages/show_venue.html', venue=data)  

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    error = False
    if form.validate():
        try:
            new_venue = Venue(
                name=request.form.get('name'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                address=request.form.get('address'),
                phone=request.form.get('phone'),
                image_link=request.form.get('image_link'),
                genres=request.form.getlist('genres'),
                facebook_link=request.form.get('facebook_link'),
                website=request.form.get('website_link'),
                seeking_talent='seeking_talent' in request.form,
                seeking_description=request.form.get('seeking_description')              
            )
            db.session.add(new_venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            error = True
            flash('An error occured. Venue' + request.form['name'] + 'could not be listed.')
            db.session.rollback()
        finally:
            db.session.close()
        if error == True:
            abort(500)      
    return render_template('pages/home.html')
 
        
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue_name = Venue.query.get(venue_id).name  
    Venue.query.filter(Venue.id==venue_id).delete()
    db.session.commit()
    flash(f'Venue {venue_name} with ID {venue_id} was successfully deleted!') 
  except:
    flash(f'Venue {venue_name} with ID {venue_id} deletion failed')
    db.session.rollback()
    abort(500)
  finally:
    db.session.close()
  return redirect(url_for('index'))     
  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
#   return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
  
    for artist in artists:
        artist_detail = {}
        artist_detail['id'] = artist.id
        artist_detail['name'] = artist.name
        data.append(artist_detail)

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    formatted_search_term = f'%{search_term}%'
    artists = Artist.query.filter(Artist.name.ilike(formatted_search_term)).all()
    count = len(artists)
    data = []
    response = {}
    for artist in artists:
        artist_detail = {}
        artist_detail['id'] = artist.id
        artist_detail['name'] = artist.name

        upcoming_shows = []
        for show in artist.shows:
            if show.start_time > current_time:
                upcoming_shows.append(show)
        artist_detail['num_upcoming_shows'] = len(upcoming_shows)
        data.append(artist_detail)
    response['count'] = count
    response['data'] = data           

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    time = datetime.datetime.now() 
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    data = {}
    data['id'] = artist.id
    data['name'] = artist.name
    data['genres'] = artist.genres    
    data['city'] = artist.city
    data['state'] = artist.state
    data['phone'] = artist.phone
    data['website'] = artist.website
    data['facebook_link'] = artist.facebook_link
    data['image_link'] = artist.image_link
    data['seeking_venue'] = artist.seeking_venue
    data['seeking_description'] = artist.seeking_description
    
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        if show.start_time < current_time:
            pastEvent = {}            
            pastEvent['venue_id'] = show.venue_id
            pastEvent['venue_name'] = show.venue.name
            pastEvent['venue_image_link'] = show.venue.image_link
            pastEvent['start_time'] = show.start_time
            past_shows.append(pastEvent)
        else:
            upcomingEvent = {}
            upcomingEvent['venue_id'] = show.venue_id
            upcomingEvent['venue_name'] = show.venue.name
            upcomingEvent['venue_image_link'] = show.venue.image_link
            upcomingEvent['start_time'] = show.start_time
            upcoming_shows.append(upcomingEvent)
        data['past_shows'] = past_shows    
        data['upcoming_shows'] = upcoming_shows
        data['past_shows_count'] = len(past_shows)
        data['upcoming_shows_count'] = len(upcoming_shows) 

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)  
  form = ArtistForm(obj=artist, website_link=artist.website)   

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    if form.validate():
        edited_artist = Artist.query.get(artist_id)
        edited_artist.name = request.form['name']
        edited_artist.city = request.form['city']
        edited_artist.state = request.form['state']        
        edited_artist.phone = request.form['phone']
        edited_artist.image_link = request.form['image_link']
        edited_artist.genres = request.form.getlist('genres')
        edited_artist.facebook_link = request.form['facebook_link']
        edited_artist.website = request.form['website_link']
        edited_artist.seeking_talent = 'seeking_talent' in request.form
        edited_artist.seeking_description = request.form['seeking_description']                      
    
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)  
  form = VenueForm(obj=venue, website_link=venue.website)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes    
    form = VenueForm(request.form)
    if form.validate():
        edited_venue = Venue.query.get(venue_id)
        edited_venue.name = request.form['name']
        edited_venue.city = request.form['city']
        edited_venue.state = request.form['state']
        edited_venue.address = request.form['address']
        edited_venue.phone = request.form['phone']
        edited_venue.image_link = request.form['image_link']
        edited_venue.genres = request.form.getlist('genres')
        edited_venue.facebook_link = request.form['facebook_link']
        edited_venue.website = request.form['website_link']
        edited_venue.seeking_talent = 'seeking_talent' in request.form
        edited_venue.seeking_description = request.form['seeking_description']                      
    
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    error = False
    if form.validate():
        try:

            new_artist = Artist(
                name=request.form.get('name'),
                city=request.form.get('city'),
                state=request.form.get('state'),            
                phone=request.form.get('phone'),            
                genres=request.form.getlist('genres'),
                image_link=request.form.get('image_link'),
                facebook_link=request.form.get('facebook_link'),
                website=request.form.get('website_link'),
                seeking_venue='seeking_venue' in request.form,
                seeking_description=request.form.get('seeking_description')
            )
            db.session.add(new_artist)
            db.session.commit()
             # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            error = True
            flash('An error occured. Artist' + request.form['name'] + 'could not be listed.') 
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            abort(500)
    return render_template('pages/home.html')             
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
 
  try:
    artist_name = Artist.query.get(artist_id).name  
    Artist.query.filter(Artist.id==artist_id).delete()
    db.session.commit()
    flash(f'Venue {artist_name} with ID {artist_id} was successfully deleted!') 
  except:
    flash(f'Venue {artist_name} with ID {artist_id} deletion failed')
    db.session.rollback()
    abort(500)
  finally:
    db.session.close()
  return redirect(url_for('index'))      


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []    
    shows = Show.query.join(Venue).filter(Show.venue_id==Venue.id).join(Artist).filter(Show.artist_id==Artist.id).all()
    for show in shows:
        detail = {}
        detail['venue_id'] = show.venue_id
        detail['venue_name'] = Venue.query.get(show.venue_id).name
        detail['artist_id'] = show.artist_id
        detail['artist_name'] = Artist.query.get(show.artist_id).name
        detail['artist_image_link'] = Artist.query.get(show.artist_id).image_link
        detail['start_time'] = show.start_time

        data.append(detail)
  # displays list of shows at /shows
  # TODO: replace with real venues data.
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    error = False
    try:
        new_show = Show(
            artist_id = request.form.get('artist_id'),
            venue_id = request.form.get('venue_id'),
            start_time = request.form.get('start_time')
            )
        db.session.add(new_show)
        db.session.commit()    
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        error = True
        flash('An error occured. Show could not be listed.')
        db.session.rollback()    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')

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

# if __name__ == '__main__':
#     # app.debug = True
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)

