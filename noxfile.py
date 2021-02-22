import nox

locations = "."


@nox.session(python=["3.8"])
def tests(session):
    args = session.posargs
    session.install(".[test]")
    session.run("pytest", *args)


@nox.session(python=["3.8"])
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)
