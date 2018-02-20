import gunicorn.app.base
from gunicorn.six import iteritems
from api import create

class LaDaBackend(gunicorn.app.base.BaseApplication):
    """Create Standalone Application LaDaBackend."""

    def __init__(self, app, options=None):
        """The init."""
        self.options = options or {}
        self.application = app
        super(LaDaBackend, self).__init__()

    def load_config(self):
        """Load configuration."""
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """Load application."""
        return self.application

def main():
    """Main function."""

    options = {
        'bind': 'localhost:4001',
        'workers': 1,
        'daemon': 'False',
        'errorlog': 'server.log',
        'timeout': 540
    }
    LaDaBackend(create(), options).run()


if __name__ == '__main__':
    main()
