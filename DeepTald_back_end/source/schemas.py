logorrea_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['interruptions_weight', 'response_length_weight']
                },
                'valuesrules': {'type': 'float', 'min': 0, 'max': 1 },
                'required': True,
                'check_with': lambda field, value, error: sum(value.values()) == 1 or error(field, 'Weights must sum to 1')
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['min_value_avg_response_length', 'max_value_avg_response_length']
                },
                'valuesrules': {'type': 'integer', 'min': 0 },
                'required': True,
                'check_with': lambda field, value, error: value['min_value_avg_response_length'] < value['max_value_avg_response_length'] 
                or error(field, 'Threshold min_value_avg_response_length must be less than max_value_avg_response_length')
            }
        }

slowed_thinking_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['pause_time_weight', 'response_time_weight']
                },
                'valuesrules': {'type': 'float', 'min': 0, 'max': 1},
                'required': True,
                'check_with': lambda field, value, error: sum(value.values()) == 1 or error(field, 'Weights must sum to 1')
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['min_value_response_time', 'max_value_response_time']
                },
                'valuesrules': {'type': 'float', 'min': 0},
                'required': True,
                'check_with': lambda field, value, error: value['min_value_response_time'] < value['max_value_response_time'] 
                or error(field, 'Threshold min_value_response_time must be less than max_value_response_time')
            }
        }

perseverance_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                },
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['cutoff']
                },
                'valuesrules': {'type': 'integer', 'min': 0},
                'required': True
            }
        }

pressure_to_speech_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                }
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['min_num_per_min', 'max_num_per_min']
                },
                'valuesrules': {'type': 'integer', 'min': 0},
                'required': True,
                'check_with': lambda field, value, error: value['min_num_per_min'] < value['max_num_per_min'] 
                or error(field, 'Threshold min_num_per_min must be less than max_num_per_min')
            }
        }

loss_of_thought_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                }
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['threshold_next_token']
                },
                'valuesrules': {'min': 0, 'max': 1.0},
                'required': True,
            }
        }

tangentiality_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                }
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['similarity_threshold']
                },
                'valuesrules': {'min': 0, 'max': 1},
                'required': True
            }
        }

rumination_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                },
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                }
            }
        }

blocking_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                },
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['pause']
                },
                'valuesrules': {'type': 'float','min': 0},
                'required': True
            }
        }

clanging_schema = {
            'weights': {
                'type': 'dict',
                'keysrules': {
                    'allowed': []
                }
            },
            'thresholds': {
                'type': 'dict',
                'keysrules': {
                    'allowed': ['low_treshold', 'high_treshold']
                },
                'valuesrules': {'type': 'float', 'min': 0},
                'required': True,
                'check_with': lambda field, value, error: value['low_treshold'] < value['high_treshold'] 
                or error(field, 'Threshold low_treshold must be less than high_treshold')
            }
        }

narrow_thinking_schema = rumination_schema
derailment_schema = tangentiality_schema