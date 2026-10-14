const artistInput = document.getElementById('artistInput');
const searchBtn = document.getElementById('searchBtn');
// UI Elements to update
const resultContainer = document.getElementById('resultContainer');
const skeletonContainer = document.getElementById('skeletonContainer');


let isPlaying = false;

searchBtn.addEventListener('click', performSearch);
artistInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const query = artistInput.value.trim();
    if (!query) return;

    // Reset UI
    resultContainer.classList.add('hidden');
    // errorContainer.classList.add('hidden');
    skeletonContainer.classList.remove('hidden');

    // Stop any currently playing audio
    if (currentAudio) {
        currentAudio.pause();
        if (currentIcon) {
            currentIcon.classList.remove('fa-pause');
            currentIcon.classList.add('fa-play');
        }
    }

    try {
        // iTunes API request
        // Using 'term' for artist, 'entity=song' to get songs, 'limit=10' to get top hits
        const response = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=song&limit=10`);

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();

        if (data.resultCount === 0) {
            alert(`No songs found for "${query}". Try another artist.`);
        } else {
            displaySongsList(data.results);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        alert('Something went wrong. Please check your connection and try again.');
    } finally {
        skeletonContainer.classList.add('hidden');
    }
}

function displaySongsList(songs) {
    resultContainer.innerHTML = ''; // Clear previous results
    resultContainer.classList.remove('hidden');

    songs.forEach((song, index) => {
        const songCard = document.createElement('div');
        songCard.classList.add('card', 'glass-card', 'list-item');

        // High res art
        const highResArt = song.artworkUrl100.replace('100x100bb', '300x300bb');

        songCard.innerHTML = `
            <div class="card-body list-layout">
                <div class="artwork-wrapper list-art">
                    <img src="${highResArt}" alt="${song.trackName}" class="album-art">
                    <div class="play-overlay" onclick="togglePlay(this, '${song.previewUrl}')">
                        <i class="fa-solid fa-play play-icon"></i>
                    </div>
                </div>
                <div class="song-info list-info">
                    <div class="header-row">
                        <span class="rank">#${index + 1}</span>
                        <h2>${song.trackName}</h2>
                    </div>
                    <p class="artist-name">${song.artistName}</p>
                    <p class="album-name">${song.collectionName}</p>
                    
                    <div class="actions">
                        <a href="https://www.youtube.com/results?search_query=${encodeURIComponent(song.artistName + ' ' + song.trackName + ' official video')}" target="_blank" class="yt-btn">
                            <i class="fa-brands fa-youtube"></i> Watch Video
                        </a>
                        <a href="https://open.spotify.com/search/${encodeURIComponent(song.artistName + " " + song.trackName)}" target="_blank" class="spotify-btn"><i class="fa-brands fa-spotify"></i> Spotify</a>
                        <a href="${song.trackViewUrl}" target="_blank" class="listen-btn small-btn">
                            <i class="fa-brands fa-apple"></i> Apple Music
                        </a>
                    </div>
                </div>
            </div>
        `;
        resultContainer.appendChild(songCard);
    });
}

let currentAudio = null;
let currentIcon = null;

function togglePlay(element, url) {
    const icon = element.querySelector('.play-icon');

    if (currentAudio && currentAudio.src === url) {
        if (currentAudio.paused) {
            currentAudio.play();
            icon.classList.remove('fa-play');
            icon.classList.add('fa-pause');
        } else {
            currentAudio.pause();
            icon.classList.remove('fa-pause');
            icon.classList.add('fa-play');
        }
    } else {
        // Stop currently playing
        if (currentAudio) {
            currentAudio.pause();
            if (currentIcon) {
                currentIcon.classList.remove('fa-pause');
                currentIcon.classList.add('fa-play');
            }
        }

        // Play new
        currentAudio = new Audio(url);
        currentAudio.play();
        currentIcon = icon;
        icon.classList.remove('fa-play');
        icon.classList.add('fa-pause');

        currentAudio.addEventListener('ended', () => {
            icon.classList.remove('fa-pause');
            icon.classList.add('fa-play');
        });
    }
}
