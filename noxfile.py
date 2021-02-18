import nox

locations = "hyperpy", "tests", "noxfile.py"

@nox.session(python=["3.8"])
def tests(session):
    args = session.posargs
    session.install(".")
    session.run("pytest", *args)


@nox.session(python=["3.8"])
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)
