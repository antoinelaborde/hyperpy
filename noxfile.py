import nox

locations = "."


@nox.session(python=["3.8"])
def tests(session):
    #session.run("pip3", "install", ".[test]")
    #session.run("pytest")
    pass


@nox.session(python=["3.8"])
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)
