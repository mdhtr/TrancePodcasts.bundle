TITLE = 'Trance Podcasts'
PREFIX = '/music/trancepodcasts'
ART = "art-default.jpg"
ICON = "icon-default.png"


def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    PopupDirectoryObject.thumb = R(ICON)
    PopupDirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)
    HTTP.CacheTime = CACHE_1HOUR


@handler(PREFIX, TITLE)
def MainMenu():
    oc = ObjectContainer()

    oc.add(build_feed_directory('http://www.fsoe-recordings.com/fsoepodcast/fsoepod.xml',
                                'Aly & Fila - Future Sound Of Egypt'))
    oc.add(build_feed_directory('http://internationaldepartures.podbean.com/feed/',
                                'International Departures Podcast with Myon & Shane 54'))
    oc.add(build_feed_directory('http://podcast.armadamusic.com/asot/podcast.xml',
                                'A State of Trance Official Podcast'))
    oc.add(build_feed_directory('http://feeds.feedburner.com/MarkusSchulzGlobalDJBroadcast?format=xml',
                                'Global DJ Broadcast'))
    oc.add(build_feed_directory('http://podcast.paulvandyk.com/feed.xml', 'Paul van Dyk\'s VONYC Sessions Podcast'))
    oc.add(build_feed_directory('http://oakenfold.libsyn.com/rss', 'Perfecto Podcast: featuring Paul Oakenfold'))
    oc.add(build_feed_directory('http://www.andymoor.com/moormusic.rss', 'Andy Moor\'s Moor Music Podcast'))
    oc.add(PrefsObject(title='Preferences'))

    return oc


def build_feed_directory(rssfeed, title):
    return DirectoryObject(
        key=Callback(AudioList,
                     title=title,
                     rssfeed=rssfeed),
        title=title)


@route(PREFIX + '/audiolist', page=int)
def AudioList(title, rssfeed, page=0, header=None, message=None):
    try:
        feed = get_feed(title, rssfeed, page)
    except RuntimeError, e:
        return MessageContainer(e.message)

    items_per_page = get_items_per_page()
    entries = feed.entries
    entries_length = len(entries)
    current_page_number = page + 1
    pages_length = get_pages_length(entries_length, items_per_page)
    page_title = get_page_title(title, current_page_number, pages_length)
    next_page = page + 1
    is_not_last_page = next_page < pages_length
    entry_sublist = get_entry_sublist(entries, items_per_page, page)
    main_thumb = feed['feed']['image']['href']

    oc = ObjectContainer(title2=page_title, header=header, message=message)
    add_entries_to_container(oc, entry_sublist, main_thumb, title)

    has_no_items_on_page = len(oc) == 0
    if has_no_items_on_page and is_not_last_page:
        return continue_to_next_page_with_warning(title, rssfeed, next_page)

    if is_not_last_page:
        oc.add(create_next_page_object(title, rssfeed, next_page))

    return oc


def get_feed(title, rssfeed, page):
    if page == 0:
        feed = RSS.FeedFromURL(rssfeed)
        # Log('parsed RSS Feed')
        # check if the url is under Maintenance
        check_text = feed['feed']['summary']
        # get RSS as feed object, using feedparser
        if 'Web Maintenance' in check_text:
            raise RuntimeError('Warning', '%s Currently under "Web Maintenance"' % rssfeed)
        else:
            # Log('saving RSS Feed object to Data')
            # save feed as python object so we can re-call feed for next page
            Data.SaveObject(title, feed)
    else:
        # if Data.Exists(title):
        # Log('loading RSS Feed object from Data')
        # load in our saved feed object for next page
        feed = Data.LoadObject(title)
    return feed


def get_items_per_page():
    if Prefs['items_per_page'] is not "All":
        items_per_page = int(Prefs['items_per_page'])
    else:
        items_per_page = "All"
    return items_per_page


def get_pages_length(entries_length, items_per_page):
    # NameError: global name 'type' is not defined for: if type(items_per_page) is int
    if items_per_page is not "All":
        return entries_length / items_per_page + (1 if entries_length % items_per_page > 0 else 0)
    else:
        return 1


def get_page_title(title, current_page_number, total_pages_length):
    page_title = '%s | Page %i of %i' % (title, current_page_number, total_pages_length)
    return page_title


def get_entry_sublist(entries, items_per_page, page):
    start_num = get_start_num(items_per_page, page)
    end_num = get_end_num(start_num, items_per_page, len(entries))
    Log('Start: %s, End: %s', start_num, end_num)
    entry_sublist = entries[start_num:end_num]
    return entry_sublist


def get_start_num(items_per_page, page):
    if items_per_page is not "All":
        return page * items_per_page
    else:
        return 0


def get_end_num(start_num, items_per_page, entries_length):
    if items_per_page is not "All":
        end_num_candidate = start_num + items_per_page
        if end_num_candidate < entries_length:
            return end_num_candidate
    return entries_length


def add_entries_to_container(oc, entry_list, main_thumb, title):
    for item in entry_list:
        item_keys = item.keys()
        url = item.enclosures[0]['url']
        title_text = item.title
        item_title = title_text.replace(title, '').lstrip(': ')

        # clean episode titles
        if title == 'Perfecto Podcast: featuring Paul Oakenfold':
            if 'Paul Oakenfold:' in item_title:
                test = Regex('(Episode\ .+)').search(item_title)
                if test:
                    item_title = test.group(1).strip()
            else:
                item_title = item_title.replace('Planet Perfecto Podcast', 'Episode').strip()
        elif title == 'Aly & Fila - Future Sound Of Egypt':
            item_title = 'Episode ' + item_title
        elif title == 'Andy Moor\'s Moor Music Podcast':
            test = Regex('(Episode\ .+)').search(item_title)
            if test:
                item_title = test.group(1).strip()
        elif title == 'Paul van Dyk\'s VONYC Sessions Podcast':
            test = Regex('(\d+)').search(item_title)
            if test:
                item_title = 'Episode ' + test.group(1).lstrip('0 ').strip()

        # find ep thumb, if not then use global thumb
        if 'image' in item_keys:
            thumb = item['image']['href']
        else:
            thumb = main_thumb

        # setup artist and genres if included
        artist = None
        genres = []
        if 'author' in item_keys:
            artist = item['author']
            if title == 'Paul van Dyk\'s VONYC Sessions Podcast':
                test = Regex('(.*)\(').search(artist)
                if test:
                    artist = test.group(1).strip()

        if 'tags' in item_keys:
            genres = [t['term'] for t in item['tags']]

        # test summary for html format
        summary_text = item.summary
        if summary_text:
            summary_node = HTML.ElementFromString(summary_text)
            summary = String.StripTags(summary_node.text_content())
        else:
            summary = None

        # leave as string, cannot propagate datetime objects between functions
        originally_available_at = item.updated
        # ep duration in milliseconds
        duration = Datetime.MillisecondsFromString(item.itunes_duration)

        item_info = {
            'title': item_title, 'artist': artist, 'summary': summary, 'thumb': thumb,
            'oaa_date': originally_available_at, 'duration': duration, 'album': title,
            'genres': genres, 'url': url
        }

        # www.moormusic.info URL is offline, they moved to moormusic.co, but not all ep are hosted
        # this will weed out the old URL host
        if 'www.moormusic.info' not in url:
            oc.add(CreateTrackObject(item_info=item_info))


def continue_to_next_page_with_warning(title, rssfeed, next_page):
    return AudioList(
        title=title, rssfeed=rssfeed, page=next_page,
        header=title,
        message='Skipping Page(s), No Valid Episode URL\'s')


def create_next_page_object(title, rssfeed, next_page):
    return NextPageObject(
        key=Callback(AudioList, title=title, rssfeed=rssfeed, page=next_page),
        title='Next Page>>')


@route(PREFIX + '/create-track-object', item_info=dict)
def CreateTrackObject(item_info, include_container=False):

    if item_info['url'].endswith('.mp3'):
        container = Container.MP3
        audio_codec = AudioCodec.MP3
    else:
        container = Container.MP4
        audio_codec = AudioCodec.AAC

    # some dates are formatted incorrectly, skip those we cannot parse
    try:
        date = Datetime.ParseDate(item_info['oaa_date'])
    except:
        date = None

    track_object = TrackObject(
        key=Callback(CreateTrackObject, item_info=item_info, include_container=True),
        rating_key=item_info['url'],
        title=item_info['title'],
        album=item_info['album'],
        artist=item_info['artist'],
        summary=item_info['summary'],
        genres=item_info['genres'],
        originally_available_at=date,
        duration=int(item_info['duration']),
        thumb=item_info['thumb'],
        art=R(ART),
        items=[
            MediaObject(
                parts=[PartObject(key=item_info['url'])],
                container=container,
                audio_codec=audio_codec,
                audio_channels=2,
                optimized_for_streaming=True if Client.Product != 'Plex Web' else False
                )
            ]
        )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object
