from werkzeug.routing import BaseConverter

class BoolConverter(BaseConverter):
    def to_python(self, value):
        return value.lower() in ('true', '1', 'yes')

    def to_url(self, value):
        return 'true' if value else 'false'
