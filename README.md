# ved

> A video-editing API for automation

Ved is a video-editing framework that allows for algorithmic video-editing, whether it be automation of repetitive tasks, advanced integration with machine-learning or just writing that filter that no video editor supports.

*Note that this project isn't ready to be used yet. If you would like to contribute, please check out [CONTRIBUTING](CONTRIBUTING.md)!*

## Usage

*Load a video and export it at a different framerate*:
```py
video = VideoFile('input.mp4')

movie = Movie(video.width, video.height, [video])
movie.export('output.mp4',  framerate=24)
```

*Blur an image*:
```py
image = ImageFile('input.png')  # create an image node
blur = GaussianBlur(image, 3.0)  # create a blur node

movie = Movie(image.width, image.height, [image, blur])  # add them both to the video
movie.screenshot('output.png', time=0.0)
```

As you might have noticed, everything in Ved is either a movie or a node. A movie is built up of nodes, which can be used for anything.

*Create a custom node*:
```py
class Sine(Audio):  # extend the base audio node
    def __init__(self, frequency):
        self.frequency = frequency
    
    def __call__(self):
        # Store the audio sample in `self.sample`, a special property read by the movie
        # The Audio class exposes a `sample_rate` property
        self.sample = Math.sin(self.sample_rate / float(self.frequency))

sine = Sine(800)
movie = Movie(1, 1)
movie.nodes = [sine]  # same as passing nodes to the movie's constructor
movie.export('output.wav')
```

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md).

## License

Distributed under GNU General Public License v3. See LICENSE for more information.
