class TestABCViews:
    def setup_method(self, method):
        """ fonction appelée lors du lancement d'un test unitaire faisant partie d'une classe """

    def test_signup_view(self):
        assert 1 == 1

    def test_testTwoName (self):
        assert 2 == 2

    def teardown_method(self, method):
        """ fonction appelée à la fin d'un test unitaire faisant partie d'une classe """
