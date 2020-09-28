# Contributing

*First off, thank you for your interest in contributing to the project! This guide will show you how to make your first code contribution*

## (Optional) Step 0: Join Discord Server

We have a [discord server](https://discord.gg/V3zPQn8) for team meetings and general project discussion.

## Step 1: Set up your Environment

You will need Git, Pipenv and [FFmpeg](https://ffmpeg.org/download.html) installed on your system.

First [fork the repository](https://github.com/ved-editor/ved/fork). Then, clone your fork and enter it:
```
git clone https://github.com/YOUR_NAME/ved.git
cd ved
```

Next, install the dependencies:
```
pipenv install --dev
```

## Step 2: Pick an Issue

Pick a [feature or bugfix](https://github.com/ved-editor/ved/issues) to implement. Then, checkout a new topic branch for your work:
```
git checkout -b my_feature
```

## Step 3: Make Changes

To execute the tests run
```
pipenv run test
```

As you develop, you can test and lint your code with
```
pipenv run test
pipenv run lint
```

## Step 4: Submit Your Changes

Update your feature branch with `upstream/master` and push:
```
git fetch upstream
git rebase upstream/master
git push origin my_feature
```

And open a pull request

## Styleguides

### Git Commit Messages

Try to adhere to the following rules:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Save movie" not "Saves movie")
- Try to limit the first line to 72 characters or less

### Python Styleguide

Run `pipenv run lint` to lint. See [PEP8](https://www.python.org/dev/peps/pep-0008/#introduction) for additional information.
