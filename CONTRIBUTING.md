# Contributing

*First off, thank you for your interest in contributing to the project! This guide will show you how to make your first code contribution*

## Setting up your environment

You will need Git and Pipenv and FFmpeg installed on your system.

First [fork the repository](https://github.com/vidar-python/vidar-python/fork). Then, clone your fork and enter it:
```
git clone https://github.com/vidar-python/vidar-python.git
cd vidar-python
```

Next, install the dependencies:
```
pipenv install
```

Finally, activate the Pipenv shell so you can run the project:
```
pipenv shell
```

## Testing

To execute the tests run
```
pipenv run python -m pytest
```

## Making Changes

Pick a [feature or bugfix](https://github.com/vidar-python/vidar-python/issues) to implement. Then, checkout a new topic branch for your work:
```
git checkout -b my_feature
```

First write the tests, and then make the changes:

1. Write unit tests that need to pass for the feature to be complete, making sure they fail when executed.
2. Implement the changes, making sure the tests pass.
3. Refactor, [simplifying the new code](https://www.agilealliance.org/glossary/rules-of-simplicity/) as necessary.

## Linting

Before you push, make sure to lint your code:
```
pipenv run python -m pylint vidar-python
```

## Submitting Your Changes

Update your feature branch with `upstream/master` and push:
```
git fetch upstream
git rebase upstream/master
git push origin my_feature
```

And open a pull request

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Save movie" not "Saves movie")
- Try to limit the first line to 72 characters or less

### Python Styleguide

> See [PEP8](https://www.python.org/dev/peps/pep-0008/#introduction)
