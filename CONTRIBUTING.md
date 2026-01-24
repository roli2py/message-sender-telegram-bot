# Contributing

Thank you that spending your time to contribute. It's very appreciatory, that you want to improve the project.

Before doing something, fully read the file.

In general, open an issue, if you don't know how to solve a problem and open PR instead, if you have a solution. 

Below are described concrete actions to do for each type of a problem:
1. If you see typos in docs, [`README.md`](README.md) and/or this file, open PR with changes.
2. If you think that something can be documented, open issues and, if you know how to do this, make PR.
3. If you notice or see a problem in a bot behavior, read "[Developing](#developing)" in this file, open an issue with 1) a description of a problem, 2) steps to reproduce this problem and 3) additional comments if needed. If you have a solution of this problem, then anyway make an issue to leave a description or the problem for situations when PR is not solving a problem and after make PR that refer to this issue.
4. If nothing is corresponding to your problem, follow the general rules: open an issue/make PR.

Follow the code of conduct when you're opening issues, making PR or communicating with other members of the project. See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) for more information.

## Security issues

See [`SECURITY.md`](SECURITY.md).

## Developing

The project uses a `Makefile` to type check, format and test it and `PlantUML` to create a UML class diagram. You need a tool that starts a `Makefile` and installed `PlantUML` with any method before continuing to read this chapter. When in the chapter `make` will be mentioned and your not using GNU `make`, assume your tool instead and change commands correspondingly.

The project follows the SOLID principles, so make sure that the changed code corresponds to this priciples. If you see classes that don't follow this principles, then also open issues/make PR as discussed before.

To set up the workspace, follow this steps:
1. Clone the repository:
    ```bash
    git clone https://github.com/roli2py/message-sender-telegram-bot
    ```
2. Navigate to the repository:
    ```bash
    cd message-sender-telegram-bot
    ```
3. Install the project's package in an editable mode with the `dev` deps:
    ```bash
    pip install -e .[dev]
    ```
4. Start to develop :)
5. After the develop, start `make` to format and test the project:
    ```bash
    make
    ```
6. To run the project, see "[Running](README.md#running)" in [`README.md`](README.md) from a fourth to ninth clause.

### Makefile targets

If you want, you can start the specific action by providing a corresponding target to `make`:
```bash
make test
```

Available targets:
1. `all` — Invokes all targets. Invoked by default, if `make` is started without the target.
2. `typecheck` — Type checks the project by `basedpyright`.
2. `format` — Formats the project by `isort` and `black`.
3. `test` — Starts the unittests by `pytest`.

### UML class diagram

The project provides a UML class diagram, made by [PlantUML](https://plantuml.com/). You can use it if you need.

When you're adding/changing/deleting (assuming that you're deleting unneeded unpublished) classes in the code, make corresponding changes to the UML class diagram.
