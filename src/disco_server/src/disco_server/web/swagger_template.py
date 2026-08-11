def build_swagger_template() -> dict:
    return {
        'info': {
            'title': 'PanicDisco API',
            'description': 'API for managing the disco track library.',
            'version': '0.1.0',
        },
        'definitions': {
            'TrackDetails': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'cue_point': {'type': 'integer', 'x-nullable': True},
                    'path': {'type': 'string'},
                },
                'required': ['id', 'name', 'path'],
            },
            'TrackEntity': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                },
                'required': ['id', 'name'],
            },
            'TrackUpdate': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'cue_point': {'type': 'integer'},
                    'path': {'type': 'string'},
                },
                'required': ['name', 'cue_point', 'path'],
            },
            'TrackUpload': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'cue_point': {'type': 'integer'},
                },
                'required': ['name', 'cue_point'],
            },
            'Error': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'status_code': {'type': 'integer'},
                },
                'required': ['error', 'status_code'],
            },
        },
    }
