# hm_api
![Pylint](https://github.com/Howard-Miller-Hekman/hm_api/workflows/Pylint/badge.svg)

Howard Miller and Heckman API



## installing via pipenv
```
pipenv install --dev
```

## Run unit tests

### Run all tests

```
pipenv run python -m unittest discover tests
```

### Run single test, example...

```
pipenv run python -m unittest tests\test_hm_notifications_api.py
```

## Example of Unittest
1. create a .py file inside test directory
2. import BaseTest class from base.py
```python
from . import base

class TestYourClassName(base.BaseTest):   
    def setUp(self) -> None:
        super().setUp()
        # do rest of the setup here
        
    def test_demo_method(self):
        pass
        
    def tearUp(self):
        super().tearDown()
        # rest of the teardown
```