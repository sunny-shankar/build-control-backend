from fabric import task


@task
def dev(c):
    c.run("uv run fastapi dev")


@task
def start(c):
    c.run("uv run fastapi run")


@task
def commit(c):
    c.run("uv run cz commit", pty=True)


@task
def db_revision(c, message="Auto Revision"):
    """Generate Alembic migration only"""
    c.run(f'uv run alembic revision --autogenerate -m "{message}"')


@task
def db_upgrade(c):
    """Apply all Alembic migrations to head"""

    c.run("uv run alembic upgrade head")
