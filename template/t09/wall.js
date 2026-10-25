/* T09 wall tiles: real frames from Eva's own past videos, placed in media/wall/.
 * Make them with:  ffmpeg -i past_video.mp4 -vf "fps=1/6,scale=640:360" media/wall/w_%03d.jpg
 * then list the file names here (or generate this file: ls media/wall | node -e "...") */
window.WALL = Array.from({ length: 60 }, (_, i) => 'w_' + String(i).padStart(3, '0') + '.jpg');
