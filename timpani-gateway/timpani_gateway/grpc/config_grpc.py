
def spec_dir(tmpdir_factory):
    master = os.path.join( os.path.dirname(__file__), "spec")
    temp = tmpdir_factory.mktemp("spec")
