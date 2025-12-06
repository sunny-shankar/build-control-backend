from fabric import task


@task
def dev(c):
    c.run("uv run fastapi dev")


@task
def start(c):
    c.run("uv run fastapi run")


@task
def commit(c):
    c.run("uv run cz commit")
