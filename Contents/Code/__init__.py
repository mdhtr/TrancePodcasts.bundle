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
    #Template:          AddAudioMenuItem(oc, '', '')

    AddAudioMenuItem(oc, 'Aly & Fila - Future Sound Of Egypt', 'http://www.fsoe-recordings.com/fsoepodcast/fsoepod.xml')
    AddAudioMenuItem(oc, 'International Departures Podcast with Myon & Shane 54', 'http://www.myonandshane54.com/id/idpodcast.xml')
    AddAudioMenuItem(oc, 'A State of Trance Official Podcast', 'http://podcast.armadamusic.com/asot/podcast.xml')
    AddAudioMenuItem(oc, 'Global DJ Broadcast', 'http://feeds.feedburner.com/MarkusSchulzGlobalDJBroadcast?format=xml')
    AddAudioMenuItem(oc, "Paul van Dyk's VONYC Sessions Podcast", 'http://podcast.paulvandyk.com/feed.xml')
    AddAudioMenuItem(oc, 'Perfecto Podcast: featuring Paul Oakenfold', 'http://oakenfold.libsyn.com/rss')
    AddAudioMenuItem(oc, "Andy Moor's Moor Music Podcast", 'http://www.andymoor.com/moormusic.rss')
    return oc

def AddAudioMenuItem(oc, titleString, rssfeedString):
    oc.add(DirectoryObject(key = Callback(GenerateAudioMenu, title = titleString, rssfeed = rssfeedString), title = titleString))
    return oc

def GenerateAudioMenu(title, rssfeed):
    oc = ObjectContainer(title1=title)
    feed = RSS.FeedFromURL(rssfeed)
    AddItemsToContainer(oc, feed) #TODO could do a pagination, a feed can hold too many items to load quickly.
    return oc

def AddItemsToContainer(oc, feed):
    for item in feed.entries:
        url = item.enclosures[0]['url']
        #url = item.enclosures[0].href
        title = item.title
        summary = item.summary
        originally_available_at = Datetime.ParseDate(item.updated)
        duration = Datetime.MillisecondsFromString(item.itunes_duration)
        oc.add(CreateTrackObject(url=url, title=title, summary=summary, originally_available_at=originally_available_at, duration=duration))
    return oc

def CreateTrackObject(url, title, summary, originally_available_at, duration, include_container=False):

    if url.endswith('.mp3'):
        container = 'mp3'
        audio_codec = AudioCodec.MP3
    else:
        container = Container.MP4
        audio_codec = AudioCodec.AAC

    track_object = TrackObject(
        key = Callback(CreateTrackObject, url=url, title=title, summary=summary, originally_available_at=originally_available_at, duration=duration, include_container=True),
        rating_key = url,
        title = title,
        summary = summary,
        originally_available_at = originally_available_at,
        duration = duration,
        items = [
            MediaObject(
                parts = [
                    PartObject(key=url)
                ],
                container = container,
                audio_codec = audio_codec,
                audio_channels = 2
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object